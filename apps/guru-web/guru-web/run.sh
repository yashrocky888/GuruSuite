#!/bin/bash

# GURU Frontend - Quick Run Script

echo "🚀 Starting GURU Frontend..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Backend not detected on http://localhost:8000"
    echo "   Make sure backend is running: cd ../guru-api && python3 main.py"
    echo ""
fi

# Run the development server
echo "✅ Starting Next.js dev server on http://localhost:3000"
echo "   Press Ctrl+C to stop"
echo ""
npm run dev

