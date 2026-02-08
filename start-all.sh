#!/bin/bash
# Complete startup script for both backend and frontend

echo "🚀 Starting Guru Suite..."
echo ""

# Kill any existing processes
echo "Stopping existing processes..."
pkill -9 -f "next dev" 2>/dev/null
pkill -9 -f "uvicorn.*main" 2>/dev/null
pkill -9 -f "python.*start_server" 2>/dev/null
sleep 2

# Start Backend
echo "Starting Backend (port 8000)..."
cd apps/guru-api
python3 start_server.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 5

# Check backend
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start. Check /tmp/backend.log"
    tail -20 /tmp/backend.log
fi

# Start Frontend
echo ""
echo "Starting Frontend (port 3000)..."
cd ../guru-web/guru-web
rm -rf .next 2>/dev/null
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
echo "Waiting for frontend to compile (this may take 20-30 seconds)..."
sleep 20

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend not responding yet. Check /tmp/frontend.log"
    tail -30 /tmp/frontend.log
fi

echo ""
echo "Backend logs: /tmp/backend.log"
echo "Frontend logs: /tmp/frontend.log"
echo ""
echo "Backend: http://127.0.0.1:8000/health"
echo "Frontend: http://localhost:3000"
