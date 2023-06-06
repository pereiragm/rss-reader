from celery import Celery

from app.core.config import settings

app = Celery(
    main="rss-reader-worker",
    broker=settings.BROKER_URL,
    include=[
        "app.worker.tasks",
    ],
)

app.conf.beat_schedule = {
    "refresh-feeds-routine": {
        "task": "app.worker.tasks.refresh_feeds_routine",
        "schedule": 300,  # every 5 minutes
    },
}
app.conf.timezone = "UTC"
