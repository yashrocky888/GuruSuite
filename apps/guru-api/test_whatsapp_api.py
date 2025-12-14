#!/usr/bin/env python3
"""
Test WhatsApp via API Endpoints

This script tests WhatsApp notifications through the API.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_whatsapp_via_api():
    """Test WhatsApp notifications via API."""
    print("="*70)
    print("  WHATSAPP NOTIFICATION TEST - VIA API")
    print("="*70)
    
    # Step 1: Create user and login
    print(f"\n📝 Step 1: Create test user and login")
    try:
        # Signup
        signup_data = {
            "name": "WhatsApp Test User",
            "email": f"whatsapp_test_{int(time.time())}@example.com",
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, timeout=10)
        if response.status_code != 200:
            print(f"   ⚠️  Signup failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return
        
        # Login
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            print(f"   ⚠️  Login failed: {response.status_code}")
            return
        
        token = response.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   ✅ User created and logged in")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 2: Save birth data
    print(f"\n📝 Step 2: Save birth data")
    try:
        birth_data = {
            "name": "Test Person",
            "dob": "1995-05-16",
            "time": "18:38",
            "lat": 12.97,
            "lon": 77.59,
            "gender": "Male"
        }
        response = requests.post(f"{BASE_URL}/user/birthdata", json=birth_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Birth data saved")
        else:
            print(f"   ⚠️  Birth data save failed: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    # Step 3: Update notification preferences to enable WhatsApp
    print(f"\n📝 Step 3: Enable WhatsApp notifications")
    test_number = input("   Enter WhatsApp number (e.g., +919110233527): ").strip()
    if not test_number:
        test_number = "+919110233527"
    
    try:
        prefs_data = {
            "channel_whatsapp": "enabled",
            "whatsapp_number": test_number,
            "delivery_time": "06:00",  # Or set to current time + 1 minute for testing
            "language": "english"
        }
        response = requests.post(
            f"{BASE_URL}/notifications/settings/update",
            json=prefs_data,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print(f"   ✅ WhatsApp notifications enabled")
            print(f"   Delivery time: {prefs_data['delivery_time']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: Manually trigger daily notifications (admin endpoint)
    print(f"\n📝 Step 4: Trigger daily notification")
    print(f"   Note: This requires premium subscription")
    try:
        response = requests.post(f"{BASE_URL}/admin/trigger-daily", headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Notification triggered!")
            result = data.get("result", {})
            print(f"   Created: {result.get('notifications_created', 0)}")
        elif response.status_code == 403:
            print(f"   ⚠️  Premium access required")
            print(f"   → Upgrade user subscription or use direct test script")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 5: Check delivery logs
    print(f"\n📝 Step 5: Check delivery logs")
    try:
        response = requests.get(f"{BASE_URL}/notifications/settings/delivery-logs", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            print(f"   ✅ Found {len(logs)} delivery logs")
            for log in logs[:3]:
                print(f"      - {log.get('channel')}: {log.get('status')} at {log.get('created_at', '')[:19]}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   - Check WhatsApp on your phone for the message")
    print("   - For sandbox, make sure you joined first")
    print("   - Check Twilio Console for delivery status")

if __name__ == "__main__":
    test_whatsapp_via_api()

