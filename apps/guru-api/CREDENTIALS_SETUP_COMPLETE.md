# ✅ Credentials Setup Complete!

## Your Current Configuration

### ✅ Twilio WhatsApp
- **SID**: `ACxxxxx` (configure in .env)
- **Auth Token**: `xxxxx` (configure in .env)
- **WhatsApp From**: `+14155238886` (Sandbox number - example)
- **Status**: ✅ Configured

### ✅ Firebase Push Notifications
- **Service Account**: `firebase-service-account.json`
- **Project ID**: `guru-api-6b9ba`
- **Status**: ✅ Configured

---

## 📝 What's Been Set Up

1. ✅ **Firebase Service Account JSON** saved to `firebase-service-account.json`
2. ✅ **WhatsApp Channel** updated to support content templates
3. ✅ **.env file** created with all your credentials
4. ✅ **Push Notifications** using Firebase Admin SDK (HTTP v1)

---

## 🧪 Testing Your Setup

### Test WhatsApp (Simple Message)

```python
from src.notifications.channels.whatsapp import send_whatsapp

result = send_whatsapp(
    to="+919110233527",
    message="Hello from Guru API!"
)
print(result)
```

### Test WhatsApp (Content Template)

```python
from src.notifications.channels.whatsapp import send_whatsapp

result = send_whatsapp(
    to="+919110233527",
    content_sid="HXb5b62575e6e4ff6129ad7c8efe1f983e",
    content_variables={"1": "12/1", "2": "3pm"}
)
print(result)
```

### Test Push Notification

```python
from src.notifications.channels.push import send_push

result = send_push(
    token="user-fcm-token-here",
    title="Test",
    message="Testing Firebase Admin SDK"
)
print(result)
```

---

## 📋 Next Steps

### 1. WhatsApp Sandbox Setup

If using Twilio Sandbox (`+14155238886`):
- Recipient must join the sandbox first
- Send "join [code]" to `+14155238886`
- Get code from: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn

### 2. Email Setup (Optional)

If you want email notifications:

**Gmail:**
```bash
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**OR SendGrid:**
```bash
SENDGRID_API_KEY=SG.your-key-here
```

### 3. Test the Full System

```bash
# Start the server
uvicorn src.main:app --reload

# Test notification preferences
curl -X POST "http://localhost:8000/notifications/settings/update" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_time": "06:00",
    "channel_whatsapp": "enabled",
    "channel_email": "enabled",
    "channel_push": "enabled",
    "language": "english"
  }'
```

---

## 🔒 Security Reminders

⚠️ **Important:**
- ✅ `.env` is already in `.gitignore`
- ✅ `firebase-service-account.json` should be added to `.gitignore`
- ✅ Never commit credentials to git
- ✅ Use different credentials for production

---

## 📚 Files Created

1. ✅ `firebase-service-account.json` - Firebase credentials
2. ✅ `.env` - Environment variables
3. ✅ `test_whatsapp_template.py` - Test script
4. ✅ Updated WhatsApp channel with content template support

---

## ✅ Status

- **WhatsApp**: ✅ Ready (supports text + content templates)
- **Firebase Push**: ✅ Ready (using Admin SDK)
- **Email**: ⚠️ Optional (not configured yet)

**Everything is set up and ready to use!** 🎉

