from datetime import datetime

from pydantic import BaseModel

from app.schemas.post import PostBase


class FeedBase(BaseModel):
    title: str
    description: str
    link: str
    language: str | None = None
    last_build_date: datetime = None
    posts: list[PostBase] = []
