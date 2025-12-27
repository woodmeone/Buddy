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
@router.post("/scripts/generate")
def generate_script(payload: dict = Body(...), session: Session = Depends(get_session)):
    """
    Mock Script Generation. 
    In future: Call LLM with Topic content + Template.
    """
    topic_id = payload.get("topic_id")
    template_id = payload.get("template_id")
    
    import time
    time.sleep(1) # Simulate LLM latency
    
    return {
        "content": f"# Video Script for Topic {topic_id}\n\n**Generated based on Template {template_id}**\n\n## Hook\nHello World! This is a generated script.\n\n## Content\n...\n"
    }

@router.get("/scripts/{id}", response_model=ScriptRead)
def read_script(id: int, session: Session = Depends(get_session)):
    item = session.get(Script, id)
    if not item:
        raise HTTPException(status_code=404, detail="Script not found")
    return item
