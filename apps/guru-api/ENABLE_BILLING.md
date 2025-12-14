# Enable Billing for GCP Project

## Quick Steps

1. **Open Billing Console:**
   https://console.cloud.google.com/billing?project=guru-api-6b9ba

2. **Link Billing Account:**
   - If you have a billing account, link it
   - If not, create a new billing account
   - Add payment method (credit card)

3. **Verify:**
   ```bash
   gcloud billing projects describe guru-api-6b9ba
   ```

4. **Deploy:**
   ```bash
   ./DEPLOY_FINAL.sh
   ```

## Free Tier Limits

Cloud Run Free Tier includes:
- ✅ 2 million requests/month
- ✅ 360,000 GB-seconds compute
- ✅ 180,000 vCPU-seconds

**Your API will likely stay within free tier!**

## After Billing is Enabled

The deployment script will automatically:
1. Enable required APIs
2. Create Firestore
3. Create secrets
4. Build and deploy

Just run: `./DEPLOY_FINAL.sh`
