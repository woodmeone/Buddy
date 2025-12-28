from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from ..database import get_session
from ..models import Topic, TopicCreate, TopicRead, TopicUpdate

router = APIRouter(prefix="/api/v1/topics", tags=["topics"])

@router.post("/{topic_id}/generate-metadata", response_model=TopicRead)
def generate_topic_metadata(topic_id: int, session: Session = Depends(get_session)):
    """
    Generates and persists AI titles, summary and tags for a topic.
    """
    db_topic = session.get(Topic, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # If already has AI title, return existing (as per user's 'persistence' request)
    if db_topic.ai_title:
        return db_topic

    # Mock AI Generation Logic
    # In reality, call LLM here.
    import time
    time.sleep(1)
    
    db_topic.ai_title = f"【爆款】{db_topic.title[:20]}... 的深度解析"
    db_topic.ai_summary = f"基于原视频 '{db_topic.title}'，本选题聚焦于创作者的核心痛点，分析了其火爆背后的底层逻辑..."
    
    # Update analysis_result with keywords
    analysis = db_topic.analysis_result or {}
    analysis["keywords"] = ["爆款逻辑", "内容创作", "选题分析"]
    analysis["targetAudience"] = "内容创作者，短视频博主"
    db_topic.analysis_result = analysis
    
    session.add(db_topic)
    session.commit()
    session.refresh(db_topic)
    return db_topic

@router.get("/", response_model=List[TopicRead])
def read_topics(session: Session = Depends(get_session)):
    topics = session.exec(select(Topic).order_by(Topic.saved_at.desc())).all()
    return topics

@router.post("/", response_model=TopicRead)
def create_topic(topic: TopicCreate, session: Session = Depends(get_session)):
    # Check for duplicate by original_id
    existing = session.exec(select(Topic).where(Topic.original_id == topic.original_id)).first()
    if existing:
        # Optional: update existing? For now, just return it to be idempotent
        return existing

    db_topic = Topic.from_orm(topic)
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
