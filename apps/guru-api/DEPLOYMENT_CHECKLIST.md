# ✅ Deployment Checklist

## Pre-Deployment

- [x] All code files verified
- [x] Firebase integration complete
- [x] Dockerfile configured (port 8080)
- [x] Environment templates created
- [x] Deployment scripts ready
- [x] Firebase credentials found: ✅
- [ ] gcloud CLI installed (install: https://cloud.google.com/sdk/docs/install)
- [ ] GCP project created
- [ ] Firestore database created
- [ ] Secrets created in Secret Manager

## Deployment Steps

1. **Install gcloud CLI** (if not installed):
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Or download from:
   # https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable APIs**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable firestore.googleapis.com
   ```

4. **Create Firestore**:
   ```bash
   gcloud firestore databases create --location=us-central
   ```

5. **Create Secrets**:
   ```bash
   # Firebase credentials
   echo -n "$(cat firebase-service-account.json)" | \
     gcloud secrets create firebase-credentials --data-file=-
   
   # Master admin key (use the generated key)
   echo -n "YOUR_MASTER_ADMIN_KEY" | \
     gcloud secrets create master-key --data-file=-
   ```

6. **Deploy**:
   ```bash
   ./deploy-firebase.sh
   ```

7. **Get Service URL**:
   ```bash
   gcloud run services describe guru-api \
     --region us-central1 \
     --format 'value(status.url)'
   ```

8. **Create First API Key**:
   ```bash
   curl -X POST YOUR_SERVICE_URL/api/admin/create-key \
     -H "x-master-admin-key: YOUR_MASTER_KEY" \
     -H "Content-Type: application/json" \
     -d '{"name":"Production Key","description":"Main key"}'
   ```

## Post-Deployment

- [ ] Test health endpoint
- [ ] Test API with generated key
- [ ] Monitor logs
- [ ] Set up alerts (optional)
- [ ] Configure custom domain (optional)

