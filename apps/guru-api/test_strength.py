#!/usr/bin/env python3
"""
Comprehensive Test Script for Phase 5: Shadbala + Ashtakavarga

This script tests both strength calculation endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_shadbala():
    """Test the Shadbala endpoint."""
    print_section("Test 1: Shadbala Calculation")
    
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    try:
        response = requests.get(f"{BASE_URL}/strength/shadbala", params=params, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            shadbala = data.get('shadbala', {})
            
            print(f"\n📊 Shadbala Results:")
            print(f"   Planets calculated: {len(shadbala)}")
            
            # Check all 6 balas are present
            required_balas = ['naisargika_bala', 'cheshta_bala', 'sthana_bala', 
                            'dig_bala', 'kala_bala', 'drik_bala', 'total_shadbala']
            
            print(f"\n   Breakdown for each planet:")
            for planet, balas in shadbala.items():
                print(f"\n   {planet}:")
                for bala_name in required_balas:
                    value = balas.get(bala_name, 0)
                    print(f"     {bala_name:20s}: {value:6.2f}")
            
            # Validation
            checks = []
            checks.append(("All 6 balas present", all(
                all(b in balas for b in required_balas) 
                for balas in shadbala.values()
            )))
            checks.append(("Naisargika values correct", all(
                balas.get('naisargika_bala', 0) > 0 
                for balas in shadbala.values()
            )))
            checks.append(("Total shadbala calculated", all(
                balas.get('total_shadbala', 0) > 0 
                for balas in shadbala.values()
            )))
            
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

def test_ashtakavarga():
    """Test the Ashtakavarga endpoint."""
    print_section("Test 2: Ashtakavarga Calculation")
    
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.97,
        "lon": 77.59
    }
    
    try:
        response = requests.get(f"{BASE_URL}/strength/ashtakavarga", params=params, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ashtakavarga = data.get('ashtakavarga', {})
            
            print(f"\n📊 Ashtakavarga Results:")
            bav = ashtakavarga.get('BAV', {})
            sav = ashtakavarga.get('SAV', {})
            
            print(f"   BAV Planets: {len(bav)}")
            print(f"   SAV Total: {ashtakavarga.get('SAV_total', 0)}")
            print(f"   SAV Average: {ashtakavarga.get('SAV_average', 0)}")
            
            print(f"\n   SAV (Sarvashtakavarga) - House Bindus:")
            for i in range(1, 13):
                house_key = f"house_{i}"
                bindus = sav.get(house_key, 0)
                print(f"     House {i:2d}: {bindus:2d} bindus")
            
            print(f"\n   BAV Sample - Sun:")
            if 'Sun' in bav:
                sun_bav = bav['Sun']
                print(f"     {sun_bav}")
            
            # Validation
            checks = []
            checks.append(("BAV present", len(bav) > 0))
            checks.append(("SAV present", len(sav) == 12))
            checks.append(("All houses have bindus", all(
                sav.get(f"house_{i}", -1) >= 0 
                for i in range(1, 13)
            )))
            checks.append(("BAV has 12 houses each", all(
                len(bav[planet]) == 12 
                for planet in bav.keys()
            )))
            
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

def main():
    """Run all tests."""
    print("\n" + "🌟"*35)
    print("  PHASE 5: SHADBALA + ASHTAKAVARGA - TEST SUITE")
    print("🌟"*35)
    
    results = []
    results.append(("Shadbala", test_shadbala()))
    results.append(("Ashtakavarga", test_ashtakavarga()))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print(f"\n   Overall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Strength calculations are working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

