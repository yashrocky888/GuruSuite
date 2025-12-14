#!/usr/bin/env python3
"""
Quick Test Script for Phase 9: User Auth + Subscription System
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test complete authentication flow."""
    print("="*70)
    print("  PHASE 9: USER AUTH + SUBSCRIPTION - QUICK TEST")
    print("="*70)
    
    # Test 1: Signup
    print(f"\n🔍 Test 1: User Signup")
    print(f"   URL: {BASE_URL}/auth/signup")
    try:
        signup_data = {
            "name": "Test User",
            "email": f"test_{hash(str(__import__('time').time())) % 10000}@example.com",
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Signup successful!")
            print(f"   User ID: {data.get('user_id')}")
            user_email = signup_data["email"]
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Login
    print(f"\n🔍 Test 2: User Login")
    print(f"   URL: {BASE_URL}/auth/login")
    try:
        login_data = {
            "email": user_email,
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"   ✅ Login successful!")
            print(f"   Subscription: {data.get('subscription')}")
            print(f"   Token received: {len(token) if token else 0} chars")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 3: Get Current User
    print(f"\n🔍 Test 3: Get Current User")
    print(f"   URL: {BASE_URL}/auth/me")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User info retrieved!")
            print(f"   Name: {data.get('name')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Subscription: {data.get('subscription_level')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Save Birth Data
    print(f"\n🔍 Test 4: Save Birth Data")
    print(f"   URL: {BASE_URL}/user/birthdata")
    try:
        birth_data = {
            "name": "Test Person",
            "dob": "1995-05-16",
            "time": "18:38",
            "lat": 12.97,
            "lon": 77.59,
            "gender": "Male"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/user/birthdata", json=birth_data, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Birth data saved!")
            print(f"   Birth Data ID: {data.get('birth_data_id')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Get Birth Data
    print(f"\n🔍 Test 5: Get Birth Data")
    print(f"   URL: {BASE_URL}/user/birthdata")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/user/birthdata", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Birth data retrieved!")
            print(f"   Count: {data.get('count', 0)}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Subscription Status
    print(f"\n🔍 Test 6: Subscription Status")
    print(f"   URL: {BASE_URL}/subscription/status")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/subscription/status", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Subscription status retrieved!")
            print(f"   Plan: {data.get('plan')}")
            print(f"   Is Active: {data.get('is_active')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   - All endpoints require authentication (Bearer token)")
    print("   - Test in browser: http://localhost:8000/docs")
    print("   - Use 'Authorize' button in Swagger UI to add token")

if __name__ == "__main__":
    test_auth_flow()



