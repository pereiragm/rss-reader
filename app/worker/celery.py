from celery import Celery

broker_url = "amqp://localhost:5672"

app = Celery(
    main="rss-reader-worker",
    broker=broker_url,
    include=[
        "app.worker.tasks",
    ],
)
