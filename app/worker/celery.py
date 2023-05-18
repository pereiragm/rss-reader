from celery import Celery

broker_url = 'amqp://localhost:5672'

app = Celery(
    main="rss-reader-worker",
    broker=broker_url,
    include=[
        "app.worker.tasks",
    ]
)


@app.task(
    bind=True,
    retry_kwargs={'max_retries': 3, "retry_backoff": True},
)
def add2(x, y):
    result = x + y
    print(f"The result of x + y = {result}")
    return result
