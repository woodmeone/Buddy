from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..database import get_session
from ..models import Persona
from ..services.crawler import crawler_service

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/feed")
def get_discovery_feed(persona_id: int, type: Optional[str] = None, session: Session = Depends(get_session)):
    """
    Returns a dynamic discovery feed based on the Persona's configuration.
    Uses MockCrawlerService to generate realistic data on-the-fly.
    """
    # 1. Get Persona and its SourceConfigs
    persona = session.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
        
    # 2. Extract configs (SQLModel relationships are lazy loaded usually, but here accessing property triggers load)
    # Ensure source_configs are loaded. 
    # Note: In async mode we'd need select options, sync mode does lazy load automatically on access if session open.
    configs = persona.source_configs
    
    # 3. Use Crawler Service to fetch (mock) data
    feed_items = crawler_service.generate_feed(configs)
    
    # 4. Filter by type if requested
    if type:
        # Map frontend 'type' query (xml, github, bilibili) to SourceConfig type or Source string
        # Frontend logic: type='xml' -> RSS? 
        pass 

    return feed_items
