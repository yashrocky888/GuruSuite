#!/bin/bash

# GURU API Backend - Quick Run Script

echo "🚀 Starting GURU API Backend..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "⚠️  Warning: .env file not found in project root"
    echo "   Make sure .env exists with GURU_API_KEY"
    echo ""
fi

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "❌ uvicorn not found. Installing dependencies..."
    python3 -m pip install -r requirements.txt
    echo ""
fi

# Run the server
echo "✅ Starting server on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
