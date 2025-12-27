from typing import List, Optional, Dict
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, Column, JSON

# --- 1. Persona (人设) ---
class PersonaBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    depth: int = Field(default=5, description="Professional depth 1-10")
    custom_prompt: Optional[str] = Field(default=None, sa_column=Column(JSON), description="System Prompt config")
    interests: List[str] = Field(default=[], sa_column=Column(JSON))

class Persona(PersonaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    source_configs: List["SourceConfig"] = Relationship(back_populates="persona")

class PersonaCreate(PersonaBase):
    pass

class PersonaRead(PersonaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    source_configs: List["SourceConfigRead"] = []

class PersonaUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    depth: Optional[int] = None
    custom_prompt: Optional[str] = None
    interests: Optional[List[str]] = None


# --- 2. SourceConfig (数据源配置) ---
class SourceConfigBase(SQLModel):
    persona_id: Optional[int] = Field(default=None, foreign_key="persona.id")
    type: str = Field(description="bilibili_user, rss_feed, hot_list")
    name: str
    config_data: Dict = Field(default={}, sa_column=Column(JSON), description="{uid: '...', url: '...'}")
    enabled: bool = Field(default=True)

class SourceConfig(SourceConfigBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    persona: Optional[Persona] = Relationship(back_populates="source_configs")
    topics: List["Topic"] = Relationship(back_populates="source_config")

class SourceConfigCreate(SourceConfigBase):
    pass

class SourceConfigRead(SourceConfigBase):
    id: int

class SourceConfigUpdate(SQLModel):
    name: Optional[str] = None
    config_data: Optional[Dict] = None
    enabled: Optional[bool] = None


# --- 3. Topic (选题) ---
class TopicBase(SQLModel):
    source_config_id: Optional[int] = Field(default=None, foreign_key="sourceconfig.id")
    original_id: str = Field(index=True, description="Unique ID from source to prevent duplicates")
    title: str
    url: str
    summary: Optional[str] = None
    thumbnail: Optional[str] = None
    
    metrics: Dict = Field(default={}, sa_column=Column(JSON), description="{views: 1200, stars: 500}")
    analysis_result: Dict = Field(default={}, sa_column=Column(JSON), description="{difficulty: 'Low', personaMatch: 'High'}")
    
    status: str = Field(default="new", description="new, saved, rejected")
    published_at: Optional[datetime] = None
    saved_at: datetime = Field(default_factory=datetime.utcnow)

class Topic(TopicBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    source_config: Optional[SourceConfig] = Relationship(back_populates="topics")
    tags: List["TopicTag"] = Relationship(back_populates="topic")
    scripts: List["Script"] = Relationship(back_populates="topic")

class TopicCreate(TopicBase):
    pass

class TopicRead(TopicBase):
    id: int

class TopicUpdate(SQLModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    analysis_result: Optional[Dict] = None
    metrics: Optional[Dict] = None


# --- 4. TopicTag (选题标签) ---
class TopicTag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topic.id")
    tag_name: str
    
    topic: Optional[Topic] = Relationship(back_populates="tags")


# --- 5. ScriptTemplate (脚本模板) ---
class ScriptTemplateBase(SQLModel):
    name: str
    content_template: str = Field(description="Markdown with {{placeholders}}")
    type: str = Field(default="fast_paced")

class ScriptTemplate(ScriptTemplateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ScriptTemplateCreate(ScriptTemplateBase):
    pass

class ScriptTemplateRead(ScriptTemplateBase):
    id: int

class ScriptTemplateUpdate(SQLModel):
    name: Optional[str] = None
    content_template: Optional[str] = None
    type: Optional[str] = None


# --- 6. Script (脚本) ---
class ScriptBase(SQLModel):
    topic_id: int = Field(foreign_key="topic.id")
    template_id: Optional[int] = Field(default=None, foreign_key="scripttemplate.id")
    title: str
    content: str
    status: str = Field(default="draft")

class Script(ScriptBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    topic: Optional[Topic] = Relationship(back_populates="scripts")

class ScriptCreate(ScriptBase):
    pass

class ScriptRead(ScriptBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ScriptUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
