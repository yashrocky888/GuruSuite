#!/usr/bin/env python3
"""
Quick Test Script for Phase 11: Payment Integration (Razorpay + Stripe)
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_payment_system():
    """Test payment system."""
    print("="*70)
    print("  PHASE 11: PAYMENT INTEGRATION - QUICK TEST")
    print("="*70)
    
    # First, create a test user and login
    print(f"\n📝 Step 1: Create test user and login")
    try:
        # Signup
        signup_data = {
            "name": "Test Payment User",
            "email": f"test_payment_{int(time.time())}@example.com",
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
    
    # Test 1: Get payment plans
    print(f"\n🔍 Test 1: Get Payment Plans")
    print(f"   URL: {BASE_URL}/payments/plans")
    try:
        response = requests.get(f"{BASE_URL}/payments/plans", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Plans retrieved!")
            print(f"   Available plans: {len(data.get('plans', []))}")
            for plan in data.get('plans', [])[:3]:
                print(f"     - {plan.get('name')}: ₹{plan.get('amount_inr')} / ${plan.get('amount_usd')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Create Razorpay order (will fail without API keys, but tests structure)
    print(f"\n🔍 Test 2: Create Razorpay Payment")
    print(f"   URL: {BASE_URL}/payments/create")
    try:
        payment_data = {
            "plan": "premium_monthly",
            "gateway": "razorpay"
        }
        response = requests.post(f"{BASE_URL}/payments/create", json=payment_data, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Razorpay order created!")
            print(f"   Order ID: {data.get('order_id', 'N/A')}")
            print(f"   Amount: ₹{data.get('amount', 0)}")
        elif response.status_code == 400:
            print(f"   ⚠️  Expected error (no API keys): {response.json().get('detail', 'N/A')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Create Stripe session (will fail without API keys, but tests structure)
    print(f"\n🔍 Test 3: Create Stripe Payment")
    print(f"   URL: {BASE_URL}/payments/create")
    try:
        payment_data = {
            "plan": "premium_yearly",
            "gateway": "stripe"
        }
        response = requests.post(f"{BASE_URL}/payments/create", json=payment_data, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stripe session created!")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            print(f"   Amount: ${data.get('amount', 0)}")
        elif response.status_code == 400:
            print(f"   ⚠️  Expected error (no API keys): {response.json().get('detail', 'N/A')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get payment history
    print(f"\n🔍 Test 4: Get Payment History")
    print(f"   URL: {BASE_URL}/payments/history")
    try:
        response = requests.get(f"{BASE_URL}/payments/history", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ History retrieved!")
            print(f"   Total transactions: {data.get('total', 0)}")
            print(f"   Count: {data.get('count', 0)}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   - Set RAZORPAY_KEY and RAZORPAY_SECRET for Razorpay")
    print("   - Set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY for Stripe")
    print("   - Payment verification requires actual payment completion")
    print("   - Test in browser: http://localhost:8000/docs")
    print("\n📋 Payment Plans:")
    print("   - Premium Monthly: ₹299 / $3.99")
    print("   - Premium Yearly: ₹1999 / $24.99")
    print("   - Lifetime: ₹4999 / $59.99")

if __name__ == "__main__":
    test_payment_system()

