# Firebase Cloud Messaging (FCM) Setup Guide

## ⚠️ Important: Legacy API Deprecated

Firebase has deprecated the legacy FCM API (the one using `FCM_SERVER_KEY`). We've updated the code to use the **modern Firebase Admin SDK (HTTP v1)**.

---

## ✅ New Method: Firebase Admin SDK (Recommended)

### Step 1: Create Firebase Project

1. Go to: https://console.firebase.google.com/
2. Click **"Add project"** or select existing
3. Enter project name: "Guru API"
4. Click through setup (disable Google Analytics if you want)

### Step 2: Enable Cloud Messaging

1. In Firebase Console, go to **⚙️ Settings** → **Project Settings**
2. Click **Cloud Messaging** tab
3. You'll see: "Cloud Messaging API (Legacy) Disabled" - **This is expected!**
4. We'll use the Admin SDK instead (more secure)

### Step 3: Create Service Account

1. Go to: https://console.cloud.google.com/
2. Select your Firebase project
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Click **"Create Service Account"**
5. Name: "guru-api-fcm"
6. Click **"Create and Continue"**
7. Role: **"Firebase Cloud Messaging API Admin"** (or "Firebase Admin SDK Administrator Service Agent")
8. Click **"Continue"** → **"Done"**

### Step 4: Generate Service Account Key

1. In **Service Accounts** page, find your service account
2. Click **"Actions"** (three dots) → **"Manage Keys"**
3. Click **"Add Key"** → **"Create new key"**
4. Select **JSON** format
5. Click **"Create"**
6. **Download the JSON file** (e.g., `guru-api-firebase-adminsdk-xxxxx.json`)

### Step 5: Set Up in Your Project

**Option A: Use Environment Variable (Recommended)**

1. Save the JSON file in your project (e.g., `firebase-service-account.json`)
2. Add to `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/firebase-service-account.json
   ```

   Or relative path:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
   ```

**Option B: Place in Standard Location**

1. Place JSON file at: `~/.config/gcloud/application_default_credentials.json`
2. Firebase Admin SDK will auto-detect it

### Step 6: Add to .gitignore

**IMPORTANT:** Never commit the service account JSON file!

Add to `.gitignore`:
```
firebase-service-account.json
*.json
!package.json
!package-lock.json
```

---

## 🔄 Migration from Legacy API

If you were using `FCM_SERVER_KEY`, you need to:

1. **Remove** `FCM_SERVER_KEY` from `.env`
2. **Add** `GOOGLE_APPLICATION_CREDENTIALS` pointing to your service account JSON
3. The code will automatically use the Admin SDK

---

## 📝 Complete .env Setup

```bash
# Firebase Admin SDK (Modern - Recommended)
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json

# OR if you still have legacy key (deprecated, will stop working June 2024)
# FCM_SERVER_KEY=AAAA... (not recommended)
```

---

## ✅ Verify Setup

Test your Firebase setup:

```python
from src.notifications.channels.push import send_push

# Test push notification
result = send_push(
    token="user-fcm-token-here",
    title="Test",
    message="Testing Firebase Admin SDK"
)

print(result)
```

---

## 🎯 Getting FCM Device Tokens

For your mobile app to receive push notifications:

1. **Android:** Use Firebase Cloud Messaging SDK
2. **iOS:** Use Firebase Cloud Messaging SDK
3. **Web:** Use Firebase Web SDK

The app will generate a device token that you store in the user's `push_token` field.

---

## 🔒 Security Best Practices

1. ✅ **Never commit** service account JSON to git
2. ✅ **Use environment variables** for paths
3. ✅ **Restrict service account permissions** (only FCM access)
4. ✅ **Rotate keys** periodically
5. ✅ **Use different keys** for dev/production

---

## 🆘 Troubleshooting

### Error: "Firebase not initialized"

**Solution:**
- Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Verify JSON file exists and is readable
- Check file permissions

### Error: "Permission denied"

**Solution:**
- Verify service account has "Firebase Cloud Messaging API Admin" role
- Check IAM permissions in Google Cloud Console

### Error: "Invalid token"

**Solution:**
- Verify FCM device token is valid
- Token might be expired (regenerate in app)

---

## 📚 Resources

- **Firebase Admin SDK Docs:** https://firebase.google.com/docs/admin/setup
- **FCM HTTP v1 API:** https://firebase.google.com/docs/cloud-messaging/migrate-v1
- **Service Account Setup:** https://cloud.google.com/iam/docs/service-accounts

---

## Summary

✅ **Old Way (Deprecated):**
- Used `FCM_SERVER_KEY`
- Legacy API (disabled by Firebase)
- Less secure

✅ **New Way (Current):**
- Use Firebase Admin SDK
- Service Account JSON file
- More secure, modern API
- Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

---

**Last Updated:** Phase 12 - Firebase Admin SDK Migration

