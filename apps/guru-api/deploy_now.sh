#!/bin/bash
# Complete deployment script - installs gcloud and deploys

set -e

PROJECT_ID="guru-api-6b9ba"
REGION="asia-south1"  # CANONICAL REGION - DO NOT CHANGE
SERVICE_NAME="guru-api"

# REGION LOCK: Fail if region is not asia-south1
if [ "$REGION" != "asia-south1" ]; then
    echo "❌ ERROR: Deployment region must be 'asia-south1'"
    echo "   Current region: $REGION"
    exit 1
fi

echo "🚀 GURU API - COMPLETE DEPLOYMENT"
echo "=================================="
echo ""

# Check if gcloud exists
if ! command -v gcloud &> /dev/null; then
    echo "📦 Installing gcloud CLI..."
    
    # Try to find existing installation
    if [ -d "$HOME/google-cloud-sdk" ]; then
        export PATH="$HOME/google-cloud-sdk/bin:$PATH"
    elif [ -d "./google-cloud-sdk" ]; then
        export PATH="$(pwd)/google-cloud-sdk/bin:$PATH"
    else
        echo "Downloading Google Cloud SDK..."
        curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-darwin-arm64.tar.gz
        tar -xzf google-cloud-cli-darwin-arm64.tar.gz
        export PATH="$(pwd)/google-cloud-sdk/bin:$PATH"
    fi
fi

# Verify gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud installation failed"
    echo "Please install manually: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud found: $(gcloud --version | head -1)"
echo ""

# Initialize gcloud if needed
if ! gcloud config get-value project &>/dev/null; then
    echo "🔧 Initializing gcloud..."
    gcloud init --skip-diagnostics || true
fi

# Authenticate
echo "🔐 Checking authentication..."
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
if [ -z "$ACCOUNT" ]; then
    echo "Please authenticate in the browser that opens..."
    gcloud auth login --no-launch-browser || gcloud auth login
else
    echo "✅ Authenticated as: $ACCOUNT"
fi
echo ""

# Set project
echo "📋 Setting project to $PROJECT_ID..."
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
echo "✅ DEPLOYMENT COMPLETE!"
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
