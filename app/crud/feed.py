from sqlalchemy.orm import Session

from app.models import Feed
from app.schemas.feed import FeedCreate


def get_feed(db: Session, uuid: str) -> Feed | None:
    return db.query(Feed).filter_by(uuid=uuid).one_or_none()


def create_feed(db: Session, obj_in: FeedCreate) -> Feed:
    feed_obj = Feed(**obj_in.dict())
    db.add(feed_obj)
    db.commit()
    db.refresh(feed_obj)
    return feed_obj
