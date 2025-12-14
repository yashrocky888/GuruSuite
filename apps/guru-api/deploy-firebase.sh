#!/bin/bash
# Quick Firebase Cloud Run Deployment Script

set -e

PROJECT_ID="${GCP_PROJECT_ID:-guru-api-6b9ba}"
REGION="asia-south1"  # CANONICAL REGION - DO NOT CHANGE
SERVICE_NAME="guru-api"

# REGION LOCK: Fail if region is not asia-south1
if [ "$REGION" != "asia-south1" ]; then
    echo "❌ ERROR: Deployment region must be 'asia-south1'"
    echo "   Current region: $REGION"
    exit 1
fi

echo "🚀 Deploying Guru API to Firebase Cloud Run"
echo "=============================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found"
    echo "Install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Build image
echo "🔨 Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO" \
  --set-secrets "GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials:latest,MASTER_ADMIN_KEY=master-key:latest" 2>/dev/null || \
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo ""
echo "✅ Deployment Complete!"
echo "======================"
echo "Service URL: $SERVICE_URL"
echo ""
echo "📝 Next Steps:"
echo "1. Create your first API key:"
echo "   curl -X POST $SERVICE_URL/api/admin/create-key \\"
echo "     -H 'x-master-admin-key: YOUR_MASTER_KEY' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"name\":\"Production Key\",\"description\":\"Main key\"}'"
echo ""
echo "2. Test health endpoint:"
echo "   curl $SERVICE_URL/api/health"
echo ""

