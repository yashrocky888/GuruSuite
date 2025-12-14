#!/usr/bin/env python3
"""
Comprehensive Test Script for Phase 3: Vimshottari Dasha Engine

This script tests the Dasha API endpoint thoroughly.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_dasha_endpoint():
    """Test the GET /dasha endpoint."""
    print_section("Test 1: GET /dasha Endpoint")
    
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    print(f"📅 Testing with:")
    print(f"   Date: {params['dob']}")
    print(f"   Time: {params['time']}")
    print(f"   Location: {params['lat']}, {params['lon']} (Bangalore)")
    
    try:
        response = requests.get(f"{BASE_URL}/dasha", params=params, timeout=10)
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information
            print(f"\n📊 Response Data:")
            print(f"   Julian Day: {data.get('julian_day', 'N/A')}")
            print(f"   Moon Degree: {data.get('moon_degree', 0):.4f}°")
            
            dasha = data.get('dasha', {})
            print(f"\n   Nakshatra: {dasha.get('nakshatra', 'N/A')}")
            print(f"   Nakshatra Index: {dasha.get('nakshatra_index', 'N/A')}")
            print(f"   Nakshatra Lord: {dasha.get('nakshatra_lord', 'N/A')}")
            
            mahadashas = dasha.get('mahadasha', [])
            print(f"\n   Mahadashas: {len(mahadashas)} periods")
            total_years = sum(m['total_years'] for m in mahadashas)
            print(f"   Total Cycle: {total_years:.1f} years")
            
            print(f"\n   First 3 Mahadashas:")
            for i, m in enumerate(mahadashas[:3], 1):
                print(f"     {i}. {m['lord']:8s}: {m['years']:6.2f} years ({m['start'][:10]} to {m['end'][:10]})")
            
            # Test antardashas
            antardashas = dasha.get('antardasha_years', {})
            if antardashas:
                first_lord = mahadashas[0]['lord']
                first_antardashas = antardashas.get(first_lord, {})
                print(f"\n   Antardashas for {first_lord} Mahadasha (sample):")
                for lord, years in list(first_antardashas.items())[:5]:
                    print(f"     {lord:8s}: {years:6.2f} years")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server!")
        print("   Make sure the server is running:")
        print("   uvicorn src.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_different_birth_details():
    """Test with different birth details."""
    print_section("Test 2: Different Birth Details")
    
    test_cases = [
        {
            "name": "Delhi",
            "dob": "1990-01-15",
            "time": "10:30",
            "lat": 28.6139,
            "lon": 77.2090
        },
        {
            "name": "Mumbai",
            "dob": "1985-06-20",
            "time": "14:45",
            "lat": 19.0760,
            "lon": 72.8777
        }
    ]
    
    results = []
    for test in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/dasha", params=test, timeout=10)
            if response.status_code == 200:
                data = response.json()
                dasha = data.get('dasha', {})
                mahadashas = dasha.get('mahadasha', [])
                total_years = sum(m['total_years'] for m in mahadashas)
                
                print(f"✅ {test['name']}:")
                print(f"   Nakshatra: {dasha.get('nakshatra')}")
                print(f"   Nakshatra Lord: {dasha.get('nakshatra_lord')}")
                print(f"   First Mahadasha: {mahadashas[0]['lord']} ({mahadashas[0]['years']:.2f} years)")
                print(f"   Total Cycle: {total_years:.1f} years")
                results.append(True)
            else:
                print(f"❌ {test['name']}: Failed (Status {response.status_code})")
                results.append(False)
        except Exception as e:
            print(f"❌ {test['name']}: Error - {e}")
            results.append(False)
    
    return all(results)

def test_validation():
    """Test response validation."""
    print_section("Test 3: Response Validation")
    
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    try:
        response = requests.get(f"{BASE_URL}/dasha", params=params, timeout=10)
        data = response.json()
        dasha = data.get('dasha', {})
        mahadashas = dasha.get('mahadasha', [])
        antardashas = dasha.get('antardasha_years', {})
        
        checks = []
        
        # Check 1: Julian Day
        checks.append(("Julian Day present", data.get('julian_day') is not None))
        
        # Check 2: Moon degree
        moon_deg = data.get('moon_degree', -1)
        checks.append(("Moon degree valid", 0 <= moon_deg <= 360))
        
        # Check 3: Nakshatra
        checks.append(("Nakshatra name present", dasha.get('nakshatra') is not None))
        checks.append(("Nakshatra index valid", 0 <= dasha.get('nakshatra_index', -1) <= 26))
        checks.append(("Nakshatra lord present", dasha.get('nakshatra_lord') is not None))
        
        # Check 4: Mahadashas
        checks.append(("9 Mahadashas", len(mahadashas) == 9))
        total_years = sum(m['total_years'] for m in mahadashas)
        checks.append(("120-year cycle", abs(total_years - 120.0) < 0.1))
        
        # Check 5: Antardashas
        checks.append(("Antardashas present", len(antardashas) > 0))
        checks.append(("All mahadashas have antardashas", len(antardashas) == 9))
        
        # Check 6: Date formats
        checks.append(("Start dates valid", all('start' in m for m in mahadashas)))
        checks.append(("End dates valid", all('end' in m for m in mahadashas)))
        
        # Print results
        for check_name, result in checks:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status}: {check_name}")
        
        passed = sum(1 for _, r in checks if r)
        total = len(checks)
        print(f"\n   Validation: {passed}/{total} checks passed")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def test_error_handling():
    """Test error handling."""
    print_section("Test 4: Error Handling")
    
    # Test invalid date format
    try:
        response = requests.get(f"{BASE_URL}/dasha", params={
            "dob": "invalid-date",
            "time": "18:38",
            "lat": 12.97,
            "lon": 77.59
        }, timeout=10)
        
        if response.status_code == 400:
            print("✅ Invalid date format handled correctly")
            print(f"   Error message: {response.json().get('detail', 'N/A')[:60]}")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "🌟"*35)
    print("  PHASE 3: VIMSHOTTARI DASHA ENGINE - TEST SUITE")
    print("🌟"*35)
    
    results = []
    results.append(("Dasha Endpoint", test_dasha_endpoint()))
    results.append(("Different Birth Details", test_different_birth_details()))
    results.append(("Response Validation", test_validation()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print(f"\n   Overall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Dasha Engine is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

