from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from ..database import get_session
from ..models import Persona, SourceConfig
from ..services.crawler import crawler_service

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.post("/sync")
def manual_sync(session: Session = Depends(get_session)):
    """
    Manually trigger background synchronization.
    """
    crawler_service.sync_all_sources(session)
    return {"ok": True, "message": "Synchronization completed"}

@router.get("/feed")
def get_discovery_feed(persona_id: int, type: Optional[str] = None, session: Session = Depends(get_session)):
    """
    Returns a dynamic discovery feed based on the Persona's configuration.
    Fetches latest topics from DB for the persona's source configs.
    """
    from ..models import Topic
    # 1. Get Persona and its SourceConfigs
    persona = session.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
        
    configs = [c for c in persona.source_configs if c.enabled]
    config_ids = [c.id for c in configs]
    
    if not config_ids:
        return []

    # 2. Fetch Topics from DB
    topics = session.exec(
        select(Topic).where(Topic.source_config_id.in_(config_ids))
        .order_by(Topic.published_at.desc(), Topic.saved_at.desc())
        .limit(50)
    ).all()
    
    # 3. Transform for frontend (ensure 'source' exists)
    results = []
    for t in topics:
        # Find the config type to set source string
        config = session.get(SourceConfig, t.source_config_id)
        source_str = "Unknown"
        if config:
            if config.type == "bilibili_user": source_str = "Bilibili"
            elif config.type == "rss_feed": source_str = "RSS"
            elif config.type == "hot_list": source_str = "HotList"

        results.append({
            "id": t.id,
            "original_id": t.original_id,
            "title": t.title,
            "url": t.url,
            "summary": t.summary,
            "thumbnail": t.thumbnail,
            "metrics": t.metrics,
            "analysis_result": t.analysis_result,
            "source": source_str,
            "published_at": t.published_at.isoformat() if t.published_at else None
        })
    
    return results
