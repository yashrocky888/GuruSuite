#!/usr/bin/env python3
"""
Quick Test Script for Phase 6: Yogas Engine

Simple and fast way to test yoga detection.
"""

import requests
import json

# Test birth details
BIRTH_DETAILS = {
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.97,
    "lon": 77.59
}

BASE_URL = "http://localhost:8000"

def test_yogas_quick():
    """Quick test of yoga detection."""
    print("="*70)
    print("  QUICK YOGAS TEST")
    print("="*70)
    
    print(f"\n📅 Testing with birth details:")
    print(f"   Date: {BIRTH_DETAILS['dob']}")
    print(f"   Time: {BIRTH_DETAILS['time']}")
    print(f"   Location: {BIRTH_DETAILS['lat']}, {BIRTH_DETAILS['lon']}")
    
    # Test 1: All Yogas
    print(f"\n🔍 Test 1: All Yogas")
    print(f"   URL: {BASE_URL}/yogas/all")
    try:
        response = requests.get(f"{BASE_URL}/yogas/all", params=BIRTH_DETAILS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            yogas = data.get('yogas', {})
            print(f"   ✅ Success!")
            print(f"   Total Yogas: {yogas.get('total_yogas', 0)}")
            print(f"   Major: {len(yogas.get('major_yogas', []))}")
            print(f"   Moderate: {len(yogas.get('moderate_yogas', []))}")
            print(f"   Doshas: {len(yogas.get('doshas', []))}")
            
            print(f"\n   Sample Yogas:")
            for yoga in yogas.get('all_yogas', [])[:5]:
                print(f"     - {yoga.get('name', 'Unknown')} ({yoga.get('category', 'Unknown')})")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to server!")
        print(f"   Make sure server is running: uvicorn src.main:app --reload")
    except requests.exceptions.Timeout:
        print(f"   ⚠️  Request timed out (server may be slow)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Major Yogas Only
    print(f"\n🔍 Test 2: Major Yogas Only")
    print(f"   URL: {BASE_URL}/yogas/major")
    try:
        response = requests.get(f"{BASE_URL}/yogas/major", params=BIRTH_DETAILS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Count: {data.get('count', 0)}")
            for yoga in data.get('major_yogas', [])[:3]:
                print(f"     - {yoga.get('name', 'Unknown')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Planetary Yogas
    print(f"\n🔍 Test 3: Planetary Yogas")
    print(f"   URL: {BASE_URL}/yogas/planetary")
    try:
        response = requests.get(f"{BASE_URL}/yogas/planetary", params=BIRTH_DETAILS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Count: {data.get('count', 0)}")
            for yoga in data.get('planetary_yogas', [])[:3]:
                print(f"     - {yoga.get('name', 'Unknown')}")
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
    print("   - Or use curl:")
    print(f"     curl '{BASE_URL}/yogas/all?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59'")

if __name__ == "__main__":
    test_yogas_quick()

