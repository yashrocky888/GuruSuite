# 🚀 Firebase Cloud Run Deployment Guide

## Prerequisites

1. Google Cloud Account
2. Firebase Project created
3. `gcloud` CLI installed and authenticated
4. Firebase Admin SDK credentials JSON file

## Step 1: Setup Firebase Project

### 1.1 Create Firebase Project

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable firestore.googleapis.com
```

### 1.2 Initialize Firestore

```bash
# Create Firestore database (if not exists)
gcloud firestore databases create --location=us-central
```

### 1.3 Create Firestore Collection Structure

The API will automatically create the `api_keys` collection, but you can pre-create it:

```bash
# Using Firebase Console:
# 1. Go to Firebase Console → Firestore Database
# 2. Create collection: `api_keys`
# 3. Add a test document (optional)
```

## Step 2: Get Firebase Admin Credentials

### 2.1 Download Service Account Key

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save the JSON file as `firebase-service-account.json`
4. **Keep this file secure!**

### 2.2 Set Environment Variable

```bash
export GOOGLE_APPLICATION_CREDENTIALS="./firebase-service-account.json"
```

## Step 3: Configure Environment Variables

Create `.env` file:

```bash
# Firebase
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json

# Master Admin Key (for creating API keys)
MASTER_ADMIN_KEY=your-super-secret-master-key-change-this

# Deployment
DEPLOYMENT_ENV=production
LOG_LEVEL=INFO

# API Configuration
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_DAY=1000

# Fallback API Keys (if Firebase unavailable)
API_KEYS=fallback-key-1,fallback-key-2
```

## Step 4: Build and Deploy to Cloud Run

### 4.1 Build Docker Image

```bash
# Build the image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/guru-api

# Or build locally first
docker build -t gcr.io/YOUR_PROJECT_ID/guru-api .
docker push gcr.io/YOUR_PROJECT_ID/guru-api
```

### 4.2 Deploy to Cloud Run

```bash
gcloud run deploy guru-api \
  --image gcr.io/YOUR_PROJECT_ID/guru-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO" \
  --set-secrets "GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials:latest,MASTER_ADMIN_KEY=master-key:latest"
```

### 4.3 Deploy with Secrets (Recommended)

```bash
# Create secrets in Secret Manager
echo -n "$(cat firebase-service-account.json)" | gcloud secrets create firebase-credentials --data-file=-
echo -n "your-master-admin-key" | gcloud secrets create master-key --data-file=-

# Deploy with secrets
gcloud run deploy guru-api \
  --image gcr.io/YOUR_PROJECT_ID/guru-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --set-secrets "GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials:latest,MASTER_ADMIN_KEY=master-key:latest" \
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO,RATE_LIMIT_PER_MINUTE=60,RATE_LIMIT_PER_DAY=1000"
```

### 4.4 Get Deployment URL

```bash
# Get the service URL
gcloud run services describe guru-api --region us-central1 --format 'value(status.url)'
```

## Step 5: Create Your First API Key

### 5.1 Using Admin Endpoint

```bash
# Set your master admin key
export MASTER_KEY="your-master-admin-key"

# Create API key
curl -X POST https://YOUR_SERVICE_URL/api/admin/create-key \
  -H "x-master-admin-key: $MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Key",
    "description": "Main production API key"
  }'
```

Response:
```json
{
  "success": true,
  "api_key": "your-generated-64-char-key",
  "name": "Production Key",
  "message": "API key created successfully. Save this key securely - it won't be shown again."
}
```

**⚠️ IMPORTANT: Save the API key immediately - it won't be shown again!**

### 5.2 List All Keys

```bash
curl -X GET https://YOUR_SERVICE_URL/api/admin/list-keys \
  -H "x-master-admin-key: $MASTER_KEY"
```

### 5.3 Deactivate a Key

```bash
curl -X POST https://YOUR_SERVICE_URL/api/admin/deactivate-key/KEY_ID \
  -H "x-master-admin-key: $MASTER_KEY"
```

## Step 6: Test the API

### 6.1 Health Check

```bash
curl https://YOUR_SERVICE_URL/api/health
```

### 6.2 Test with API Key

```bash
export API_KEY="your-generated-api-key"

curl -X POST https://YOUR_SERVICE_URL/api/kundali/full \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-15",
    "birth_time": "10:30",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }'
```

## Step 7: Update Deployment

### 7.1 Rebuild and Redeploy

```bash
# Rebuild
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/guru-api

# Redeploy
gcloud run deploy guru-api \
  --image gcr.io/YOUR_PROJECT_ID/guru-api \
  --platform managed \
  --region us-central1
```

### 7.2 Rollback

```bash
# List revisions
gcloud run revisions list --service guru-api --region us-central1

# Rollback to previous revision
gcloud run services update-traffic guru-api \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Firebase service account JSON | Yes |
| `MASTER_ADMIN_KEY` | Master key for admin endpoints | Yes |
| `DEPLOYMENT_ENV` | Environment (production/development) | No |
| `LOG_LEVEL` | Logging level (INFO/DEBUG/ERROR) | No |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per minute | No |
| `RATE_LIMIT_PER_DAY` | Rate limit per day | No |
| `API_KEYS` | Fallback API keys (comma-separated) | No |

## Security Best Practices

1. **Never commit credentials** - Use Secret Manager
2. **Rotate master admin key** regularly
3. **Use strong master admin key** (64+ characters)
4. **Monitor API key usage** via Firestore
5. **Deactivate unused keys** immediately
6. **Enable Cloud Run authentication** for admin endpoints (optional)
7. **Use HTTPS only** (Cloud Run provides this)
8. **Set up Cloud Monitoring** alerts

## Monitoring

### View Logs

```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=guru-api" --limit 50

# Real-time logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=guru-api"
```

### Monitor API Key Usage

```bash
# Query Firestore for key usage
gcloud firestore query --collection=api_keys --order-by=usage_count --limit=10
```

## Troubleshooting

### Firebase Not Initialized

```bash
# Check credentials file
ls -la firebase-service-account.json

# Verify credentials
gcloud auth application-default login
```

### API Key Not Working

1. Check Firestore collection exists
2. Verify key is active in Firestore
3. Check cache (wait 5 minutes or restart service)
4. Verify `x-api-key` header name (case-sensitive)

### Deployment Fails

```bash
# Check build logs
gcloud builds list --limit=5

# View build details
gcloud builds describe BUILD_ID
```

## Cost Optimization

- **Min instances**: 0 (scale to zero)
- **Max instances**: 10 (adjust based on traffic)
- **Memory**: 2Gi (adjust based on usage)
- **CPU**: 2 (adjust based on load)
- **Timeout**: 300s (5 minutes)

## Next Steps

1. Set up custom domain (optional)
2. Configure Cloud CDN for caching
3. Set up Cloud Monitoring alerts
4. Configure auto-scaling policies
5. Set up CI/CD pipeline

---

## Quick Deploy Script

Save as `deploy-firebase.sh`:

```bash
#!/bin/bash
PROJECT_ID="YOUR_PROJECT_ID"
REGION="us-central1"

echo "Building image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/guru-api

echo "Deploying to Cloud Run..."
gcloud run deploy guru-api \
  --image gcr.io/$PROJECT_ID/guru-api \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --set-secrets "GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials:latest,MASTER_ADMIN_KEY=master-key:latest" \
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO"

echo "Deployment complete!"
gcloud run services describe guru-api --region $REGION --format 'value(status.url)'
```

Make executable and run:
```bash
chmod +x deploy-firebase.sh
./deploy-firebase.sh
```

