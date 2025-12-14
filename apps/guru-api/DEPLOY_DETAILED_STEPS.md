# 🚀 DETAILED DEPLOYMENT STEPS

## Option 1: Deploy from Cloud Console (Step-by-Step)

### Step 1: Click "Edit & deploy new revision"
- In your Cloud Console, click the blue button "Edit & deploy new revision"
- This opens the deployment wizard

### Step 2: Choose "Deploy from source"
- In the wizard, you'll see tabs: "Container", "Source", "YAML"
- Click "Source" tab
- Select "Cloud Source Repositories" or "Upload code"

### Step 3: If uploading code:
- Click "Browse" or drag & drop
- Upload the entire Guru_API folder
- Make sure it includes:
  - src/jyotish/kundli_engine.py (with house lords)
  - guru_api.py (fixed)
  - Dockerfile
  - requirements.txt

### Step 4: Configure build
- Build type: Dockerfile
- Dockerfile path: ./Dockerfile
- Region: us-central1
- Service name: guru-api

### Step 5: Deploy
- Click "Deploy" button
- Wait 5-10 minutes for build and deployment
- You'll see "Deployment successful"

## Option 2: Deploy from Terminal (I'll do this)

Let me install gcloud and deploy for you...
