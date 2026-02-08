#!/bin/bash
# Shadbala Final Deployment Script
# Deploys updated Shadbala API with status + ratio fields

set -e

echo "🚀 SHADBALA FINAL DEPLOYMENT"
echo "============================"
echo ""

# Check if we're in the right directory
if [ ! -f "src/jyotish/strength/shadbala.py" ]; then
    echo "❌ Error: Must run from apps/guru-api directory"
    exit 1
fi

echo "✅ Step 1: Verifying SHADBALA_CONFIG..."
python3 -c "
from src.jyotish.strength.shadbala import SHADBALA_CONFIG
assert SHADBALA_CONFIG['KENDRADI_SCALE'] == 1.0
assert SHADBALA_CONFIG['DIGBALA_SUN_MULTIPLIER'] == 1.0
assert SHADBALA_CONFIG['SAPTAVARGAJA_DIVISOR'] == 1.0
print('✅ SHADBALA_CONFIG locked to PURE BPHS (1.0 / 1.0 / 1.0)')
"

echo ""
echo "✅ Step 2: Verifying status function..."
python3 -c "
from src.jyotish.strength.shadbala import calculate_bphs_status
assert calculate_bphs_status(1.25) == 'Very Strong'
assert calculate_bphs_status(1.10) == 'Strong'
assert calculate_bphs_status(0.90) == 'Average'
assert calculate_bphs_status(0.80) == 'Weak'
print('✅ Status calculation verified')
"

echo ""
echo "🔄 Step 3: Restarting backend service..."

# Check if running via Docker
if docker ps | grep -q guru-api; then
    echo "   Detected Docker deployment"
    docker-compose restart guru-api
    echo "   ✅ Backend service restarted (Docker)"
elif pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "   Detected direct Python deployment"
    pkill -f "uvicorn.*main:app"
    sleep 2
    echo "   ⚠️  Backend stopped. Please restart manually:"
    echo "      python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000"
else
    echo "   ⚠️  No running backend detected"
    echo "   Start backend with:"
    echo "      python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000"
fi

echo ""
echo "✅ Step 4: Backend deployment complete"
echo ""
echo "📋 Next Steps:"
echo "   1. Rebuild frontend: cd ../guru-web/guru-web && npm run build"
echo "   2. Deploy frontend to your hosting service"
echo "   3. Clear CDN/cache if applicable"
echo "   4. Verify live UI at /shadbala page"
echo ""
echo "🧪 Test API endpoint:"
echo "   curl 'http://localhost:8000/strength/shadbala?dob=2006-02-03&time=22:30&lat=12.9716&lon=77.5946' | jq '.shadbala.Sun.status'"
echo ""
echo "✅ Shadbala backend ready for deployment"
