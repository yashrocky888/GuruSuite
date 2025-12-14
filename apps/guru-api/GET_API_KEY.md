# 🔑 How to Get API Key for Your Guru Project

## Method 1: Using Admin Endpoint (Recommended)

### Step 1: Grant Firestore Permissions

The service account needs Firestore permissions. Run:

```bash
gcloud projects add-iam-policy-binding guru-api-6b9ba \
  --member="serviceAccount:660206747784-compute@developer.gserviceaccount.com" \
  --role="roles/firestore.user"
```

### Step 2: Create API Key

```bash
curl -X POST https://guru-api-660206747784.us-central1.run.app/api/admin/create-key \
  -H "x-master-admin-key: fIhJDMkrEnvffjq1uvEwPZ6ofjd016FwsACdoGC8AD8EspSfeKkRzBZtwsJzVaM4k5AS7RymvtZ8XcMe8BstdA" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Guru Project - Production",
    "description": "API key for Guru project integration"
  }'
```

**Response:**
```json
{
  "success": true,
  "api_key": "your-generated-api-key-here",
  "name": "Guru Project - Production",
  "message": "API key created successfully. Save this key securely - it won't be shown again."
}
```

⚠️ **Save the API key immediately!**

---

## Method 2: Using Environment Variable (Fallback)

If Firestore is not accessible, you can set API keys via environment variable:

1. **Set in Cloud Run:**
```bash
gcloud run services update guru-api \
  --region us-central1 \
  --update-env-vars "API_KEYS=your-api-key-1,your-api-key-2"
```

2. **Or use Secret Manager:**
```bash
echo -n "your-api-key-here" | gcloud secrets create api-keys --data-file=-
```

---

## Method 3: Manual Creation via Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/project/guru-api-6b9ba/firestore)
2. Navigate to Firestore Database
3. Create a collection: `api_keys`
4. Add a document with:
   - `key`: Your API key string
   - `name`: "Guru Project"
   - `description`: "Production key"
   - `active`: true
   - `created_at`: Server timestamp
   - `usage_count`: 0

---

## Using Your API Key

Once you have the API key, use it in all requests:

```bash
curl -X POST https://guru-api-660206747784.us-central1.run.app/api/kundali/full \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-15",
    "birth_time": "10:30",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }'
```

---

## For Development/Testing

For quick testing, you can use the default development key (if configured):

```bash
# Check if default key works
curl -X GET https://guru-api-660206747784.us-central1.run.app/api/health \
  -H "x-api-key: dev-api-key-change-in-production"
```

---

## Next Steps

1. ✅ Get your API key using one of the methods above
2. ✅ Save it securely (environment variable, secret manager, etc.)
3. ✅ Use it in your Guru project
4. ✅ See `API_USAGE_GUIDE.md` for code examples

