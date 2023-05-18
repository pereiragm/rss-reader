import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Feed(Base):
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    title = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(1000), nullable=False)
    link = Column(String(255), unique=True, nullable=False)
    language = Column(String(255), nullable=True)
    last_build_date = Column(DateTime(timezone=True), nullable=True, index=True)
    refresh_enabled = Column(Boolean(), nullable=False, default=True)
    posts = relationship("Post", back_populates="feed", lazy="dynamic")