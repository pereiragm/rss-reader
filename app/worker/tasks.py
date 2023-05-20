from celery.utils.log import get_task_logger

from app.db.session import SessionLocal
from app.models import Feed
from app.readers import helpers
from app.worker.celery import app as celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
# def refresh_feed(self, feed_uuid: str, default_countdowns: tuple[int] = (1, 5)) -> None:
def refresh_feed(
        self,
        feed_uuid: str,
        default_countdowns: tuple[int] = (2 * 60, 5 * 60, 8 * 60)
) -> None:
    """
    Task to refresh feed posts.
    Max retries = 3 with default back-off mechanism
    of 2, 5 and 8 minutes between retries.
    """

    base_log = f"[refresh_feed] - Feed({feed_uuid}) -"

    logger.info(f"{base_log} Start")

    try:
        db = SessionLocal()
        helpers.refresh_feed(db, feed_uuid)
    except Exception as exc:
        logger.exception(f"{base_log} {exc}")
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
