import os
import json
import logging
import hashlib
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from ..models import Topic, Persona
from .cache_service import cache_service

# 确保在初始化前加载 .env
load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY")
        self.base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1")
        self.model = os.getenv("AI_MODEL", "deepseek-chat")
        
        logger.info(f"Initializing AIService (Model: {self.model}, BaseURL: {self.base_url}, KeyFound: {bool(self.api_key)})")
        
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            logger.error("AI_API_KEY not found in environment variables.")

    def pick_best_topics(self, topics: List[Dict], persona: Persona, n: int = 6) -> List[Dict]:
        """
        通用型选题精选逻辑。
        topics: 候选列表（通常来自 Redis 缓存的 Dict 列表）
        """
        if not self.client or not topics:
            return []

        # 1. 检查缓存
        # 生成候选内容的 Hash，用于判断数据源是否变化
        content_str = "".join([str(t.get("original_id") or t.get("id")) for t in topics[:20]])
        # 加上人设的关键信息
        persona_info = f"{persona.id}-{persona.depth}-{persona.custom_prompt or ''}"
        cache_key = f"ai:picks:persona:{persona.id}:hash:{hashlib.md5((content_str + persona_info).encode()).hexdigest()}"
        
        cached_res = cache_service.get(cache_key)
        if cached_res:
            logger.info(f"AI Picks Cache Hit for persona {persona.name}")
            return cached_res

        # 2. 准备候选数据
        candidates_data = []
        for t in topics:
            candidates_data.append({
                "id": t.get("id") or t.get("original_id"),
                "title": t.get("title"),
                "source": t.get("source") or "Unknown",
                "metrics": t.get("metrics") or {},
                "summary": (t.get("summary", "")[:100] + "...") if t.get("summary") and len(t.get("summary", "")) > 100 else (t.get("summary") or "")
            })

        # 3. 构建通用 Prompt，注入 custom_prompt
        interests_str = ", ".join(persona.interests) if persona.interests else "泛内容创作"
        
        # 核心逻辑：将人设详细设定注入 System Prompt
        custom_instructions = f"\n人设核心指令（务必严格遵守）：\n{persona.custom_prompt}" if persona.custom_prompt else ""

        system_prompt = f"""你是一个顶级的智能选题顾问。你的服务对象是【{persona.name}】。
人设描述：{persona.description or "无"}
兴趣标签：{interests_str}
专业深度：{persona.depth}/10
{custom_instructions}

任务：从提供的跨平台候选列表中，根据上述人设画像，挑选出最契合、最具备爆款潜力的 {n} 个选题。
挑选原则：
1. 匹配度：必须符合该人设的特定风格（如：犀利、硬核、温情等）。
2. 差异化：尽量均衡不同来源（B站、RSS、热榜）。
3. 潜力值：参考播放量、热度等指标。

请严格返回如下 JSON 格式：
{{
    "picks": [
        {{"id": 选题ID, "reason": "针对性推荐理由，说明为什么高度符合该人设的性格和偏好"}}
    ]
}}"""

        user_prompt = f"候选列表：\n{json.dumps(candidates_data, ensure_ascii=False, indent=2)}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )

            result = json.loads(response.choices[0].message.content)
            picks = result.get("picks", [])
            
            # 组装返回数据
            valid_results = []
            for p in picks:
                if "id" in p and "reason" in p:
                    # 我们尽量保持 ID 为原始类型
                    valid_results.append({"id": p["id"], "reason": p["reason"]})
            
            # 存入缓存（12小时）
            cache_service.set(cache_key, valid_results, expire=43200)
            return valid_results

        except Exception as e:
            logger.error(f"AI Picks Error: {str(e)}")
            return []

ai_service = AIService()
