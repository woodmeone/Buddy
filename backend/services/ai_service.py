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
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=110.0)
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

    def analyze_topic(self, topic: Topic, persona: Persona) -> Dict:
        """
        针对单个选题进行深度分析，生成标题、摘要、关键词等。
        """
        if not self.client:
            return {}

        # 1. 准备 Topic 数据
        topic_data = {
            "title": topic.title,
            "summary": topic.summary or "",
            "metrics": topic.metrics or {},
            "author": topic.author or "未知"
        }

        # 2. 构建 Prompt
        interests_str = ", ".join(persona.interests) if persona.interests else "泛内容创作"
        custom_instructions = f"\n人设核心指令（务必严格遵守）：\n{persona.custom_prompt}" if persona.custom_prompt else ""

        system_prompt = f"""你是一个顶级的智能选题分析师。你的服务对象是【{persona.name}】。
人设描述：{persona.description or "无"}
兴趣标签：{interests_str}
专业深度：{persona.depth}/10
{custom_instructions}

任务：对提供的单个选题进行深度分析和内容重塑。
要求：
1. 【标题建议】：从好奇、价值、情绪三个视角生成 3 个新标题。
2. 【AI 总结】：生成 1 段 200 字以内的深度总结。
3. 【核心关键词】：提取 5 个核心关键词。
4. 【评估】：评估上手难度（1-10）和人设匹配度（1-10）。

请严格返回如下 JSON 格式 (You must respond with valid JSON):
{{
    "titles": ["标题(视角A)", "标题(视角B)", "标题(视角C)"],
    "summary": "AI 总结内容...",
    "keywords": ["关键词1", "关键词2", ...],
    "difficulty": 5,
    "personaMatch": 9
}}"""

        user_prompt = f"选题原文信息：\n{json.dumps(topic_data, ensure_ascii=False, indent=2)}"

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
            return result

        except Exception as e:
            logger.error(f"AI Analyze Topic Error: {str(e)}")
            if 'response' in locals() and hasattr(response, 'choices'):
                logger.error(f"Raw Response: {response.choices[0].message.content}")
            return {}

    def generate_script(self, topic: Topic, template: Dict, persona: Persona, extra_prompt: str = "") -> str:
        """
        根据模板风格、人设和选题信息，生成视频脚本。
        """
        if not self.client:
            return "AI 服务未初始化"

        # 1. 准备上下文
        template_name = template.get("name", "通用模板")
        template_content = template.get("content_template", "")
        
        # 1. 准备语言模型所需的上下文环境
        interests_str = ", ".join(persona.interests) if persona.interests else "泛内容创作"
        
        system_prompt = f"""你是一个顶级的短视频剧本主创，擅长通过拆解优秀案例来为特定人设（Persona）量身定制内容。

【当前人设身份】
- 名称：{persona.name}
- 专业深度：{persona.depth}/10
- 核心标签：{interests_str}
- 人设设定：{persona.custom_prompt or "未设定"}

【创作准则】
1. **适配案例骨架**：下方的【参考案例】是你本次创作的结构模版。请学习其叙事节奏、分镜逻辑和互动钩子。
2. **灵魂人设化**：产出的台词必须完全符合上述【人设身份】的语气和专业厚度。
3. **内容素材融合**：将【选题素材】中的核心观点、数据和背景，自然地嵌入到参考案例的结构中。

【参考案例（脚本模板）】
---
{template_content}
---

【输出格式】
- 使用 Markdown 格式。
- 必须包含 [画面提示] 和 [口播台词]。
- 节奏感需与参考案例保持一致。
{f"- 额外特殊要求：{extra_prompt}" if extra_prompt else ""}"""

        user_prompt = f"""【选题素材】
- 标题：{topic.title}
- 背景分析：{topic.summary or "无"}
- AI 深度见解：{topic.ai_summary or "无"}
- 关键数据：{json.dumps(topic.metrics or {}, ensure_ascii=False)}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI Generate Script Error: {str(e)}")
            raise e

    def generate_metadata_from_script(self, topic: Topic, script_content: str, persona: Persona) -> Dict:
        """
        基于生成的脚本内容，反向推导爆款标题、简介和标签。
        """
        if not self.client:
            return {}

        system_prompt = f"""你是一个短视频运营专家。
你的任务是基于一份已经写好的【视频脚本】，为【{persona.name}】的人设撰写配套的宣发物料。

【核心任务】：
1. 标题：从以下【三个不同视角】分别生成 1 个爆款标题，总共 3 个：
   - 视角 A (好奇/痛点)：直击用户核心疑惑或现实痛点，利用反差感勾起好奇。
   - 视角 B (价值/干货)：强调视频能带来的具体获得感、成长或利益点。
   - 视角 C (情绪/态度)：通过强烈的情绪共鸣或犀利的观点吸引特定圈层。
2. 简介：生成一段 100 字左右的视频简介，吸引用户观看。
3. 标签：提取 5 个精准的 SEO 标签。

请严格返回 JSON 格式 (You must respond with valid JSON):
{{
    "titles": ["标题(视角A)", "标题(视角B)", "标题(视角C)"],
    "intro": "视频简介内容",
    "tags": ["标签1", "标签2", ...]
}}"""

        user_prompt = f"""选题原摘要：{topic.summary or "无"}
AI 深度分析：{topic.ai_summary or "无"}
最终脚本内容：
---
{script_content}
---"""

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
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"AI Generate Metadata Error: {str(e)}")
            raise e

ai_service = AIService()
