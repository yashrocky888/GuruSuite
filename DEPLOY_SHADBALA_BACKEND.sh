#!/bin/bash
# Shadbala Backend Deployment Script (Cloud Run)
# Run this script to deploy updated Shadbala API

set -e

echo "🚀 SHADBALA BACKEND DEPLOYMENT"
echo "=============================="
echo ""

cd "$(dirname "$0")/apps/guru-api"

# Verify code
echo "✅ Step 1: Verifying code..."
python3 -c "
from src.jyotish.strength.shadbala import SHADBALA_CONFIG, calculate_bphs_status
assert SHADBALA_CONFIG['KENDRADI_SCALE'] == 1.0
assert SHADBALA_CONFIG['DIGBALA_SUN_MULTIPLIER'] == 1.0
assert SHADBALA_CONFIG['SAPTAVARGAJA_DIVISOR'] == 1.0
assert calculate_bphs_status(1.25) == 'Very Strong'
print('✅ Code verified: PURE BPHS')
"

echo ""
echo "🔄 Step 2: Deploying to Cloud Run..."
echo ""

# Deploy to Cloud Run
gcloud run deploy guru-api \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated

echo ""
echo "✅ Backend deployment complete!"
echo ""
echo "📡 Backend URL: https://guru-api-660206747784.asia-south1.run.app"
echo ""
echo "🧪 Test API:"
echo "curl 'https://guru-api-660206747784.asia-south1.run.app/strength/shadbala?dob=2006-02-03&time=22:30&lat=12.9716&lon=77.5946' | jq '.shadbala.Sun.status'"
echo ""
