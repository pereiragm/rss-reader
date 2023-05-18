# rss-reader

## Installation

Open a terminal and follow these instructions:
```commandline
Create virtual en and activate it
pip install -U pip poetry==1.4.2
```

Install the project dependencies with poetry:
```commandline
poetry install
```

Start postgres
```commandline
docker container run -d -p 5435:5432 --name pgsql --mount type=volume,src=dbdata,dst=/data -e POSTGRES_PASSWORD=postgres postgres:15.2
```

Initialize DB by entering the container and creating the databases manually:
```commandline
docker exec -it pgsql bash
su -l postgres -c psql
CREATE ROLE dbadmin WITH LOGIN PASSWORD 'dbadmin';
CREATE DATABASE  rss_reader OWNER dbadmin;
CREATE DATABASE  rss_reader_test OWNER dbadmin;
```