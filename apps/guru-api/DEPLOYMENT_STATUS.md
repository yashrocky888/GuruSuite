# Deployment Status - D10 Fix

## ✅ Changes Committed Locally

**Commit:** `1ff5bb9 - Fix D10 (Dasamsa) calculation to match Prokerala exactly`

**Files Changed:**
- `apps/guru-api/src/jyotish/varga_drik.py` - D10 calculation fix
- `apps/guru-api/tests/test_d10_golden.py` - Golden tests (new)
- `apps/guru-api/tests/test_varga_accuracy.py` - Updated test
- `apps/guru-api/TEST_D10.md` - Testing guide (new)

## 📤 GitHub Push - Pending

**Status:** Requires authentication

**To Push:**

### Option 1: GitHub CLI
```bash
cd /Users/yashm/GuruSuite
gh auth login
git push origin main
```

### Option 2: SSH
```bash
cd /Users/yashm/GuruSuite
# First configure SSH key in GitHub settings
git remote set-url origin git@github.com:yashrocky888/GuruSuite.git
git push origin main
```

### Option 3: Personal Access Token
```bash
cd /Users/yashm/GuruSuite
git remote set-url origin https://YOUR_TOKEN@github.com/yashrocky888/GuruSuite.git
git push origin main
# Then reset: git remote set-url origin https://github.com/yashrocky888/GuruSuite.git
```

### Option 4: GitHub Desktop
- Open GitHub Desktop
- Click "Push origin" button

## 🚀 API Deployment - Pending

**Status:** Requires gcloud CLI setup

### Prerequisites

1. **Install Google Cloud SDK:**
   ```bash
   # Mac with Homebrew
   brew install google-cloud-sdk
   
   # OR download from:
   # https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate:**
   ```bash
   gcloud auth login
   ```

3. **Set Project:**
   ```bash
   gcloud config set project guru-api-660206747784
   ```

### Deploy

**Option 1: Use Deployment Script**
```bash
cd /Users/yashm/GuruSuite/apps/guru-api
./DEPLOY_TERMINAL.sh
```

**Option 2: Manual Deploy**
```bash
cd /Users/yashm/GuruSuite/apps/guru-api

# Build Docker image
gcloud builds submit --tag gcr.io/guru-api-660206747784/guru-api

# Deploy to Cloud Run
gcloud run deploy guru-api \
  --image gcr.io/guru-api-660206747784/guru-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO"
```

**Option 3: Google Cloud Console**
1. Go to: https://console.cloud.google.com
2. Navigate to: Cloud Run → guru-api
3. Click "Edit & Deploy New Revision"
4. Upload new container or build from source

## ✅ Verification After Deployment

### Test D10 Endpoint
```bash
# Replace SERVICE_URL with your deployed URL
curl "SERVICE_URL/api/v1/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata" | jq '.D10'
```

### Expected Results
- **Ascendant:** Cancer (Karka) - sign 4, house 4
- **Venus:** Aquarius (Kumbha) - sign 11, house 11
- **Mars:** Pisces (Meena) - sign 12, house 12
- **All planets:** Should match Prokerala exactly

## 📋 Current Status

- ✅ Code changes: Committed locally
- ⏳ GitHub push: Pending (needs authentication)
- ⏳ API deployment: Pending (needs gcloud setup)

## 🔧 Troubleshooting

### GitHub Push Issues
- **Authentication failed:** Use `gh auth login` or configure SSH keys
- **Permission denied:** Check repository access permissions
- **Token expired:** Generate new Personal Access Token

### Deployment Issues
- **gcloud not found:** Install Google Cloud SDK
- **Authentication failed:** Run `gcloud auth login`
- **Project not found:** Verify project ID: `guru-api-660206747784`
- **Build failed:** Check Dockerfile and dependencies
- **Deploy failed:** Check Cloud Run permissions and quotas

## 📞 Next Steps

1. **Push to GitHub** using one of the methods above
2. **Set up gcloud** if not already installed
3. **Deploy API** using deployment script or manual commands
4. **Verify** D10 results match Prokerala
5. **Test in UI** to confirm D10 chart displays correctly

