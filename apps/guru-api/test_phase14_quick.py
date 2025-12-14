#!/usr/bin/env python3
"""
Quick Test Script for Phase 14: Ask the Guru
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_ask_guru():
    """Test Ask the Guru functionality."""
    print("="*70)
    print("  PHASE 14: ASK THE GURU - QUICK TEST")
    print("="*70)
    
    # You'll need a valid token - get it from login
    print("\n⚠️  Note: You need a valid JWT token to test this.")
    print("   Get token by logging in first:")
    print("   POST /auth/login")
    
    token = input("\n📝 Enter JWT token (or press Enter to skip): ").strip()
    
    if not token:
        print("   ⏭️  Skipping API tests (no token provided)")
        print("\n💡 To test:")
        print("   1. Login: POST /auth/login")
        print("   2. Save birth data: POST /user/birthdata")
        print("   3. Ask question: POST /guru/ask")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Ask a question
    print(f"\n🔍 Test 1: Ask the Guru")
    print(f"   URL: {BASE_URL}/guru/ask")
    print(f"   Question: 'Is today good for financial decisions?'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/guru/ask",
            json={"question": "Is today good for financial decisions?"},
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Question ID: {data.get('question_id')}")
            print(f"   Answer length: {len(data.get('answer', ''))} characters")
            print(f"   Answer preview: {data.get('answer', '')[:200]}...")
        elif response.status_code == 400:
            error = response.json()
            print(f"   ⚠️  Error: {error.get('detail', 'Unknown error')}")
            if "Birth data" in str(error):
                print(f"   💡 Tip: Save your birth data first: POST /user/birthdata")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Get question history
    print(f"\n🔍 Test 2: Question History")
    print(f"   URL: {BASE_URL}/guru/history")
    
    try:
        response = requests.get(
            f"{BASE_URL}/guru/history",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Total questions: {data.get('total_questions', 0)}")
            questions = data.get('questions', [])
            if questions:
                print(f"   Latest question: {questions[0].get('question', 'N/A')[:60]}...")
            else:
                print(f"   No questions yet")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   - Make sure you have birth data saved")
    print("   - Questions are stored in database")
    print("   - AI uses full astrological context")
    print("   - Test in browser: http://localhost:8000/docs")

if __name__ == "__main__":
    test_ask_guru()

