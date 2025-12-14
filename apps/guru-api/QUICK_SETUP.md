# Quick Setup Guide - Notification Credentials

## Your Current Setup

✅ **Twilio (WhatsApp):**
- SID: `ACxxxxx` (configure in .env)
- Token: `xxxxx` (configure in .env)
- Phone: `+1xxxxxxxxxx` (configure in .env)

---

## 1. TWILIO_WHATSAPP_FROM (5 minutes)

### Quick Method - Use Twilio Sandbox:

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. You'll see a sandbox number (usually `+14155238886`)
3. Copy that number
4. Set in `.env`:
   ```
   TWILIO_WHATSAPP_FROM=+14155238886
   ```

**Note:** For sandbox, users need to join first by sending "join [code]" to the sandbox number.

---

## 2. Email Credentials (10 minutes)

### Option A: Gmail (Easiest)

1. **Enable 2-Factor Authentication** on your Gmail
2. **Generate App Password:**
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" → "Other (Custom name)"
   - Name: "Guru API"
   - Click "Generate"
   - Copy the 16-character password (remove spaces)

3. **Add to `.env`:**
   ```
   SMTP_USER=your-email@gmail.com
   SMTP_PASS=abcdefghijklmnop
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   ```

### Option B: SendGrid (Better for Production)

1. Sign up: https://signup.sendgrid.com/ (free tier: 100 emails/day)
2. Verify email
3. Go to: https://app.sendgrid.com/settings/api_keys
4. Click "Create API Key"
5. Name: "Guru API", Permissions: "Full Access"
6. Copy the key (starts with `SG.`)
7. **Add to `.env`:**
   ```
   SENDGRID_API_KEY=SG.your-key-here
   ```

---

## 3. Firebase Admin SDK (15 minutes)

### ⚠️ Legacy API Deprecated - Use Admin SDK

Firebase deprecated the legacy API. Use the modern Admin SDK:

1. **Create Firebase Project:**
   - Go to: https://console.firebase.google.com/
   - Click "Add project" → Name: "Guru API"

2. **Create Service Account:**
   - Go to: https://console.cloud.google.com/
   - Select your Firebase project
   - **IAM & Admin** → **Service Accounts**
   - Click **"Create Service Account"**
   - Name: "guru-api-fcm"
   - Role: **"Firebase Cloud Messaging API Admin"**

3. **Download JSON Key:**
   - Click **"Actions"** → **"Manage Keys"**
   - **"Add Key"** → **"Create new key"** → **JSON**
   - Download the file (e.g., `firebase-service-account.json`)

4. **Add to `.env`:**
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
   ```

5. **Add to `.gitignore`:**
   ```
   firebase-service-account.json
   ```

**See `FIREBASE_SETUP.md` for detailed instructions!**

---

## Complete .env File

Create `.env` in project root:

```bash
# Twilio WhatsApp
TWILIO_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_FROM=+14155238886

# Email - Gmail
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# OR Email - SendGrid (uncomment to use)
# SENDGRID_API_KEY=SG.your-key-here

# Push - FCM
FCM_SERVER_KEY=AAAAyour-fcm-key-here
```

---

## Test Your Setup

After setting up, test each channel:

```bash
# Test credentials
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); exec(open('check_credentials.py').read())"
```

Or use the API:
```bash
# Update user preferences
curl -X POST "http://localhost:8000/notifications/settings/update" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_time": "06:00",
    "channel_email": "enabled",
    "channel_whatsapp": "enabled",
    "channel_push": "enabled"
  }'
```

---

## Quick Links

- **Twilio Console:** https://console.twilio.com/
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **SendGrid:** https://signup.sendgrid.com/
- **Firebase Console:** https://console.firebase.google.com/

---

**Need Help?** See `ENV_SETUP_GUIDE.md` for detailed instructions.

