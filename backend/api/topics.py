from datetime import datetime
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from ..database import get_session
from ..models import Topic, TopicCreate, TopicRead, TopicUpdate, Persona
from ..services.ai_service import ai_service

router = APIRouter(prefix="/api/v1/topics", tags=["topics"])

@router.post("/{topic_id}/generate-metadata", response_model=TopicRead)
def generate_topic_metadata(
    topic_id: int, 
    persona_id: Optional[int] = None,
    payload: dict = Body({}),
    session: Session = Depends(get_session)
):
    """
    Generates and persists AI titles, summary and tags for a topic.
    If script_content is provided, recommendations are based on the script.
    """
    db_topic = session.get(Topic, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    script_content = payload.get("script_content")

    # Get Persona for analysis context
    if persona_id:
        persona = session.get(Persona, persona_id)
    else:
        persona = session.exec(select(Persona)).first()
    
    if not persona:
        raise HTTPException(status_code=400, detail="No persona found for context")

    # Call AI Generation
    if script_content:
        # Base on Script
        result = ai_service.generate_metadata_from_script(db_topic, script_content, persona)
        if result:
            # Force a fresh dict to ensure change detection
            analysis = dict(db_topic.analysis_result or {})
            analysis["ai_titles"] = result.get("titles", [])
            analysis["keywords"] = result.get("tags", [])
            
            if result.get("titles"):
                db_topic.ai_title = result.get("titles")[0]
            if result.get("intro"):
                 analysis["script_intro"] = result.get("intro")
            
            db_topic.analysis_result = analysis
    else:
        # Standard Deep Dive Analysis (only if not already done)
        if db_topic.ai_title:
            return db_topic
            
        result = ai_service.analyze_topic(db_topic, persona)
        if result:
            db_topic.ai_title = result.get("titles", [""])[0] if result.get("titles") else f"【解析】{db_topic.title}"
            db_topic.ai_summary = result.get("summary")
            
            # Force a fresh dict
            analysis = dict(db_topic.analysis_result or {})
            analysis["ai_titles"] = result.get("titles", [])
            analysis["keywords"] = result.get("keywords", [])
            analysis["difficulty"] = result.get("difficulty")
            analysis["personaMatch"] = result.get("personaMatch")
            db_topic.analysis_result = analysis
    
    if not result:
        raise HTTPException(status_code=500, detail="AI analysis failed")
    
    session.add(db_topic)
    session.commit()
    session.refresh(db_topic)
    return db_topic

@router.get("/", response_model=List[TopicRead])
def read_topics(session: Session = Depends(get_session)):
    topics = session.exec(
        select(Topic).where(Topic.status == "saved").order_by(Topic.saved_at.desc())
    ).all()
    return topics

@router.post("/", response_model=TopicRead)
def create_topic(topic: TopicCreate, session: Session = Depends(get_session)):
    # Check for duplicate by original_id
    existing = session.exec(select(Topic).where(Topic.original_id == topic.original_id)).first()
    if existing:
        # If it was 'new' (from discovery feed), promote it to 'saved'
        if existing.status == "new":
            existing.status = "saved"
            existing.saved_at = datetime.utcnow()
            session.add(existing)
            session.commit()
            session.refresh(existing)
        return existing

    db_topic = Topic.from_orm(topic)
    # Ensure status is 'saved' when manually creating/adding from dashboard
    db_topic.status = "saved"
    session.add(db_topic)
    session.commit()
    session.refresh(db_topic)
    return db_topic

@router.get("/{topic_id}", response_model=TopicRead)
def read_topic(topic_id: int, session: Session = Depends(get_session)):
    topic = session.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/{topic_id}", response_model=TopicRead)
def update_topic(topic_id: int, topic: TopicUpdate, session: Session = Depends(get_session)):
    db_topic = session.get(Topic, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic_data = topic.dict(exclude_unset=True)
    for key, value in topic_data.items():
        setattr(db_topic, key, value)
        
    session.add(db_topic)
    session.commit()
    session.refresh(db_topic)
    return db_topic

@router.delete("/{topic_id}")
def delete_topic(topic_id: int, session: Session = Depends(get_session)):
    topic = session.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    session.delete(topic)
    session.commit()
    return {"ok": True}

@router.post("/batch-delete")
def batch_delete_topics(ids: List[int] = [], session: Session = Depends(get_session)):
    # Note: Using body for deletion is non-standard but practical
    # Or strict REST: DELETE /topics?ids=1,2,3
    # Design says POST /topics/batch-delete
    
    # We iterate for SQLite simplicity
    from typing import Sequence # Import if needed, or just list
    
    for id in ids:
        topic = session.get(Topic, id)
        if topic:
            session.delete(topic)
    session.commit()
    return {"ok": True}
