#!/bin/bash

set -e

# Load environment variables
source .env

# PostgreSQL authentication
export PGPASSWORD=$DB_PASS
#psql -U postgres -d $DB_NAME -h $DB_HOST -p $DB_PORT
psql -U postgres -d $DB_NAME -h $DB_HOST -p $DB_PORT -c "GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;"
psql -U postgres -d $DB_NAME -h $DB_HOST -p $DB_PORT -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
psql -U postgres -d $DB_NAME -h $DB_HOST -p $DB_PORT -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"

echo "Applying migrations..."
alembic upgrade head

echo "Seeding the database..."
python seed_db.py

echo "Database seeding completed!"
