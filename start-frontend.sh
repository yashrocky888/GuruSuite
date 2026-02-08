#!/bin/bash
# Simple frontend startup script from project root

cd "$(dirname "$0")/apps/guru-web/guru-web"

echo "🚀 Starting Guru Web Frontend..."
echo "📍 Directory: $(pwd)"
echo "🌐 URL: http://localhost:3000"
echo ""

# Kill any existing Next.js processes
pkill -f "next dev" 2>/dev/null || true
sleep 2

# Start the frontend
npm run dev
