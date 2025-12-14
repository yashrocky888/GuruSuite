#!/bin/bash

# Startup script for Guru API
# This script handles database initialization and starts the FastAPI server

echo "🚀 Starting Guru API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Using default configuration."
    echo "   Please create .env file from .env.example for production use."
fi

# Wait for database to be ready (if using PostgreSQL)
if [ ! -z "$DATABASE_URL" ]; then
    echo "⏳ Waiting for database to be ready..."
    # Add database connection check here if needed
fi

# Run database migrations (if using Alembic)
# Uncomment the following lines if you set up Alembic migrations
# echo "🔄 Running database migrations..."
# alembic upgrade head

# Start the application
echo "✨ Starting FastAPI server..."
exec uvicorn src.main:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload

