from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    description: str
    link: str
    pub_date: datetime
