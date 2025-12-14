# Gmail Email Setup Guide - For Later Configuration

## 📧 Step-by-Step Instructions for Gmail SMTP Setup

Follow these steps when you're ready to configure email notifications.

---

## ✅ Prerequisites

- A Gmail account
- Access to Google Account settings
- 2-Factor Authentication enabled (required for App Passwords)

---

## 📝 Step 1: Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Scroll to **"How you sign in to Google"**
3. Find **"2-Step Verification"**
4. Click **"Get started"** (if not already enabled)
5. Follow the setup wizard:
   - Enter your password
   - Add a phone number
   - Verify with code sent to phone
   - Click **"Turn on"**

**Note:** This is required to generate App Passwords.

---

## 📝 Step 2: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
   - Or navigate: **Google Account** → **Security** → **2-Step Verification** → **App passwords**

2. You'll see a page titled **"App passwords"**

3. Select app:
   - Click dropdown: **"Select app"**
   - Choose **"Mail"**

4. Select device:
   - Click dropdown: **"Select device"**
   - Choose **"Other (Custom name)"**
   - Enter name: **"Guru API"**
   - Click **"Generate"**

5. **Copy the 16-character password:**
   - Example: `abcd efgh ijkl mnop`
   - **Important:** Copy this immediately - you won't see it again!
   - Remove spaces when using: `abcdefghijklmnop`

---

## 📝 Step 3: Add to .env File

Open your `.env` file and add:

```bash
# Email - Gmail SMTP
SMTP_USER=your-email@gmail.com
SMTP_PASS=abcdefghijklmnop
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**Replace:**
- `your-email@gmail.com` with your actual Gmail address
- `abcdefghijklmnop` with the App Password you generated (no spaces)

---

## 📝 Step 4: Test Email Sending

### Option A: Test via Python

```python
from src.notifications.channels.emailer import send_email

result = send_email(
    to="test@example.com",
    subject="Test from Guru API",
    body="This is a test email from Guru API!"
)

print(result)
```

### Option B: Test via API

1. Start your server: `uvicorn src.main:app --reload`
2. Update user preferences to enable email:
   ```bash
   curl -X POST "http://localhost:8000/notifications/settings/update" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "channel_email": "enabled"
     }'
   ```

---

## 🔍 Troubleshooting

### Error: "Username and Password not accepted"

**Solution:**
- Make sure you're using **App Password**, not your regular Gmail password
- Verify App Password has no spaces
- Check that 2-Factor Authentication is enabled

### Error: "Less secure app access"

**Solution:**
- Gmail no longer supports "Less secure app access"
- You **must** use App Passwords (generated in Step 2)
- App Passwords only work with 2FA enabled

### Error: "Connection refused" or "Timeout"

**Solution:**
- Check firewall settings
- Verify SMTP_HOST is `smtp.gmail.com`
- Verify SMTP_PORT is `587`
- Try port `465` with SSL (requires different code)

---

## 📋 Quick Checklist

When you're ready to set up Gmail:

- [ ] Enable 2-Factor Authentication on Gmail
- [ ] Generate App Password from Google Account
- [ ] Copy 16-character App Password (remove spaces)
- [ ] Add to `.env` file:
  - `SMTP_USER=your-email@gmail.com`
  - `SMTP_PASS=your-app-password`
  - `SMTP_HOST=smtp.gmail.com`
  - `SMTP_PORT=587`
- [ ] Test email sending
- [ ] Update user notification preferences to enable email channel

---

## 🔄 Alternative: SendGrid (Recommended for Production)

If you prefer a more professional solution:

1. **Sign up:** https://signup.sendgrid.com/
2. **Verify email** (check inbox)
3. **Create API Key:**
   - Go to: https://app.sendgrid.com/settings/api_keys
   - Click **"Create API Key"**
   - Name: "Guru API"
   - Permissions: "Full Access" or "Restricted Access" (Mail Send)
   - Copy key (starts with `SG.`)
4. **Add to `.env`:**
   ```bash
   SENDGRID_API_KEY=SG.your-key-here
   ```
5. **Verify Sender:**
   - Go to: https://app.sendgrid.com/settings/sender_auth/senders
   - Click **"Create New Sender"**
   - Enter your email and verify

**Benefits:**
- More reliable than Gmail SMTP
- Better for production
- Free tier: 100 emails/day
- Better deliverability
- Analytics dashboard

---

## 📝 Complete .env Example (After Setup)

```bash
# Email - Gmail SMTP (Option 1)
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# OR Email - SendGrid (Option 2 - Preferred for production)
# SENDGRID_API_KEY=SG.your-sendgrid-key-here
```

**Note:** The code will try SendGrid first (if `SENDGRID_API_KEY` is set), then fall back to SMTP.

---

## 🎯 When to Configure

Configure Gmail email when:
- ✅ You want to test email notifications
- ✅ You're ready to send daily horoscope emails
- ✅ You want to enable email channel for users
- ✅ You need email delivery logs

**Current Status:** Email notifications are optional. The system works without email configured.

---

## 📚 Related Files

- `src/notifications/channels/emailer.py` - Email sending implementation
- `ENV_SETUP_GUIDE.md` - Complete environment setup guide
- `QUICK_SETUP.md` - Quick reference for all credentials

---

**Last Updated:** Phase 12 - Gmail Setup Instructions
**Status:** Ready to configure when needed

