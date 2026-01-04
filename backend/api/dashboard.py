from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select
from ..database import get_session
from ..models import Persona, SourceConfig
from ..services.crawler import crawler_service

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.post("/sync")
def manual_sync(background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """
    Manually trigger background synchronization.
    """
    if crawler_service.is_syncing:
        return {"ok": False, "message": "Synchronization already in progress"}
    
    background_tasks.add_task(crawler_service.sync_all_sources, session)
    return {"ok": True, "message": "Synchronization started in background"}

@router.get("/sync/status")
def get_sync_status():
    """
    Get the current synchronization status and progress.
    """
    progress = 0
    if crawler_service.total_count > 0:
        progress = int((crawler_service.current_count / crawler_service.total_count) * 100)
    
    return {
        "is_syncing": crawler_service.is_syncing,
        "progress": progress,
        "current_count": crawler_service.current_count,
        "total_count": crawler_service.total_count,
        "last_message": crawler_service.last_message
    }

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
