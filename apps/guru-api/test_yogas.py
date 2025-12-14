#!/usr/bin/env python3
"""
Comprehensive Test Script for Phase 6: Yogas Engine

This script tests all yoga detection endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_all_yogas():
    """Test the /yogas/all endpoint."""
    print_section("Test 1: All Yogas Detection")
    
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    try:
        response = requests.get(f"{BASE_URL}/yogas/all", params=params, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            yogas = data.get('yogas', {})
            
            print(f"\n📊 Yoga Analysis:")
            print(f"   Total Yogas: {yogas.get('total_yogas', 0)}")
            print(f"   Major Yogas: {len(yogas.get('major_yogas', []))}")
            print(f"   Moderate Yogas: {len(yogas.get('moderate_yogas', []))}")
            print(f"   Doshas: {len(yogas.get('doshas', []))}")
            
            print(f"\n   By Type:")
            by_type = yogas.get('by_type', {})
            for yoga_type, yoga_list in by_type.items():
                print(f"     {yoga_type}: {len(yoga_list)}")
            
            print(f"\n   Sample Major Yogas:")
            for yoga in yogas.get('major_yogas', [])[:5]:
                print(f"     - {yoga.get('name', 'Unknown')} ({yoga.get('type', 'Unknown')})")
            
            # Validation
            checks = []
            checks.append(("Total yogas > 0", yogas.get('total_yogas', 0) > 0))
            checks.append(("Major yogas present", len(yogas.get('major_yogas', [])) > 0))
            checks.append(("By type structure present", len(by_type) > 0))
            
            print(f"\n   Validation:")
            for check_name, result in checks:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"     {status}: {check_name}")
            
            return all(r for _, r in checks)
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_major_yogas():
    """Test the /yogas/major endpoint."""
    print_section("Test 2: Major Yogas Only")
    
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    try:
        response = requests.get(f"{BASE_URL}/yogas/major", params=params, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            major_yogas = data.get('major_yogas', [])
            
            print(f"\n📊 Major Yogas:")
            print(f"   Count: {data.get('count', 0)}")
            
            for yoga in major_yogas[:10]:
                print(f"   - {yoga.get('name', 'Unknown')}")
            
            return len(major_yogas) > 0
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_planetary_yogas():
    """Test the /yogas/planetary endpoint."""
    print_section("Test 3: Planetary Yogas")
    
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    try:
        response = requests.get(f"{BASE_URL}/yogas/planetary", params=params, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            planetary_yogas = data.get('planetary_yogas', [])
            
            print(f"\n📊 Planetary Yogas:")
            print(f"   Count: {data.get('count', 0)}")
            
            for yoga in planetary_yogas:
                print(f"   - {yoga.get('name', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_house_yogas():
    """Test the /yogas/house endpoint."""
    print_section("Test 4: House-Based Yogas")
    
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    try:
        response = requests.get(f"{BASE_URL}/yogas/house", params=params, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            house_yogas = data.get('house_yogas', [])
            
            print(f"\n📊 House-Based Yogas:")
            print(f"   Count: {data.get('count', 0)}")
            
            for yoga in house_yogas[:10]:
                print(f"   - {yoga.get('name', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "🌟"*35)
    print("  PHASE 6: YOGAS ENGINE - TEST SUITE")
    print("🌟"*35)
    
    results = []
    results.append(("All Yogas", test_all_yogas()))
    results.append(("Major Yogas", test_major_yogas()))
    results.append(("Planetary Yogas", test_planetary_yogas()))
    results.append(("House Yogas", test_house_yogas()))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print(f"\n   Overall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Yogas Engine is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

