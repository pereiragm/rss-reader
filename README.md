# rss-reader

Web service which provides an API to interact with multiple RSS feeds and a background
process to fetch the most recend feeds registered on our database.

## System Design
The classes have beens designed as shown in the diagram below:

![Classes diagram](db_relationship_diagram.png)

- A post points to a unique feed and a feed can have multiple posts.
- A user can follow or unfollow a post. Hence, a register on the N-N table `UserFeed`
represents a subscription of a user to a post, and a removal represents the unfollow
action.
- A user can mark a post as read. Hence, when it happens we add a register on the N-N
table `UserPost`, and its removal represents the inverse (unread).

Based on this design we have the system divided in two parts:

**Background Process:**
- Implemented with [Celery](https://docs.celeryq.dev/en/stable/index.html) and [RabbitMQ](https://www.rabbitmq.com/)
  to perform the asynchronous processing of feed refresh.
- Routine (every 5 minutes) to trigger a refresh on all feeds which are "refreashable"
  (default=True), which means querying their URL, parsing 
  its information and inserting the posts related to the feed. Each feed refresh is 
  performed by an isolated task, which can be processes in parallel by multiple
  workers.
- In case of failure on a feed refresh, the system provides 3 retries with a back-off
  mechanism of 2, 5 and 8 minutes between retries. If the task reach the max retries
  without success it will try to refresh on the next routine scheduled by the system (in 5 minutes).


**API**
- Endpoints for the user to perform the actions of follow/unfollow a feed or
  mark a post as read/unread.
- Endpoint to force a feed refresh (synchronously)
- Endpoint to list posts using filters (read/unread, by feed)
- Implemented with [FastAPI](https://fastapi.tiangolo.com/) framework
- Offers an OpenAPI documentation for the API where you make requests to the available endpoints
  using the browser and explore details of each endpoint (request/response schemas).
  You can check how to access it on the section "Running the application".

## Running the application

### Docker (preferred)
The installation with docker requires that you have both [docker](https://docs.docker.com/get-started/) 
and [docker compose](https://docs.docker.com/compose/) installed on your host machine.
It means that you don't need to install python, neither have the services like
PostgreSQL and RabbitMQ running on your machine. This is because docker compose will
take care of building/downloading the images related to each service and creating
isolated containers (logical and physical isolation) running the processes for each
service (check the [docker-compose.yml](docker-compose.yml) file).

If it's **your first time** running the project or if you removed the containers
and volumes start with **Step 1**, otherwise proceed to **Step 3**.

**Step 1** - Open a terminal run the following command to create the databases
(development and test) and execute migration to create the tables
```commandline
docker compose run web alembic -c alembic.ini upgrade head 
```
This will start a new container for the `web` service (will also start a container
for the `db` service as it's a dependency) and run a one-off command to execute the 
migration

**Step 2 (optional)** - Populate the database with initial data (user and some feeds):
```commandline
docker compose run web python app/initialize_db.py
```

**Step 3** - Create containers and start all services:
```commandline
docker compose up -d
```
You can check the running services with:
```commandline
docker compose ps
```
And open the logs for each service (check the names on the Compose file)
in a separate terminal:
```commandline
docker compose logs -f <service_name> 
```
To stop all services and remove the containers:
```commandline
docker compose down
```
**Note:** use the option `--volumes` (e.g., `docker compose down --volumes`)
to also remove named volumes declared in the volumes section of the Compose file and
anonymous volumes attached to containers. In practice, it will destroy the databases
created on **Step 1** and consequently the initial data populated on **Step 2**.


### Locally (host machine)
This process requires that you have Python 3.11+ installed on your host machine, so
we can install the project dependencies in a [virtualenv](https://docs.python.org/3/library/venv.html)
to execute the web, worker and beat processes. Also, as web application and celery 
worker rely on both PostgreSQL 15.2 and RabbitMQ services running on your host machine,
you need to install them or use docker to start a container for each one of them
(the second option is what is described here).

First, lets install the project. Open a terminal and follow the instructions:

Create a virtual environment and activate it:
```commandline
python3 -m venv venv/
source venv/bin/activate
```

Install [poetry](https://python-poetry.org/docs/) (dependency manager)
```commandline
pip install -U pip poetry==1.4.2
```

Install the project:
```commandline
poetry install
```

After installing the project, lets run the application by following the steps:

**Step 1** - Start the `db` service (will create a container with PostgreSQL and execute
[initialization script](init_db.sh) to create user and databases)
```commandline
docker compose up -d db
```
The `rss_reader` is used by the application and the `rss_reader_test` is used
only to run the tests.

**Step 2** - On another terminal, run the migration to create the tables with alembic
on database `rss_reader`:
```commandline
alembic -c alembic.ini upgrade head
```

**Step 3 (optional)** - Populate the database with initial data (user and some feeds):
```commandline
python app/initialize_db.py
```

**Step 4** - Start `broker` service which will create a container with the RabbitMQ,
so the beat (routine scheduler) can add messages to the broker (message queue) and
the celery worker will be able to get them and process:
```commandline
docker compose up -d broker
```

After all this set up you can run the different processes in different terminals:
- Web application (access the OpenAPI documentation generated automatically on http://localhost:8000/docs)
    ```commandline
    uvicorn app.main:app --reload
    ```
- Celery worker
    ```commandline
    celery -A app.worker worker -l INFO
    ```
- Celery beat
    ```commandline
    celery -A app.worker beat -l INFO
    ```

## Running Tests

- If you are running the project with docker and docker compose, open a terminal and
execute:
  ```commandline
  docker compose run web pytest -v
  ```

- If your installed the project locally, you can simply execute:
  ```commandline
  pytest -v
  ```
  Note: make sure the `db` is running (`docker compose ps`) and if not, start it 
  with `docker compose up -d db`.
