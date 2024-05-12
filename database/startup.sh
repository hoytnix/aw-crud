#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER hoyt;

    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'hoyt') THEN
        RAISE NOTICE 'Database already exists';
    ELSE
        CREATE DATABASE hoyt;

    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'test_hoyt') THEN
        RAISE NOTICE 'Database already exists';
    ELSE
        CREATE DATABASE test_hoyt;

    GRANT ALL PRIVILEGES ON DATABASE hoyt TO hoyt;
    GRANT ALL PRIVILEGES ON DATABASE test_hoyt TO hoyt;
EOSQL
