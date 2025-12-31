from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import logging

from ..database import get_session
from ..models import Persona
from ..services.ai_service import ai_service

logger = logging.getLogger("BuddyApp.ai")
router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

class DiscoveryTopic(BaseModel):
    id: Optional[int] = None # DB ID if exists
    original_id: str
    title: str
    url: str
    summary: Optional[str] = None
    thumbnail: Optional[str] = None
    author: Optional[str] = None
    source: str
    metrics: Dict = {}
    published_at: Optional[datetime] = None

class AISelectionItem(BaseModel):
    topic: DiscoveryTopic
    reason: str

class AISelectionResponse(BaseModel):
    items: List[AISelectionItem]
    count: int

@router.post("/picks", response_model=AISelectionResponse)
def get_ai_picks(
    persona_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """
    通用 AI 选题精选接口 - 使用 Redis 候选池
    """
    from ..services.cache_service import cache_service

    # 1. 获取目标人设
    if persona_id:
        persona = session.get(Persona, persona_id)
    else:
        persona = session.exec(select(Persona)).first()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # 2. 获取 Redis 候选池
    cache_key = f"discovery:persona:{persona.id}"
    candidates = cache_service.get(cache_key) or []
    
    if not candidates:
        logger.warning(f"AI Picks: No candidates found in Redis for persona {persona.name}")
        return {"items": [], "count": 0}

    # 3. 调用 AI 精选 (已带结果缓存)
    logger.info(f"AI Picks Request - Persona: {persona.name}, Pool Size: {len(candidates)}")
    picks = ai_service.pick_best_topics(candidates, persona, n=6)
    
    # 4. 组装结果对象
    # 在 Redis 模式下，candidates 是 dict 列表。我们需要根据 ID 找回完整对象返回给前端。
    # 注意：这里的 topic 部分需要符合 TopicRead 模型
    candidate_map = {str(c.get("original_id") or c.get("id")): c for c in candidates}
    result_items = []
    
    for p in picks:
        tid = str(p["id"])
        if tid in candidate_map:
            result_items.append({
                "topic": candidate_map[tid],
                "reason": p["reason"]
            })

    return {"items": result_items, "count": len(result_items)}
