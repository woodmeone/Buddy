from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from ..database import get_session
from ..models import Script, ScriptCreate, ScriptRead, ScriptUpdate, ScriptTemplate, ScriptTemplateCreate, ScriptTemplateRead, ScriptTemplateUpdate

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
    Returns existing script if one already exists for this topic and template.
    """
    topic_id = payload.get("topic_id")
    template_id = payload.get("template_id")
    
    if not topic_id:
        raise HTTPException(status_code=400, detail="topic_id is required")

    # Check for existing script
    existing = session.exec(
        select(Script).where(Script.topic_id == topic_id, Script.template_id == template_id)
    ).first()
    if existing:
        return existing

    # Get topic and template info for generation
    topic = session.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Mock Generation logic
    # In a real app, this would call an LLM with topic.title, topic.summary, etc.
    import time
    time.sleep(1) # Simulate LLM latency
    
    title = f"AI Script for: {topic.title}"
    content = f"# {topic.title}\n\n## AI Analysis Summary\n{topic.ai_summary or 'No AI summary yet.'}\n\n## Video Hook\nWelcome back! Today we are diving into..."
    
    db_script = Script(
        topic_id=topic_id,
        template_id=template_id,
        title=title,
        content=content,
        status="final"
    )
    session.add(db_script)
    session.commit()
    session.refresh(db_script)
    return db_script

@router.get("/scripts/{id}", response_model=ScriptRead)
def read_script(id: int, session: Session = Depends(get_session)):
    item = session.get(Script, id)
    if not item:
        raise HTTPException(status_code=404, detail="Script not found")
    return item
