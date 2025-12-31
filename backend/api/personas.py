from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from ..database import get_session
from ..models import Persona, PersonaCreate, PersonaRead, PersonaUpdate, SourceConfig

router = APIRouter(prefix="/api/v1/personas", tags=["personas"])

@router.post("/", response_model=PersonaRead)
def create_persona(persona: PersonaCreate, session: Session = Depends(get_session)):
    db_persona = Persona.from_orm(persona)
    session.add(db_persona)
    session.commit()
    session.refresh(db_persona)
    return db_persona

@router.get("/", response_model=List[PersonaRead])
def read_personas(session: Session = Depends(get_session)):
    personas = session.exec(select(Persona)).all()
    return personas

@router.get("/{persona_id}", response_model=PersonaRead)
def read_persona(persona_id: int, session: Session = Depends(get_session)):
    persona = session.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona

@router.put("/{persona_id}", response_model=PersonaRead)
def update_persona(persona_id: int, persona: PersonaUpdate, session: Session = Depends(get_session)):
    db_persona = session.get(Persona, persona_id)
    if not db_persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    persona_data = persona.dict(exclude_unset=True)
    for key, value in persona_data.items():
        setattr(db_persona, key, value)
        
    session.add(db_persona)
    session.commit()
    session.refresh(db_persona)
    return db_persona

@router.delete("/{persona_id}")
def delete_persona(persona_id: int, session: Session = Depends(get_session)):
    persona = session.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    session.delete(persona)
    session.commit()
@router.put("/{persona_id}/sources", response_model=List[SourceConfig])
def update_persona_sources(persona_id: int, sources: List[SourceConfig], session: Session = Depends(get_session)):
    """
    Update sources for a persona. Reuses existing IDs to maintain topic associations.
    """
    persona = session.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
        
    # 1. Map existing sources by (type, unique_key)
    # unique_key depends on type: uid for bilibili, url for rss, name for hot
    existing_sources = session.exec(select(SourceConfig).where(SourceConfig.persona_id == persona_id)).all()
    
    def get_source_key(s):
        stype = s.type
        data = s.config_data or {}
        if stype == "bilibili_user": return f"bili:{data.get('uid')}"
        if stype == "rss_feed": return f"rss:{data.get('url')}"
        if stype == "hot_list": return f"hot:{s.name}"
        return f"other:{s.name}"

    existing_map = {get_source_key(s): s for s in existing_sources}
    new_ids = []
    
    # 2. Process incoming sources
    for s_in in sources:
        key = get_source_key(s_in)
        if key in existing_map:
            # Update existing
            db_s = existing_map.pop(key)
            db_s.name = s_in.name
            db_s.enabled = s_in.enabled
            db_s.views_threshold = s_in.views_threshold
            db_s.config_data = s_in.config_data
            session.add(db_s)
            new_ids.append(db_s)
        else:
            # Create new
            new_source = SourceConfig(
                persona_id=persona_id,
                type=s_in.type,
                name=s_in.name,
                config_data=s_in.config_data,
                enabled=s_in.enabled,
                views_threshold=s_in.views_threshold
            )
            session.add(new_source)
            new_ids.append(new_source)
            
    # 3. Delete remaining sources that are no longer in the list
    for s_to_del in existing_map.values():
        session.delete(s_to_del)
        
    session.commit()
    
    # Refresh all
    for s in new_ids:
        session.refresh(s)
        
    return new_ids
