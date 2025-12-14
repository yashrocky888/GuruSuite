#!/bin/bash
# Phase 21: Start script for Guru API

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults
WORKERS=${WORKERS:-4}
API_HOST=${API_HOST:-0.0.0.0}
API_PORT=${API_PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-INFO}

echo "Starting Guru API..."
echo "Workers: $WORKERS"
echo "Host: $API_HOST"
echo "Port: $API_PORT"
echo "Log Level: $LOG_LEVEL"

# Run uvicorn with multiple workers
uvicorn api.main:app \
    --host "$API_HOST" \
    --port "$API_PORT" \
    --workers "$WORKERS" \
    --log-level "$LOG_LEVEL" \
    --access-log \
    --no-use-colors

