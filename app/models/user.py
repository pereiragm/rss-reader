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

user_post = Table(
    "user_post",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("post_id", ForeignKey("post.id"), primary_key=True),
)


class User(Base):
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False, index=True)
    feeds = relationship(
        "Feed", secondary=user_feed, backref="followers", lazy="dynamic"
    )
    read_posts = relationship(
        "Post", secondary=user_post, backref="readers", lazy="dynamic"
    )
