#!/bin/bash
# Simple backend startup script from project root

cd "$(dirname "$0")/apps/guru-api"

echo "🚀 Starting Guru API Backend..."
echo "📍 Directory: $(pwd)"
echo ""

# Kill any existing processes
pkill -f "uvicorn.*main:app" 2>/dev/null || true
sleep 2

# Start the backend
python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000
