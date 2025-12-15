# Deploy D10 Fix - Quick Guide

## Changes Committed
✅ D10 calculation fix committed locally
- Fixed D10 formula in `varga_drik.py`
- Added golden tests (`test_d10_golden.py`)
- Added testing guide (`TEST_D10.md`)
- Updated test accuracy file

**Commit:** `1ff5bb9 - Fix D10 (Dasamsa) calculation to match Prokerala exactly`

---

## Step 1: Push to GitHub

### Option A: Using GitHub CLI (Recommended)
```bash
cd /Users/yashm/GuruSuite
gh auth login
git push origin main
```

### Option B: Using SSH
```bash
cd /Users/yashm/GuruSuite
git remote set-url origin git@github.com:yashrocky888/GuruSuite.git
git push origin main
```

### Option C: Using Personal Access Token
```bash
cd /Users/yashm/GuruSuite
# Replace YOUR_TOKEN with your GitHub Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/yashrocky888/GuruSuite.git
git push origin main
# Then reset to HTTPS:
git remote set-url origin https://github.com/yashrocky888/GuruSuite.git
```

---

## Step 2: Deploy API to Google Cloud

### Quick Deploy
```bash
cd /Users/yashm/GuruSuite/apps/guru-api
./DEPLOY_TERMINAL.sh
```

### Or Manual Deploy
```bash
cd /Users/yashm/GuruSuite/apps/guru-api

# Set project (if not already set)
export GCP_PROJECT_ID="guru-api-660206747784"
gcloud config set project $GCP_PROJECT_ID

# Build and deploy
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/guru-api
gcloud run deploy guru-api \
  --image gcr.io/$GCP_PROJECT_ID/guru-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO"

# Get service URL
gcloud run services describe guru-api --region us-central1 --format 'value(status.url)'
```

---

## Step 3: Verify Deployment

### Test D10 Endpoint
```bash
# Replace SERVICE_URL with your deployed URL
curl "SERVICE_URL/api/v1/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata" | jq '.D10'
```

### Expected Results
- **Ascendant:** Cancer (Karka) - sign 4
- **Venus:** Aquarius (Kumbha) - sign 11
- **Mars:** Pisces (Meena) - sign 12

---

## Current Status

✅ **Local Changes:** Committed (1 commit ahead)
⏳ **GitHub:** Needs push (authentication required)
⏳ **Deployment:** Ready to deploy (gcloud authentication required)

---

## Troubleshooting

### GitHub Push Issues
- If authentication fails, use GitHub CLI: `gh auth login`
- Or use SSH keys if configured
- Or push via GitHub Desktop

### Deployment Issues
- Ensure `gcloud` is installed: `gcloud --version`
- Authenticate: `gcloud auth login`
- Set project: `gcloud config set project guru-api-660206747784`
- Check billing is enabled for the project

