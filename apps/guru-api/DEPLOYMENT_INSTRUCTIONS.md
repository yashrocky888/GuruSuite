# Deployment Instructions - JHORA House Calculations

## Summary of Changes

✅ **JHORA House Calculation Implemented for All Varga Charts:**
- D1 (Main Chart): JHORA method (house = sign number)
- D2 (Hora): JHORA method
- D3 (Drekkana): JHORA method
- D4 (Chaturthamsa): JHORA method
- D7 (Saptamsa): JHORA method
- D9 (Navamsa): JHORA method
- D10 (Dasamsa): JHORA method
- D12 (Dwadasamsa): JHORA method

✅ **Varga Sign Calculations:**
- All varga sign calculations verified and passing tests
- D7, D10, D12 match reference data 100%

## Deployment Steps

### Option 1: Using Deployment Script

```bash
./DEPLOY_JHORA.sh
```

### Option 2: Manual Deployment

```bash
# Set project
gcloud config set project guru-api-6b9ba

# Build Docker image
gcloud builds submit --tag gcr.io/guru-api-6b9ba/guru-api

# Deploy to Cloud Run
gcloud run deploy guru-api \
  --image gcr.io/guru-api-6b9ba/guru-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### Option 3: Using Google Cloud Console

1. Go to Cloud Build in Google Cloud Console
2. Create a new build trigger or submit build manually
3. Use the Dockerfile in the project root
4. Tag: `gcr.io/guru-api-6b9ba/guru-api`
5. Deploy to Cloud Run service `guru-api` in region `us-central1`

## Verification After Deployment

Test the deployed API:

```bash
curl "https://guru-api-6b9ba-uc.a.run.app/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata"
```

Check that:
- D1 planets have correct house assignments (house = sign number)
- All varga charts (D2, D3, D4, D7, D9, D10, D12) have house assignments
- House numbers match sign numbers (JHORA method)

## Notes

- The same API key can be used after deployment
- No breaking changes to API structure
- All existing endpoints remain functional
- JHORA house calculation is now the default for all charts

