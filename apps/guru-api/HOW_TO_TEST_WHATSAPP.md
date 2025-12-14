# How to Test WhatsApp Notifications - Complete Guide

## 🚀 Quick Start

### Method 1: Direct Python Test (Easiest)

```bash
python3 test_whatsapp_now.py
```

This will:
1. Ask for your WhatsApp number
2. Send a test message
3. Show results

---

## 📱 Method 2: Test via API (Full Flow)

### Step 1: Start the Server

```bash
uvicorn src.main:app --reload
```

### Step 2: Run API Test Script

```bash
python3 test_whatsapp_api.py
```

This will:
1. Create a test user
2. Save birth data
3. Enable WhatsApp notifications
4. Trigger notification
5. Show delivery logs

---

## 🧪 Method 3: Manual API Testing

### Step 1: Create User & Get Token

```bash
# Signup
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123"
  }'

# Login (get token)
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

### Step 2: Save Birth Data

```bash
curl -X POST "http://localhost:8000/user/birthdata" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Person",
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.97,
    "lon": 77.59
  }'
```

### Step 3: Enable WhatsApp Notifications

```bash
curl -X POST "http://localhost:8000/notifications/settings/update" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_whatsapp": "enabled",
    "whatsapp_number": "+919110233527",
    "delivery_time": "06:00"
  }'
```

### Step 4: Trigger Notification (Requires Premium)

```bash
curl -X POST "http://localhost:8000/admin/trigger-daily" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Method 4: Direct Function Test (For Developers)

```python
from src.notifications.channels.whatsapp import send_whatsapp

# Simple text message
result = send_whatsapp(
    to="+919110233527",
    message="Hello from Guru API! 🌟"
)
print(result)

# Content template
result = send_whatsapp(
    to="+919110233527",
    content_sid="HXb5b62575e6e4ff6129ad7c8efe1f983e",
    content_variables={"1": "12/1", "2": "3pm"}
)
print(result)
```

---

## ⚠️ Important: Twilio Sandbox Setup

If you're using Twilio Sandbox (`+14155238886`), the recipient **must join first**:

1. **Get Sandbox Code:**
   - Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - You'll see a code like: `join xyz-abc`

2. **Join Sandbox:**
   - Send WhatsApp message to: `+14155238886`
   - Message: `join xyz-abc` (use your actual code)
   - You'll receive confirmation

3. **Then Test:**
   - Now you can receive messages from the sandbox number

---

## 🔍 Check Message Status

### Via Twilio Console

1. Go to: https://console.twilio.com/us1/monitor/logs/messages
2. You'll see all sent messages
3. Check status: `delivered`, `sent`, `failed`

### Via API (Delivery Logs)

```bash
curl "http://localhost:8000/notifications/settings/delivery-logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 Test Scenarios

### Scenario 1: Immediate Test

```python
# Test right now
from src.notifications.channels.whatsapp import send_whatsapp

result = send_whatsapp(
    to="+919110233527",
    message="Test message from Guru API!"
)
```

### Scenario 2: Scheduled Test

1. Set delivery_time to current time + 1 minute
2. Wait for scheduler (runs every 5 minutes)
3. Or manually trigger: `/admin/trigger-daily`

### Scenario 3: Content Template Test

```python
result = send_whatsapp(
    to="+919110233527",
    content_sid="HXb5b62575e6e4ff6129ad7c8efe1f983e",
    content_variables={"1": "12/1", "2": "3pm"}
)
```

---

## 🐛 Troubleshooting

### Error: "Not a valid WhatsApp number"

**Solution:**
- Make sure number starts with `+` and country code
- Format: `+919110233527` (not `919110233527`)

### Error: "The number is not registered in WhatsApp"

**Solution:**
- For sandbox: Recipient must join first (send "join [code]")
- For production: Number must be approved WhatsApp Business number

### Error: "Twilio client not initialized"

**Solution:**
- Check `.env` file has `TWILIO_SID` and `TWILIO_AUTH_TOKEN`
- Restart server after adding credentials

### Message not received

**Check:**
1. Twilio Console → Monitor → Logs → Messages
2. Check message status
3. Verify recipient joined sandbox (if using sandbox)
4. Check delivery logs via API

---

## ✅ Success Indicators

When WhatsApp notification works, you'll see:

1. **In Python:**
   ```python
   {
       "success": True,
       "message_sid": "SMxxxxx",
       "status": "queued" or "sent",
       "method": "text_message" or "content_template"
   }
   ```

2. **In Twilio Console:**
   - Message appears in logs
   - Status: `sent` → `delivered`

3. **On Your Phone:**
   - WhatsApp message received
   - From: `+14155238886` (sandbox) or your business number

---

## 📋 Quick Test Checklist

- [ ] Twilio credentials in `.env`
- [ ] Server running: `uvicorn src.main:app --reload`
- [ ] Recipient joined sandbox (if using sandbox)
- [ ] Test number format: `+919110233527`
- [ ] Run test script: `python3 test_whatsapp_now.py`
- [ ] Check WhatsApp on phone
- [ ] Check Twilio Console for status

---

## 🎯 Recommended Test Flow

1. **Start with Direct Test:**
   ```bash
   python3 test_whatsapp_now.py
   ```

2. **If successful, test via API:**
   ```bash
   python3 test_whatsapp_api.py
   ```

3. **Check delivery logs:**
   ```bash
   curl "http://localhost:8000/notifications/settings/delivery-logs" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

---

**Ready to test?** Run: `python3 test_whatsapp_now.py`

