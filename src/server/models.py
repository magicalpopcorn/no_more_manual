from typing import List, Optional

from pydantic import BaseModel, Field


class Character(BaseModel):
    id: str = Field(alias="_id")
    name: str
    ch: Optional[int] = None
    rss_order: Optional[str] = None
    rss_level: Optional[int] = None
    slot_number: Optional[int] = None


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    ch: Optional[int] = None
    rss_order: Optional[str] = None
    rss_level: Optional[int] = None
    slot_number: Optional[int] = None


class Account(BaseModel):
    """
    Represents an account resource in the system.
    """

    id: str = Field(alias="_id")
    name: str
    characters: Optional[List[str]] = []


class AccountUpdate(BaseModel):
    """
    Represents a partial update to an account.
    """

    name: Optional[str] = None
    characters: Optional[List[str]] = None


class TaskRequest(BaseModel):
    instance_name: str
    tasks: List[str]
    mode: int
