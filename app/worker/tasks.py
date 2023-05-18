from datetime import datetime

from celery.utils.log import get_task_logger
from fastapi import Depends
from sqlalchemy.orm import Session

from app.crud.post import create_post
from app.db.session import SessionLocal
from app.main import get_db
from app.models import Feed, Post
from app.readers.base_reader import RSSFeedReader
from app.worker.celery import app as celery_app
from celery.app.log import Logging

logger = get_task_logger(__name__)


@celery_app.task
def add(x, y):
    result = x + y
    print(f"The result of x + y = {result}")
    return result


@celery_app.task
def query_feeds():
    def _query(db):
        feeds = db.query(Feed).all()
        logger.info("===> Feeds from the DB:")
        for feed in feeds:
            logger.info(f"Feed(id={feed.id}, name={feed.title})")

    base_log = "[query_feeds]"

    logger.info(f"{base_log} - Started.")

    try:
        db = SessionLocal()
        _query(db)
    finally:
        db.close()

    logger.info(f"{base_log} - Finished.")


@celery_app.task
def refresh_feed(feed_uuid: str) -> None:
    def _get_most_recent_post_pub_date(_feed: Feed) -> datetime | None:
        post = _feed.posts.order_by(Post.pub_date.desc()).first()
        return post.pub_date if post else None

    base_log = "[refresh_feed]"

    logger.info(f"{base_log} - Start")

    try:
        db = SessionLocal()
        feed = db.query(Feed).filter_by(uuid=feed_uuid).one()
        most_recent_post_dt = _get_most_recent_post_pub_date(feed)
        reader = RSSFeedReader(rss_url=feed.link)
        # logger.info(f"{base_log} - reader feed: {reader.model.dict()}")

        if most_recent_post_dt is None:
            # Select all posts retrieved from the RSS feed
            posts_to_be_dumped = reader.model.posts
        else:
            posts_to_be_dumped = [
                post
                for post in reader.model.posts
                if post.pub_date > most_recent_post_dt
            ]

        for post in posts_to_be_dumped:
            create_post(db, obj_in=post, feed_id=feed.id)
    finally:
        db.close()

    logger.info(f"{base_log} - End")


@celery_app.task()
def refresh_feeds_routine() -> None:
    try:
        db = SessionLocal()

        # get all refreshable feeds uuids
        feed_uuids = db.query(Feed.uuid).filter(Feed.refresh_enabled.is_(True)).all()

        for (uuid,) in feed_uuids:
            refresh_feed.delay(str(uuid))
    finally:
        db.close()


@celery_app.task(
    bind=True,
    retry_kwargs={'max_retries': 3, "retry_backoff": True},
)
def test_task(self):
    try:
        logger.info("TESTING..............")
        a = 1/0
    except Exception as exc:
        raise self.retry(exc=exc)
