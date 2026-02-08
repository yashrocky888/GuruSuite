#!/bin/bash
# Shadbala Go-Live Verification Script
# Run this after deployment to verify everything is working

set -e

echo "🔍 SHADBALA GO-LIVE VERIFICATION"
echo "=================================="
echo ""

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

# Test data
TEST_DOB="2006-02-03"
TEST_TIME="22:30"
TEST_LAT=12.9716
TEST_LON=77.5946

echo "📡 Step 1: Testing Backend API..."
echo "   URL: $API_URL/strength/shadbala"
echo ""

# Test API endpoint
API_RESPONSE=$(curl -s "${API_URL}/strength/shadbala?dob=${TEST_DOB}&time=${TEST_TIME}&lat=${TEST_LAT}&lon=${TEST_LON}" 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ Backend API not accessible"
    echo "   Error: $API_RESPONSE"
    exit 1
fi

# Check for status field
if echo "$API_RESPONSE" | grep -q '"status"'; then
    echo "✅ API returns status field"
else
    echo "❌ API missing status field"
    exit 1
fi

# Check for ratio field
if echo "$API_RESPONSE" | grep -q '"ratio"'; then
    echo "✅ API returns ratio field"
else
    echo "❌ API missing ratio field"
    exit 1
fi

# Check calculation_mode
if echo "$API_RESPONSE" | grep -q '"calculation_mode".*"PURE BPHS"'; then
    echo "✅ API returns PURE BPHS calculation_mode"
else
    echo "❌ API calculation_mode incorrect"
    exit 1
fi

# Extract and verify Sun status
SUN_STATUS=$(echo "$API_RESPONSE" | grep -o '"Sun".*"status":"[^"]*"' | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ -z "$SUN_STATUS" ]; then
    echo "❌ Could not extract Sun status"
    exit 1
fi

if [[ "$SUN_STATUS" =~ ^(Very Strong|Strong|Average|Weak)$ ]]; then
    echo "✅ Sun status is valid: $SUN_STATUS"
else
    echo "❌ Sun status is invalid: $SUN_STATUS"
    exit 1
fi

echo ""
echo "🌐 Step 2: Testing Frontend..."
echo "   URL: $FRONTEND_URL/shadbala"
echo ""

# Check if frontend is accessible
FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}/shadbala" 2>&1)

if [ "$FRONTEND_CHECK" = "200" ]; then
    echo "✅ Frontend /shadbala page accessible"
else
    echo "⚠️  Frontend not accessible (HTTP $FRONTEND_CHECK)"
    echo "   This is expected if frontend is not running locally"
fi

echo ""
echo "✅ VERIFICATION COMPLETE"
echo ""
echo "📋 Manual UI Checklist:"
echo "   [ ] Navigate to /shadbala page"
echo "   [ ] 'Calculation Mode: PURE BPHS' visible"
echo "   [ ] All 7 planets rendered"
echo "   [ ] Status badges visible for all planets"
echo "   [ ] Tooltips work on hover/touch"
echo "   [ ] Transparency note visible"
echo "   [ ] Values match API response"
echo ""
echo "🔗 Test API directly:"
echo "   curl '${API_URL}/strength/shadbala?dob=${TEST_DOB}&time=${TEST_TIME}&lat=${TEST_LAT}&lon=${TEST_LON}' | jq '.shadbala.Sun.status'"
echo ""
