import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base

user_feed = Table(
    "user_feed",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("feed_id", ForeignKey("feed.id"), primary_key=True),
)


class User(Base):
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    feeds = relationship("Feed", secondary=user_feed, backref="followers", lazy="dynamic")
    # hashed_password = Column(String, nullable=False)
    # is_active = Column(Boolean(), default=True)
    # is_superuser = Column(Boolean(), default=False)
