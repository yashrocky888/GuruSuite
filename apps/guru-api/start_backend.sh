#!/bin/bash
# Backend startup script for Guru API

cd "$(dirname "$0")"

# Kill any existing uvicorn processes
pkill -f "uvicorn.*main:app" || true
sleep 2

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Try to start the backend
echo "🚀 Starting Guru API backend on 127.0.0.1:8000..."
python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000
