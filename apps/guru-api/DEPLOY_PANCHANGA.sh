#!/bin/bash
# Deploy Panchanga Engine to Cloud Run
# This script deploys the latest Drik Panchang-compliant Panchanga engine

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

PROJECT_ID="guru-api-6b9ba"
REGION="asia-south1"  # CANONICAL REGION - DO NOT CHANGE
SERVICE_NAME="guru-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# REGION LOCK: Fail if region is not asia-south1
if [ "$REGION" != "asia-south1" ]; then
    echo "❌ ERROR: Deployment region must be 'asia-south1'"
    exit 1
fi

echo "🚀 Deploying Panchanga Engine to Cloud Run"
echo "=============================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Set project
echo "📋 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Build Docker image
echo "🔨 Building Docker image..."
echo "This may take 5-10 minutes..."
gcloud builds submit --tag ${IMAGE_NAME} --project ${PROJECT_ID}

# Deploy to Cloud Run
echo ""
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO" \
  --project ${PROJECT_ID}

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID} --format 'value(status.url)')
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""

# Test Panchanga endpoint
echo "🧪 Testing Panchanga endpoint..."
curl -s "${SERVICE_URL}/api/v1/panchanga?date=2026-01-22&lat=12.9716&lon=77.5946&tz=Asia/Kolkata" | python3 -m json.tool | head -50

echo ""
echo "✅ Verify:"
echo "  - Sunrise should be 06:46 (not 06:00)"
echo "  - Tithi should have 'current' and 'next' structure"
echo "  - Karana should be an array"
echo "  - Lunar months should be present"
echo ""
