#!/bin/bash
# Terminal Deployment Script - Detailed Steps

set -e

echo "🚀 GURU API - TERMINAL DEPLOYMENT"
echo "=================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found"
    echo ""
    echo "📋 INSTALL GCLOUD:"
    echo "------------------"
    echo "Option 1 (Mac with Homebrew):"
    echo "  brew install google-cloud-sdk"
    echo ""
    echo "Option 2 (Manual):"
    echo "  Download from: https://cloud.google.com/sdk/docs/install"
    echo "  Then run this script again"
    echo ""
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Set project
PROJECT_ID="guru-api-6b9ba"
REGION="asia-south1"  # CANONICAL REGION - DO NOT CHANGE
SERVICE_NAME="guru-api"

# REGION LOCK: Fail if region is not asia-south1
if [ "$REGION" != "asia-south1" ]; then
    echo "❌ ERROR: Deployment region must be 'asia-south1'"
    echo "   Current region: $REGION"
    echo "   This is a safety check to prevent accidental deployments to wrong region"
    exit 1
fi

echo "📋 Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo ""

# Check authentication
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
if [ -z "$ACCOUNT" ]; then
    echo "🔐 Authenticating..."
    gcloud auth login
else
    echo "✅ Authenticated as: $ACCOUNT"
fi
echo ""

# Set project
echo "📋 Setting project..."
gcloud config set project $PROJECT_ID
echo "✅ Project set"
echo ""

# Build Docker image
echo "🔨 Building Docker image..."
echo "This may take 5-10 minutes..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
echo "✅ Build complete"
echo ""

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
  --quiet

echo ""
echo "✅ Deployment complete!"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' 2>/dev/null)
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "🧪 Test the deployment:"
echo "  curl $SERVICE_URL/api/health"
echo ""
echo "✅ All changes are now live!"
echo "   - House lords (no more 'Unknown')"
echo "   - Sanskrit names for all signs"
echo "   - Fixed interpretation engine"
echo ""

