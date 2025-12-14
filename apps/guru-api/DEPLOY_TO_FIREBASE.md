# 🚀 Deploy to Firebase Cloud Run

## Current Status
- ✅ **Service Already Deployed:** https://guru-api-660206747784.us-central1.run.app
- ✅ **Changes Ready:** House lords and Sanskrit names fixed
- ⚠️ **Need to Deploy:** Changes are local only

## Quick Deploy Options

### Option 1: Install gcloud and Deploy (Recommended)
```bash
# Install gcloud (Mac)
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project guru-api-660206747784

# Deploy
./DEPLOY_FINAL.sh
```

### Option 2: Use Google Cloud Console
1. Go to: https://console.cloud.google.com/run/detail/us-central1/guru-api
2. Click "Edit & Deploy New Revision"
3. Click "Deploy from source" or upload the Dockerfile
4. Build and deploy

### Option 3: Use Cloud Build API (if you have API access)
```bash
# Build
gcloud builds submit --tag gcr.io/guru-api-660206747784/guru-api

# Deploy
gcloud run deploy guru-api \
  --image gcr.io/guru-api-660206747784/guru-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## What Will Be Deployed
- ✅ House lords (no more "Unknown")
- ✅ Sanskrit names for all signs
- ✅ Fixed interpretation engine

## After Deployment
Test the API:
```bash
curl -X POST https://guru-api-660206747784.us-central1.run.app/api/kundali/full \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1995-05-16",
    "birth_time": "18:38",
    "birth_latitude": 12.9629,
    "birth_longitude": 77.5775,
    "timezone": "Asia/Kolkata"
  }'
```

Check that response has:
- `"lord": "Sun"` (not "Unknown") in houses
- `"sign_sanskrit": "Simha"` in all signs

