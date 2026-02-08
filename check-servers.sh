#!/bin/bash
echo "=== Server Status Check ==="
echo ""

echo "Backend (port 8000):"
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
    curl -s http://127.0.0.1:8000/health
else
    echo "❌ Backend is NOT running"
fi
echo ""

echo "Frontend (port 3000):"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend is NOT running"
fi
echo ""

echo "Running processes:"
ps aux | grep -E "next dev|uvicorn|start_server" | grep -v grep | head -3
