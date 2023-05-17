import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class Post(Base):
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feed.id"))
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    title = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(1000), nullable=False)
    link = Column(String(255), unique=True, nullable=False)
    pub_date = Column(DateTime(), nullable=False, index=True)
