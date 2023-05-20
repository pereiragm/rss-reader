from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.post import PostBase


class FeedBase(BaseModel):
    title: str
    description: str
    link: str
    language: str | None = None
    last_build_date: datetime = None
    posts: list[PostBase] = []


class FeedBase2(BaseModel):
    uuid: Optional[UUID]
    title: str
    description: str
    link: str
    language: str | None = None
    last_build_date: datetime = None
    refresh_enabled: bool = True


class FeedRssReader(FeedBase2):
    posts: list[PostBase] = []


class FeedCreate(FeedBase2):
    pass
