# Cloud Run Region Lock - Canonical Service

## 🎯 CANONICAL SERVICE

**ONLY ONE Cloud Run service exists and must be used:**

- **Service Name:** `guru-api`
- **Region:** `asia-south1` ✅ **CANONICAL**
- **Project:** `guru-api-6b9ba`
- **Service URL:** `https://guru-api-660206747784.asia-south1.run.app`
- **Status:** Production (Active)

## ❌ INVALID REGIONS

**DO NOT deploy to these regions:**
- ❌ `us-central1` - **DELETED** (was accidentally created)
- ❌ `us-central11` - Invalid region
- ❌ Any other region

## 🔒 REGION LOCK ENFORCEMENT

All deployment scripts have been updated with **hard region validation**:

```bash
# REGION LOCK: Fail if region is not asia-south1
if [ "$REGION" != "asia-south1" ]; then
    echo "❌ ERROR: Deployment region must be 'asia-south1'"
    exit 1
fi
```

**Files with region lock:**
- ✅ `DEPLOY_TERMINAL.sh`
- ✅ `deploy_now.sh`
- ✅ `DEPLOY_JHORA.sh`
- ✅ `DEPLOY_FINAL.sh`
- ✅ `quick-deploy.sh`
- ✅ `deploy-firebase.sh`

## 📋 WHY asia-south1?

1. **Original Production Service:** This was the first and intended production deployment
2. **Geographic Location:** Closer to target users (India/Asia)
3. **Consistency:** All documentation and frontend configs point to this region
4. **Stability:** Established service with proper configuration

## 🚀 DEPLOYMENT COMMAND (FOREVER)

**Use this exact command for ALL future deployments:**

```bash
cd apps/guru-api
export PATH="/Users/yashm/google-cloud-sdk/bin:$PATH"
PROJECT_ID="guru-api-6b9ba"
REGION="asia-south1"  # CANONICAL - DO NOT CHANGE
SERVICE_NAME="guru-api"

# Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy
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
  --set-env-vars "DEPLOYMENT_ENV=production,LOG_LEVEL=INFO"
```

**Or use the deployment script:**
```bash
cd apps/guru-api
./DEPLOY_TERMINAL.sh
```

## 🔍 VERIFICATION

### Check Service Status
```bash
gcloud run services list --platform managed
```

**Expected Output:**
```
SERVICE   REGION       URL
guru-api  asia-south1  https://guru-api-660206747784.asia-south1.run.app
```

### Test Endpoint
```bash
curl "https://guru-api-660206747784.asia-south1.run.app/api/v1/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata" | jq '.D10'
```

## 🎨 FRONTEND CONFIGURATION

**Frontend API URLs updated to use asia-south1:**

- ✅ `apps/guru-web/guru-web/services/api.ts`
  - Default: `https://guru-api-660206747784.asia-south1.run.app`

- ✅ `apps/guru-web/guru-astro-api/src/services/astroService.ts`
  - Default: `https://guru-api-660206747784.asia-south1.run.app`

**Both UI and API now point to the same canonical service.**

## 📝 HISTORY

- **2025-12-14:** 
  - Deleted `us-central1/guru-api` service (accidentally created)
  - Locked all deployment scripts to `asia-south1`
  - Updated frontend configs to use `asia-south1`
  - Deployed D10 fix to `asia-south1` (revision: guru-api-00005-rdl)

## ⚠️ CRITICAL RULES

1. **NEVER deploy to us-central1** - Service deleted, must not be recreated
2. **ALWAYS use asia-south1** - Only valid region for production
3. **Verify before deploying** - Check region in script before running
4. **Test after deployment** - Verify service URL matches asia-south1
5. **Update frontend if URL changes** - Keep UI and API in sync

## 🔧 TROUBLESHOOTING

### If deployment fails with region error:
- ✅ This is expected - region lock is working
- Check script has `REGION="asia-south1"`
- Verify no hardcoded `us-central1` in script

### If multiple services appear:
- ❌ This should never happen
- Delete any non-asia-south1 services immediately
- Verify region lock in all deployment scripts

### If frontend can't connect:
- Check `apps/guru-web/guru-web/services/api.ts` has asia-south1 URL
- Check `apps/guru-web/guru-astro-api/src/services/astroService.ts` has asia-south1 URL
- Verify environment variables if using custom URL

## ✅ CURRENT STATUS

- ✅ **Only ONE service exists:** `asia-south1/guru-api`
- ✅ **All deployment scripts locked:** Region validation enforced
- ✅ **Frontend configured:** Both API clients use asia-south1
- ✅ **D10 fix deployed:** Revision guru-api-00005-rdl
- ✅ **Service verified:** D10 results match Prokerala exactly

---

**Last Updated:** 2025-12-14  
**Maintained By:** DevOps Team  
**Contact:** See deployment scripts for project details

