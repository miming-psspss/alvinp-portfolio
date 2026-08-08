#!/bin/bash
# Runs automatically on first container start (postgres official image sources every
# .sh file in /docker-entrypoint-initdb.d/). Creates the second database this project
# needs (cas_test, for the fictional member/staff/BOD/policy dataset) and loads its
# schema + seed data. n8n's own internal state stays in $N8N_DB, created separately by
# the postgres image itself via POSTGRES_DB.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -c "CREATE DATABASE cas_test;"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d cas_test -f /docker-entrypoint-initdb.d/cas-schema.sql

echo "cas_test database created and schema loaded."
