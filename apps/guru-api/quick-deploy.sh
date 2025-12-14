#!/bin/bash
# Quick deployment script with gcloud setup

# Setup gcloud
export CLOUDSDK_PYTHON=$(which python3)
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"

# Check if gcloud is available
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud not found. Please install: brew install google-cloud-sdk"
    exit 1
fi

# Get project ID
if [ -z "$GCP_PROJECT_ID" ]; then
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$CURRENT_PROJECT" ]; then
        echo "⚠️  No GCP project set"
        echo "Set it with: export GCP_PROJECT_ID='your-project-id'"
        echo "Or: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    else
        GCP_PROJECT_ID=$CURRENT_PROJECT
        echo "✅ Using project: $GCP_PROJECT_ID"
    fi
else
    echo "✅ Using project: $GCP_PROJECT_ID"
    gcloud config set project $GCP_PROJECT_ID
fi

# Check authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "⚠️  Not authenticated. Running: gcloud auth login"
    gcloud auth login
fi

# Enable APIs
echo "📋 Enabling required APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com --quiet

# Check Firestore
echo "📋 Checking Firestore..."
if ! gcloud firestore databases list --format="value(name)" 2>/dev/null | grep -q .; then
    echo "⚠️  Firestore not found. Creating..."
    gcloud firestore databases create --location=us-central1 --quiet
fi

# Build and deploy
echo "🔨 Building Docker image..."
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/guru-api --quiet

# REGION LOCK: asia-south1 is canonical
REGION="asia-south1"  # CANONICAL REGION - DO NOT CHANGE

# REGION LOCK: Fail if region is not asia-south1
if [ "$REGION" != "asia-south1" ]; then
    echo "❌ ERROR: Deployment region must be 'asia-south1'"
    exit 1
fi

echo "☁️  Deploying to Cloud Run..."
gcloud run deploy guru-api \
  --image gcr.io/$GCP_PROJECT_ID/guru-api \
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

# Get URL
SERVICE_URL=$(gcloud run services describe guru-api --region $REGION --format 'value(status.url)' 2>/dev/null)

echo ""
echo "✅ Deployment Complete!"
echo "======================"
echo "Service URL: $SERVICE_URL"
echo ""
echo "📝 Next: Create your first API key"
echo "See DEPLOY_NOW.md for instructions"
