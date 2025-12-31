from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
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
def get_discovery_feed(persona_id: int, session: Session = Depends(get_session)):
    """
    Returns discovery feed from Redis cache (TopHub style).
    """
    from ..services.cache_service import cache_service
    
    cache_key = f"discovery:persona:{persona_id}"
    cached_data = cache_service.get(cache_key)
    
    if cached_data:
        return cached_data
    
    # Cache miss: if it's the first time or expired
    return []
