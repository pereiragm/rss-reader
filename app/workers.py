from sqlalchemy.orm import Session

from app.crud.post import create_post
from app.models import Feed
from app.readers.base_reader import RSSFeedReader


def refresh_feed(feed_uuid: str, db: Session) -> None:
    feed = db.query(Feed).filter_by(uuid=feed_uuid).one()
    reader = RSSFeedReader(rss_url=feed.link)
    for post in reader.model.posts:
        create_post(db, obj_in=post, feed_id=feed.id)


def refresh_valid_feeds(db: Session) -> None:
    # get all refreshable feeds
    feed_uuids = db.query(Feed.uuid).filter(Feed.refresh_enabled.is_(True)).all()
    for (uuid,) in feed_uuids:
        refresh_feed(feed_uuid=str(uuid), db=db)
