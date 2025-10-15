import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Character(BaseModel):
    id: str = Field(alias="_id")
    name: str
    ch: Optional[int] = None
    rss_order: Optional[str] = None
    rss_level: Optional[int] = None
    slot_number: Optional[int] = None

    class Config:
        populate_by_name = True


class Account(BaseModel):
    """
    Represents an account resource in the system.
    """

    id: str = Field(alias="_id")
    name: str
    characters: Optional[List[str]] = []

    class Config:
        populate_by_name = True


class TaskRequest(BaseModel):
    tasks: List[str]
    instance_name: str
    mode: int


# match TaskRecord with MongoDB document structure
class TaskRecord(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    tasks: List[str]
    instance_name: str
    mode: int
    status: Literal["queued", "running", "completed", "failed", "stopped"] = "queued"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    log_file: Optional[str] = None

    class Config:
        populate_by_name = True
