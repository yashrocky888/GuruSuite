#!/usr/bin/env python3
"""
Simple test script for Guru API - Beginner Friendly

This script tests the main Kundli endpoint and shows you how to use the API.
"""

import requests
import json
from datetime import datetime

# Base URL of your API
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_check():
    """Test 1: Health Check"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server!")
        print("   Make sure the server is running:")
        print("   uvicorn src.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root_endpoint():
    """Test 2: Root Endpoint"""
    print_section("Test 2: Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        data = response.json()
        print(f"✅ API Name: {data.get('name')}")
        print(f"✅ Version: {data.get('version')}")
        print(f"✅ Status: {data.get('status')}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_kundli_simple():
    """Test 3: Simple Kundli Calculation (GET)"""
    print_section("Test 3: Kundli Calculation (GET /kundli)")
    
    # Test parameters
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    print(f"📅 Date of Birth: {params['dob']}")
    print(f"⏰ Time: {params['time']}")
    print(f"📍 Location: {params['lat']}, {params['lon']} (Bangalore)")
    
    try:
        response = requests.get(f"{BASE_URL}/kundli", params=params, timeout=10)
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            kundli_data = response.json()
            
            # Extract key information
            print("\n📊 Key Information:")
            print(f"   Julian Day: {kundli_data.get('julian_day', 'N/A')}")
            
            d1 = kundli_data.get('D1', {})
            asc = d1.get('Ascendant', {})
            print(f"   Ascendant: {asc.get('sign', 'N/A')} at {asc.get('degree', 0):.2f}°")
            
            planets = d1.get('Planets', {})
            print(f"\n   Planets:")
            for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                if planet in planets:
                    p_data = planets[planet]
                    print(f"     {planet:8s}: {p_data.get('sign', 'N/A'):12s} at {p_data.get('degree', 0):.2f}°")
            
            houses = d1.get('Houses', [])
            print(f"\n   Houses: {len(houses)} house cusps calculated")
            
            d9 = kundli_data.get('D9', {})
            d10 = kundli_data.get('D10', {})
            print(f"\n   D9 (Navamsa): {len(d9)} planets")
            print(f"   D10 (Dasamsa): {len(d10)} planets")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_kundli_post():
    """Test 4: Full Kundli with POST (more details)"""
    print_section("Test 4: Full Kundli (POST /api/v1/kundli)")
    
    data = {
        "name": "Test User",
        "birth_date": "1995-05-16T18:38:00",
        "birth_time": "18:38",
        "birth_latitude": 12.97,
        "birth_longitude": 77.59,
        "birth_place": "Bangalore",
        "timezone": "Asia/Kolkata"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/kundli", json=data, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            kundli_data = response.json()
            print(f"✅ Name: {kundli_data.get('name', 'N/A')}")
            print(f"✅ Chart Type: {kundli_data.get('chart_type', 'N/A')}")
            print(f"✅ Planets: {len(kundli_data.get('planets', {}))} planets")
            print(f"✅ Houses: {len(kundli_data.get('houses', {}))} houses")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_your_details():
    """Test 5: Interactive - Use Your Own Details"""
    print_section("Test 5: Use Your Own Birth Details")
    print("💡 You can modify this function with your own details!")
    print("\nExample:")
    print("   params = {")
    print("       'dob': '1990-01-15',  # Your date of birth")
    print("       'time': '10:30',      # Your time of birth")
    print("       'lat': 28.6139,      # Your city latitude")
    print("       'lon': 77.2090       # Your city longitude")
    print("   }")
    print("\n   Find your coordinates at: https://www.latlong.net/")

def main():
    """Run all tests"""
    print("\n" + "🌟"*30)
    print("  GURU API - TESTING SCRIPT")
    print("  Beginner Friendly Guide")
    print("🌟"*30)
    
    # Run tests
    results = []
    results.append(("Health Check", test_health_check()))
    
    if results[0][1]:  # Only continue if server is running
        results.append(("Root Endpoint", test_root_endpoint()))
        results.append(("Kundli GET", test_kundli_simple()))
        results.append(("Kundli POST", test_kundli_post()))
        test_with_your_details()
    else:
        print("\n⚠️  Server is not running. Please start it first:")
        print("   uvicorn src.main:app --reload")
        return
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()

