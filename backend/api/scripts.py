from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from ..database import get_session
from ..models import Script, ScriptCreate, ScriptRead, ScriptUpdate, ScriptTemplate, ScriptTemplateCreate, ScriptTemplateRead, ScriptTemplateUpdate, Topic, Persona
from ..services.ai_service import ai_service

router = APIRouter(prefix="/api/v1", tags=["scripts"]) 

# --- Script Templates ---
@router.get("/script-templates", response_model=List[ScriptTemplateRead])
def read_templates(session: Session = Depends(get_session)):
    return session.exec(select(ScriptTemplate)).all()

@router.post("/script-templates", response_model=ScriptTemplateRead)
def create_template(template: ScriptTemplateCreate, session: Session = Depends(get_session)):
    db_item = ScriptTemplate.from_orm(template)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.put("/script-templates/{id}", response_model=ScriptTemplateRead)
def update_template(id: int, template: ScriptTemplateUpdate, session: Session = Depends(get_session)):
    db_item = session.get(ScriptTemplate, id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Template not found")
    data = template.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(db_item, k, v)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/script-templates/{id}")
def delete_template(id: int, session: Session = Depends(get_session)):
    db_item = session.get(ScriptTemplate, id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Template not found")
    session.delete(db_item)
    session.commit()
    return {"ok": True}

# --- Scripts (The generated ones) ---
@router.post("/scripts/generate", response_model=ScriptRead)
def generate_script(payload: dict = Body(...), session: Session = Depends(get_session)):
    """
    Generate and persist a script for a topic.
    """
    topic_id = payload.get("topic_id")
    template_id = payload.get("template_id")
    persona_id = payload.get("persona_id")
    extra_prompt = payload.get("extra_prompt", "")
    
    if not topic_id:
        raise HTTPException(status_code=400, detail="topic_id is required")

    try:
        topic_id = int(topic_id)
        if template_id is not None:
            template_id = int(template_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="IDs must be integers")

    # 1. Get Context
    topic = session.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    template = session.get(ScriptTemplate, template_id) if template_id else None
    template_data = template.dict() if template else {}

    if persona_id:
        persona = session.get(Persona, persona_id)
    else:
        persona = session.exec(select(Persona)).first()

    if not persona:
        raise HTTPException(status_code=400, detail="Persona not found")

    # 2. Real AI Generation
    content = ai_service.generate_script(
        topic=topic,
        template=template_data,
        persona=persona,
        extra_prompt=extra_prompt
    )
    
    title = f"【脚本】{topic.title[:20]}"
    
    # Check for existing script to update or create new
    existing = session.exec(
        select(Script).where(Script.topic_id == topic_id, Script.template_id == template_id)
    ).first()
    
    if existing:
        existing.content = content
        existing.updated_at = datetime.utcnow()
        db_script = existing
    else:
        db_script = Script(
            topic_id=topic_id,
            template_id=template_id,
            title=title,
            content=content,
            status="draft"
        )
    
    session.add(db_script)
    session.commit()
    session.refresh(db_script)
    return db_script

@router.get("/scripts/topic/{topic_id}", response_model=ScriptRead)
def read_script_by_topic(topic_id: int, session: Session = Depends(get_session)):
    item = session.exec(select(Script).where(Script.topic_id == topic_id)).first()
    if not item:
        raise HTTPException(status_code=404, detail="Script not found")
    return item

@router.get("/scripts/{id}", response_model=ScriptRead)
def read_script(id: int, session: Session = Depends(get_session)):
    item = session.get(Script, id)
    if not item:
        raise HTTPException(status_code=404, detail="Script not found")
    return item
