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
    Replace all source configs for a persona with the new list.
    """
    persona = session.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
        
    # 1. Delete existing sources for this persona
    # Note: efficient way is delete where persona_id = persona_id
    # but we need to keep IDs if we want stable IDs? 
    # For MVP, full replace is fine.
    existing_sources = session.exec(select(SourceConfig).where(SourceConfig.persona_id == persona_id)).all()
    for s in existing_sources:
        session.delete(s)
        
    # 2. Add new sources
    new_configs = []
    for s in sources:
        # Create new instance to ensure ID is generated or reset if passed
        # We assume frontend passes config data. ID might be temporary or existing.
        # We ignore ID from frontend for insert usually, unless we want to update.
        new_source = SourceConfig(
            persona_id=persona_id,
            type=s.type,
            name=s.name,
            config_data=s.config_data,
            enabled=s.enabled,
            views_threshold=s.views_threshold
        )
        session.add(new_source)
        new_configs.append(new_source)
        
    session.commit()
    
    # 3. Refresh to get IDs
    for s in new_configs:
        session.refresh(s)
        
    return new_configs
