from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    original_file: Optional[str] = None
    transformed_file: Optional[str] = None
    lyrics: Optional[str] = None
    style: Optional[str] = None
    stems_directory: Optional[str] = None
    midi_files: Optional[List[str]] = []
    musicxml_files: Optional[List[str]] = []
    main_midi: Optional[str] = None
    transformation_type: Optional[str] = None
    transformation_complete: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectCreate(BaseModel):
    name: str


class UserStyle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    sample_lyrics: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserStyleCreate(BaseModel):
    name: str
    description: str
    sample_lyrics: str


class LyricsRequest(BaseModel):
    project_id: str
    style: str
    custom_prompt: Optional[str] = None
    user_style_id: Optional[str] = None


class LyricsResponse(BaseModel):
    lyrics: str
    style: str
