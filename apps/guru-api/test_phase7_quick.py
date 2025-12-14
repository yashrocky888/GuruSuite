#!/usr/bin/env python3
"""
Quick Test Script for Phase 7: Transits + Daily Impact Engine
"""

import requests
import json

BASE_URL = "http://localhost:8000"

BIRTH_DETAILS = {
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.97,
    "lon": 77.59
}

def test_transits():
    """Test transit endpoints."""
    print("="*70)
    print("  PHASE 7: TRANSITS + DAILY IMPACT - QUICK TEST")
    print("="*70)
    
    print(f"\n📅 Testing with birth details:")
    print(f"   Date: {BIRTH_DETAILS['dob']}")
    print(f"   Time: {BIRTH_DETAILS['time']}")
    print(f"   Location: {BIRTH_DETAILS['lat']}, {BIRTH_DETAILS['lon']}")
    
    # Test 1: All Transits
    print(f"\n🔍 Test 1: All Transits")
    print(f"   URL: {BASE_URL}/transit/all")
    try:
        response = requests.get(f"{BASE_URL}/transit/all", params=BIRTH_DETAILS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            transits = data.get('transits', {})
            print(f"   ✅ Success!")
            print(f"   Planets in transit: {len(transits)}")
            print(f"   Moon house: {transits.get('Moon', {}).get('house', 'N/A')}")
            print(f"   Moon aspects: {len(transits.get('Moon', {}).get('aspects', {}))}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Daily Summary
    print(f"\n🔍 Test 2: Daily Summary")
    print(f"   URL: {BASE_URL}/daily/summary")
    try:
        response = requests.get(f"{BASE_URL}/daily/summary", params=BIRTH_DETAILS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Date: {data.get('date', 'N/A')}")
            print(f"   Score: {data.get('score', 0):.1f}/100")
            print(f"   Rating: {data.get('rating', 'N/A')}")
            print(f"   Summary: {data.get('summary', 'N/A')}")
            print(f"   Lucky Color: {data.get('lucky_color', 'N/A')}")
            print(f"   Good Time: {data.get('timing', {}).get('good_time', 'N/A')}")
            print(f"   Caution Time: {data.get('timing', {}).get('caution_time', 'N/A')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Daily Rating (Quick)
    print(f"\n🔍 Test 3: Daily Rating (Quick)")
    print(f"   URL: {BASE_URL}/daily/rating")
    try:
        response = requests.get(f"{BASE_URL}/daily/rating", params=BIRTH_DETAILS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Score: {data.get('score', 0):.1f}/100")
            print(f"   Rating: {data.get('rating', 'N/A')}")
            print(f"   Lucky Color: {data.get('lucky_color', 'N/A')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   - If server is not running, start it with:")
    print("     uvicorn src.main:app --reload")
    print("   - Test in browser: http://localhost:8000/docs")

if __name__ == "__main__":
    test_transits()

