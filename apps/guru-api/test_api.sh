#!/bin/bash
# Quick API Test Script

echo "🧪 Testing Guru API"
echo "==================="
echo ""

# Get API key from .env
API_KEY=$(grep "API_KEYS=" .env | cut -d'=' -f2 | cut -d',' -f1)

if [ -z "$API_KEY" ]; then
    echo "❌ API key not found in .env"
    exit 1
fi

echo "✅ Using API key: ${API_KEY:0:20}..."
echo ""

# Test 1: Health Check
echo "1️⃣ Testing Health Endpoint..."
HEALTH=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Health check passed"
    echo "   Response: $HEALTH"
else
    echo "   ❌ Health check failed"
    echo "   Response: $HEALTH"
fi
echo ""

# Test 2: Kundali Endpoint
echo "2️⃣ Testing Kundali Endpoint..."
KUNDALI_RESPONSE=$(curl -s -X POST http://localhost:8000/api/kundali/full \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-15",
    "birth_time": "10:30",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }')

if echo "$KUNDALI_RESPONSE" | grep -q "success"; then
    echo "   ✅ Kundali endpoint working"
    echo "   Response preview: $(echo "$KUNDALI_RESPONSE" | head -c 200)..."
else
    echo "   ⚠️  Kundali endpoint response:"
    echo "   $KUNDALI_RESPONSE" | head -c 500
fi
echo ""

echo "✅ Testing complete!"
echo ""
echo "📖 Full API documentation: http://localhost:8000/docs"
