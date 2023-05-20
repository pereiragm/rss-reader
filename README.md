# rss-reader

## Requirements
Python 3.11+

## Installation

Open a terminal and follow the instructions:

Create a virtual environment and activate it:
```commandline
python3 -m venv venv/
source venv/bin/activate
```

Install poetry (manage ours dependencies) and install the project:
```commandline
pip install -U pip poetry==1.4.2
poetry install
```

## Running the application

Step 1 - Start a container with PostgreSQL:
```commandline
docker container run -d -p 5435:5432 --name pgsql -e POSTGRES_PASSWORD=postgres postgres:15.2
```

Step 2 - Enter the `pgsql` container and the databases manually:
```commandline
docker exec -it pgsql bash
su -l postgres -c psql
CREATE ROLE dbadmin WITH LOGIN PASSWORD 'dbadmin';
CREATE DATABASE  rss_reader OWNER dbadmin;
CREATE DATABASE  rss_reader_test OWNER dbadmin;
```
The `rss_reader` is used by the application and the `rss_reader_test` is used
only to run the tests.

Step 3 - On another terminal, create the tables with alembic on database `rss_reader`:
```commandline
alembic -c alembic.ini upgrade head
```

Step 4 - Add some initial data by running the script initialize_db.py:
```commandline
python initialize_db.py
```

Step 4 - Start a container with the rabbitmq broker, sob the beat can add messages
and the celery worker would be able to get them and process:
```commandline
docker run -d -p 5672:5672 --name rabbitmq-broker rabbitmq
```

After all this set up you can run the different processes in different terminals:
- Web application (access the swagger with the API on http://localhost:8000/docs)
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
On a terminal execute:
```commandline
pytest -v
```