#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER dbadmin WITH PASSWORD 'dbadmin';
	CREATE DATABASE rss_reader OWNER dbadmin;
    CREATE DATABASE rss_reader_test OWNER dbadmin;
EOSQL
