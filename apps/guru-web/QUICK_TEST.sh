#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "  GURU PROJECT - QUICK TEST SCRIPT"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if backend is running
echo "1. Checking Backend API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on http://localhost:8000"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "   Backend responded"
else
    echo "   ❌ Backend is NOT running"
    echo "   Start it with: cd guru-api && uvicorn main:app --reload"
fi

echo ""
echo "2. Checking Frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running on http://localhost:3000"
else
    echo "   ❌ Frontend is NOT running"
    echo "   Start it with: cd guru-web && npm run dev"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  TESTING CHECKLIST"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Open http://localhost:3000 and test:"
echo ""
echo "  [ ] Home page loads (/)"
echo "  [ ] Can submit birth details"
echo "  [ ] Dashboard loads (/dashboard)"
echo "  [ ] Kundli page (/kundli)"
echo "  [ ] Divisional charts (/kundli/divisional)"
echo "  [ ] Dasha timeline (/dasha)"
echo "  [ ] Transits page (/transits)"
echo "  [ ] Panchang page (/panchang)"
echo "  [ ] Guru AI page (/guru)"
echo ""
echo "Check browser console (F12) for errors"
echo "Check Network tab for API calls"
echo ""
