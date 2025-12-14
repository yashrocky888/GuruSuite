#!/bin/bash
# Final deployment with correct project detection

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

echo "🚀 GURU API - DEPLOYMENT"
echo "========================"
echo ""

# Try to detect project from URL
PROJECT_NUM="660206747784"
REGION="asia-south1"  # CANONICAL REGION - DO NOT CHANGE
SERVICE_NAME="guru-api"

# REGION LOCK: Fail if region is not asia-south1
if [ "$REGION" != "asia-south1" ]; then
    echo "❌ ERROR: Deployment region must be 'asia-south1'"
    echo "   Current region: $REGION"
    exit 1
fi

# Try to get project ID from project number
PROJECT_ID=$(gcloud projects list --filter="projectNumber=$PROJECT_NUM" --format="value(projectId)" 2>/dev/null | head -1)

if [ -z "$PROJECT_ID" ]; then
    echo "📋 Available projects:"
    gcloud projects list --format="table(projectId,projectNumber)" 2>&1 | head -10
    echo ""
    read -p "Enter your project ID: " PROJECT_ID
else
    echo "✅ Detected project: $PROJECT_ID"
fi

# Set project
echo "📋 Setting project..."
gcloud config set project "$PROJECT_ID"
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
echo "✅ All changes are now live!"
echo ""
