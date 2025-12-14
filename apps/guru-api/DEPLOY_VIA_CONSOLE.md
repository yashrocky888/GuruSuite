# 🚀 Deploy Changes via Google Cloud Console

## Quick Steps to Deploy

Since your service is already in the Cloud Console, you can deploy directly:

### Method 1: Deploy from Source (Easiest)
1. In the Cloud Console, click **"Edit & deploy new revision"** button
2. Select **"Deploy from source"** tab
3. Choose your source repository or upload the code
4. Click **"Deploy"**

### Method 2: Deploy from Container Image
1. Click **"Edit & deploy new revision"**
2. Go to **"Container"** tab
3. Build the image first (or use existing)
4. Deploy

### Method 3: Use Cloud Build (Recommended)
Since you're already in the console, you can trigger a build:

1. Go to **Cloud Build** → **Triggers**
2. Create a new trigger or use existing
3. Or manually build:
   - Go to **Cloud Build** → **History**
   - Click **"Create Build"**
   - Use this configuration:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/guru-api-660206747784/guru-api', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/guru-api-660206747784/guru-api']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'guru-api'
      - '--image'
      - 'gcr.io/guru-api-660206747784/guru-api'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
```

## What Changed
- ✅ House lords (no more "Unknown")
- ✅ Sanskrit names for all signs
- ✅ Fixed interpretation engine

## After Deployment
Test at: https://guru-api-660206747784.us-central1.run.app

