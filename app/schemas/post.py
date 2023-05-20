from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    description: str
    link: str
    pub_date: datetime


class PostBase2(BaseModel):
    uuid: Optional[UUID]
    title: str
    description: str
    link: str
    pub_date: datetime


class PostCreate(PostBase2):
    pass
