# 🚀 DETAILED CLOUD CONSOLE DEPLOYMENT STEPS

## You're Already in the Console - Follow These Steps:

### STEP 1: Click "Edit & deploy new revision"
- In your Cloud Console screenshot, you can see this button
- Click it to start the deployment wizard

### STEP 2: Choose Deployment Method

**Option A: Deploy from Source Repository (Recommended)**
1. In the wizard, click the **"Source"** tab
2. You'll see options:
   - "Cloud Source Repositories" (if you have code in a repo)
   - "Upload code" (to upload directly)

**Option B: Deploy from Container Image**
1. Click the **"Container"** tab
2. Enter: `gcr.io/guru-api-660206747784/guru-api:latest`
3. Or build new image first

### STEP 3: If Uploading Code
1. Click **"Browse"** or drag & drop
2. Upload a ZIP file of your Guru_API folder containing:
   ```
   Guru_API/
   ├── src/
   │   └── jyotish/
   │       └── kundli_engine.py (✅ with house lords)
   ├── guru_api.py (✅ fixed)
   ├── Dockerfile
   ├── requirements.txt
   └── api/
       └── main.py
   ```

### STEP 4: Configure Build Settings
- **Build type:** Dockerfile
- **Dockerfile path:** `./Dockerfile`
- **Region:** `us-central1`
- **Service name:** `guru-api`
- **Memory:** 2Gi
- **CPU:** 2
- **Timeout:** 300 seconds
- **Max instances:** 10

### STEP 5: Environment Variables
Add these if not already set:
- `DEPLOYMENT_ENV=production`
- `LOG_LEVEL=INFO`

### STEP 6: Deploy!
1. Click the **"Deploy"** button
2. Wait 5-10 minutes for:
   - Code upload
   - Docker image build
   - Container deployment
3. You'll see "Deployment successful" when done

### STEP 7: Verify
After deployment, test:
```
https://guru-api-660206747784.us-central1.run.app/api/health
```

## What Changed (Will Be Deployed):
✅ House lords (no more "Unknown")
✅ Sanskrit names for all signs (Mesha, Vrishabha, etc.)
✅ Fixed interpretation engine

## Quick Checklist:
- [ ] Click "Edit & deploy new revision"
- [ ] Choose "Source" tab
- [ ] Upload code or connect repository
- [ ] Configure settings
- [ ] Click "Deploy"
- [ ] Wait for completion
- [ ] Test the API

---

**Need to create a ZIP file?**
```bash
cd /Users/yashm/Guru_API
zip -r deploy.zip . -x "*.git*" -x "venv/*" -x "__pycache__/*" -x "*.pyc"
```

Then upload `deploy.zip` in the Cloud Console!

