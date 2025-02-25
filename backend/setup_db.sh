#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if psql (PostgreSQL CLI) is installed
if ! command_exists psql; then
    echo "Error: PostgreSQL CLI (psql) is not installed."
    echo "Please install PostgreSQL and ensure psql is accessible via the terminal."
    echo "Installation instructions:"
    echo "  - macOS: brew install postgresql"
    echo "  - Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "  - Windows: Download from https://www.postgresql.org/download/"
    exit 1
fi

# Ensure PostgreSQL service is running (Linux/macOS)
if command_exists systemctl; then
    sudo systemctl start postgresql
elif command_exists service; then
    sudo service postgresql start
fi

# Load environment variables
source .env

# Create the database and user if they don't exist
echo "Setting up PostgreSQL database..."

# Check if database exists, create it if not
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -U postgres -c "CREATE DATABASE $DB_NAME;"

# Check if user exists, create it if not
psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER'" | grep -q 1 || \
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

# Grant privileges to the user
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "PostgreSQL database setup complete."
