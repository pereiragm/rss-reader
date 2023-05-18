from datetime import datetime

from celery.utils.log import get_task_logger

from app.crud.post import create_post
from app.db.session import SessionLocal
from app.models import Feed, Post
from app.readers.base_reader import RSSFeedReader
from app.worker.celery import app as celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def refresh_feed(self, feed_uuid: str, default_countdowns: tuple[int] = (1, 5)) -> None:
    # def refresh_feed(self, feed_uuid: str, default_countdowns: tuple[int] = (2 * 60, 5 * 60, 8 * 60)) -> None:  # 3 retries in 2, 5 and 8 minutes
    def _get_most_recent_post_pub_date(_feed: Feed) -> datetime | None:
        post = _feed.posts.order_by(Post.pub_date.desc()).first()
        return post.pub_date if post else None

    base_log = f"[refresh_feed] - Feed({feed_uuid}) -"

    logger.info(f"{base_log} Start")

    try:
        db = SessionLocal()
        feed = db.query(Feed).filter_by(uuid=feed_uuid).one()
        most_recent_post_dt = _get_most_recent_post_pub_date(feed)
        reader = RSSFeedReader(rss_url=feed.link)

        if most_recent_post_dt is None:
            # Select all posts retrieved from the RSS feed
            posts_to_be_added = reader.model.posts
        else:
            posts_to_be_added = [
                post
                for post in reader.model.posts
                if post.pub_date > most_recent_post_dt
            ]

        for post in posts_to_be_added:
            create_post(db, obj_in=post, feed_id=feed.id)
    except Exception as exc:
        logger.exception(f"{base_log} exc")
        if self.request.retries == len(default_countdowns):
            logger.info(f"{base_log} Reached max_retries. Aborting...")
        else:
            raise self.retry(
                exc=exc, countdown=default_countdowns[self.request.retries]
            )
    finally:
        db.close()

    logger.info(f"{base_log} End")


@celery_app.task(max_retries=3, default_retry_delay=30)
def refresh_feeds_routine() -> None:
    try:
        db = SessionLocal()

        # get all refreshable feeds uuids
        feed_uuids = db.query(Feed.uuid).filter(Feed.refresh_enabled.is_(True)).all()

        for (uuid,) in feed_uuids:
            refresh_feed.delay(str(uuid))
    finally:
        db.close()
