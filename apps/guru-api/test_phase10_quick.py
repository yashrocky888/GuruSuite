#!/usr/bin/env python3
"""
Quick Test Script for Phase 10: Automatic Notifications + Cron Scheduler
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_notification_system():
    """Test notification system."""
    print("="*70)
    print("  PHASE 10: AUTOMATIC NOTIFICATIONS - QUICK TEST")
    print("="*70)
    
    # First, create a test user and login
    print(f"\n📝 Step 1: Create test user and login")
    try:
        # Signup
        signup_data = {
            "name": "Test User Notifications",
            "email": f"test_notif_{int(time.time())}@example.com",
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
    
    # Save birth data
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
    
    # Test 1: Manual trigger (admin endpoint)
    print(f"\n🔍 Test 1: Manual Trigger Daily Notifications")
    print(f"   URL: {BASE_URL}/admin/trigger-daily")
    try:
        response = requests.post(f"{BASE_URL}/admin/trigger-daily", headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Trigger successful!")
            result = data.get("result", {})
            print(f"   Notifications created: {result.get('notifications_created', 0)}")
            print(f"   Notifications failed: {result.get('notifications_failed', 0)}")
        elif response.status_code == 403:
            print(f"   ⚠️  Premium access required (expected for free users)")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Get notification history
    print(f"\n🔍 Test 2: Get Notification History")
    print(f"   URL: {BASE_URL}/notifications/history")
    try:
        response = requests.get(f"{BASE_URL}/notifications/history", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ History retrieved!")
            print(f"   Total: {data.get('total', 0)}")
            print(f"   Count: {data.get('count', 0)}")
            notifications = data.get('notifications', [])
            if notifications:
                print(f"   Latest notification:")
                latest = notifications[0]
                print(f"     Title: {latest.get('title', 'N/A')}")
                print(f"     Summary: {latest.get('summary', 'N/A')[:60]}...")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get unread count
    print(f"\n🔍 Test 3: Get Unread Count")
    print(f"   URL: {BASE_URL}/notifications/unread-count")
    try:
        response = requests.get(f"{BASE_URL}/notifications/unread-count", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Unread count: {data.get('unread_count', 0)}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get latest notification
    print(f"\n🔍 Test 4: Get Latest Notification")
    print(f"   URL: {BASE_URL}/notifications/latest")
    try:
        response = requests.get(f"{BASE_URL}/notifications/latest", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            notif = data.get('notification')
            if notif:
                print(f"   ✅ Latest notification found!")
                print(f"     Title: {notif.get('title', 'N/A')}")
                print(f"     Is Read: {notif.get('is_read', 'N/A')}")
            else:
                print(f"   ℹ️  No notifications yet")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Scheduler status (admin)
    print(f"\n🔍 Test 5: Scheduler Status")
    print(f"   URL: {BASE_URL}/admin/scheduler-status")
    try:
        response = requests.get(f"{BASE_URL}/admin/scheduler-status", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Scheduler status retrieved!")
            print(f"   Running: {data.get('running', False)}")
            print(f"   Jobs: {data.get('jobs_count', 0)}")
        elif response.status_code == 403:
            print(f"   ⚠️  Premium access required")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   - Scheduler runs daily at 6:00 AM IST (00:30 UTC)")
    print("   - Use /admin/trigger-daily to manually trigger")
    print("   - Premium users get full AI predictions")
    print("   - Free users get summary only")
    print("   - Test in browser: http://localhost:8000/docs")

if __name__ == "__main__":
    test_notification_system()

