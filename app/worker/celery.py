from celery import Celery

broker_url = "amqp://localhost:5672"

app = Celery(
    main="rss-reader-worker",
    broker=broker_url,
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
