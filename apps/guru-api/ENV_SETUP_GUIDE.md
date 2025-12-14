# Environment Variables Setup Guide

## Phase 12: Multi-Channel Notification Credentials

This guide explains how to obtain all required credentials for the notification delivery system.

---

## 1. WhatsApp (Twilio) - TWILIO_WHATSAPP_FROM

### You Already Have:
- ✅ `TWILIO_SID`: ACxxxxx (configure in .env)
- ✅ `TWILIO_AUTH_TOKEN`: xxxxx (configure in .env)
- ✅ `TWILIO_PHONE_NUMBER`: +1xxxxxxxxxx (configure in .env)

### How to Get WhatsApp Number:

**Option A: Use Twilio Sandbox (Free for Testing)**
1. Go to https://console.twilio.com/
2. Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
3. You'll see a sandbox number like: `whatsapp:+14155238886`
4. Join the sandbox by sending "join [code]" to that number
5. Use: `TWILIO_WHATSAPP_FROM=+14155238886` (or the sandbox number shown)

**Option B: Get Production WhatsApp Number (Paid)**
1. Go to https://console.twilio.com/
2. Navigate to **Messaging** → **Settings** → **WhatsApp Sender**
3. Request a WhatsApp Business number (requires approval)
4. Once approved, you'll get a WhatsApp-enabled number
5. Use that number as `TWILIO_WHATSAPP_FROM`

**For Testing (Sandbox):**
```
TWILIO_WHATSAPP_FROM=+14155238886
```
(Common Twilio sandbox number - verify in your console)

---

## 2. Email - SMTP_USER & SMTP_PASS

### Option A: Gmail SMTP (Free)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Guru API" as name
   - Click "Generate"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

3. **Set Environment Variables:**
   ```
   SMTP_USER=your-email@gmail.com
   SMTP_PASS=abcd efgh ijkl mnop  (the app password, remove spaces)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   ```

### Option B: SendGrid (Recommended for Production)

1. **Sign up:** https://signup.sendgrid.com/
2. **Verify your account** (check email)
3. **Create API Key:**
   - Go to: https://app.sendgrid.com/settings/api_keys
   - Click "Create API Key"
   - Name it "Guru API"
   - Select "Full Access" or "Restricted Access" (Mail Send)
   - Click "Create & View"
   - **Copy the key immediately** (shown only once!)
   - Format: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

4. **Set Environment Variable:**
   ```
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. **Verify Sender (Required):**
   - Go to: https://app.sendgrid.com/settings/sender_auth/senders
   - Click "Create New Sender"
   - Enter your email and details
   - Verify via email

**Note:** SendGrid free tier: 100 emails/day

---

## 3. Push Notifications - Firebase Admin SDK

### ⚠️ Important: Legacy API Deprecated

Firebase has **deprecated the legacy FCM API** (the one using `FCM_SERVER_KEY`). 
We now use the **modern Firebase Admin SDK (HTTP v1)**.

### Firebase Cloud Messaging Setup (Modern Method)

1. **Create Firebase Project:**
   - Go to: https://console.firebase.google.com/
   - Click "Add project" or select existing
   - Enter project name (e.g., "Guru API")
   - Click "Continue" → "Continue" → "Create project"

2. **Create Service Account:**
   - Go to: https://console.cloud.google.com/
   - Select your Firebase project
   - Navigate to **IAM & Admin** → **Service Accounts**
   - Click **"Create Service Account"**
   - Name: "guru-api-fcm"
   - Role: **"Firebase Cloud Messaging API Admin"**
   - Click **"Create"**

3. **Generate Service Account Key:**
   - In Service Accounts, find your account
   - Click **"Actions"** (three dots) → **"Manage Keys"**
   - Click **"Add Key"** → **"Create new key"**
   - Select **JSON** format
   - Download the JSON file (e.g., `guru-api-firebase-adminsdk.json`)

4. **Set Environment Variable:**
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
   ```
   (Use absolute or relative path to your JSON file)

5. **Add to .gitignore:**
   ```
   firebase-service-account.json
   ```

**See `FIREBASE_SETUP.md` for detailed instructions!**

---

## Complete .env File Example

Create or update `.env` file in project root:

```bash
# Twilio WhatsApp
TWILIO_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_FROM=+14155238886

# Email - Option 1: Gmail SMTP
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Email - Option 2: SendGrid (preferred for production)
# SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Push Notifications - FCM
FCM_SERVER_KEY=AAAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Other existing variables...
DATABASE_URL=postgresql://user:pass@localhost:5432/guru_api
JWT_SECRET=your-jwt-secret-here
OPENAI_API_KEY=your-openai-key-here
```

---

## Quick Setup Steps Summary

### 1. WhatsApp (5 minutes)
- ✅ Already have SID and Token
- Go to Twilio Console → Messaging → WhatsApp Sandbox
- Use sandbox number: `+14155238886` (or check your console)
- Set: `TWILIO_WHATSAPP_FROM=+14155238886`

### 2. Email (10 minutes)
**Gmail (Easiest):**
- Enable 2FA on Gmail
- Generate App Password: https://myaccount.google.com/apppasswords
- Set: `SMTP_USER`, `SMTP_PASS`, `SMTP_HOST`, `SMTP_PORT`

**OR SendGrid (Better for production):**
- Sign up: https://signup.sendgrid.com/
- Create API Key
- Set: `SENDGRID_API_KEY`

### 3. Push (10 minutes)
- Create Firebase project: https://console.firebase.google.com/
- Go to Project Settings → Cloud Messaging
- Copy Server Key
- Set: `FCM_SERVER_KEY`

---

## Testing Your Setup

After setting environment variables, test each channel:

```python
# Test WhatsApp
from src.notifications.channels.whatsapp import send_whatsapp
result = send_whatsapp("+919876543210", "Test message")
print(result)

# Test Email
from src.notifications.channels.emailer import send_email
result = send_email("test@example.com", "Test", "Test email")
print(result)

# Test Push
from src.notifications.channels.push import send_push
result = send_push("fcm_token_here", "Test", "Test push")
print(result)
```

---

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to git
- Add `.env` to `.gitignore`
- Use environment variables in production
- Rotate keys regularly
- Use separate keys for development/production

---

## Troubleshooting

### WhatsApp
- **Error: "Not a valid WhatsApp number"**
  - Make sure number starts with `+` and country code
  - For sandbox, user must join first: send "join [code]" to sandbox number

### Email
- **Gmail: "Username and Password not accepted"**
  - Make sure you're using App Password, not regular password
  - Enable "Less secure app access" (if not using App Password)

### Push
- **Error: "Invalid FCM key"**
  - Verify Server Key from Firebase Console
  - Make sure Cloud Messaging API is enabled
  - Check key format (starts with `AAAA`)

---

**Last Updated:** Phase 12 Implementation

