#!/bin/bash
# Quick server start script for Guru API

echo "🚀 Starting Guru API Server..."
echo ""

cd "$(dirname "$0")"

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8000 is already in use!"
    echo "   Either stop the existing server or use a different port"
    echo ""
    echo "   To stop existing server:"
    echo "   kill \$(lsof -ti:8000)"
    exit 1
fi

echo "📍 Starting server on http://localhost:8000"
echo "📚 API Docs will be at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

