# 🚀 Deploy Changes to Production

## Status
- ✅ **Local Changes:** All fixes are working locally
- ⚠️ **Production:** Changes NOT yet deployed

## What Changed
1. ✅ Added house lords to all houses (no more "Unknown")
2. ✅ Added Sanskrit names for all signs (e.g., "Mesha" for Aries)
3. ✅ Fixed interpretation engine to use kundli correctly

## Deploy to Production

### Option 1: Quick Deploy (Recommended)
```bash
cd /Users/yashm/Guru_API
./DEPLOY_FINAL.sh
```

### Option 2: Manual Deploy
```bash
# Set your project
gcloud config set project guru-api-660206747784

# Build and deploy
gcloud builds submit --tag gcr.io/guru-api-660206747784/guru-api
gcloud run deploy guru-api \
  --image gcr.io/guru-api-660206747784/guru-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### Option 3: Test First (Recommended)
```bash
# Test the API locally first
cd /Users/yashm/Guru_API
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8080

# In another terminal, test:
curl -X POST http://localhost:8080/api/kundali/full \
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

## Verify Deployment
After deploying, test the production API:
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
  }' | jq '.data.kundli.Houses[9]'  # Check house 10
```

You should see:
- `"lord": "Sun"` (not "Unknown")
- `"sign_sanskrit": "Simha"` (Sanskrit name)
- `"sign": "Leo"` (English name)

## Files Changed
- `src/jyotish/kundli_engine.py` - Added house lords and Sanskrit names
- `guru_api.py` - Fixed interpretation engine call

## Ready to Deploy?
Run: `./DEPLOY_FINAL.sh`
