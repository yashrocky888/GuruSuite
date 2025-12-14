#!/usr/bin/env python3
"""
Quick Test Script for Phase 13: Kundli Matching
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test birth details
BOY = {
    "dob": "1990-05-15",
    "time": "10:30",
    "lat": 12.97,
    "lon": 77.59
}

GIRL = {
    "dob": "1992-08-20",
    "time": "14:45",
    "lat": 12.97,
    "lon": 77.59
}

def test_matching():
    """Test all matching endpoints."""
    print("="*70)
    print("  PHASE 13: KUNDLI MATCHING - QUICK TEST")
    print("="*70)
    
    print(f"\n📅 Test Birth Details:")
    print(f"   Boy: {BOY['dob']} {BOY['time']}")
    print(f"   Girl: {GIRL['dob']} {GIRL['time']}")
    
    # Test 1: Gun Milan
    print(f"\n🔍 Test 1: Gun Milan (36 Points)")
    print(f"   URL: {BASE_URL}/match/gunas")
    try:
        params = {
            "boy_dob": BOY["dob"],
            "boy_time": BOY["time"],
            "boy_lat": BOY["lat"],
            "boy_lon": BOY["lon"],
            "girl_dob": GIRL["dob"],
            "girl_time": GIRL["time"],
            "girl_lat": GIRL["lat"],
            "girl_lon": GIRL["lon"]
        }
        response = requests.get(f"{BASE_URL}/match/gunas", params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            print(f"   ✅ Success!")
            print(f"   Total Score: {result.get('total', 0)}/36")
            print(f"   Percentage: {result.get('percentage', 0)}%")
            print(f"   Verdict: {result.get('verdict', 'N/A')}")
            print(f"   Nadi: {result.get('nadi', {}).get('score', 0)}/8")
            print(f"   Bhakoot: {result.get('bhakoot', {}).get('score', 0)}/7")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Porutham
    print(f"\n🔍 Test 2: Porutham (10 Checks)")
    print(f"   URL: {BASE_URL}/match/porutham")
    try:
        response = requests.get(f"{BASE_URL}/match/porutham", params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            print(f"   ✅ Success!")
            print(f"   Score: {result.get('score', 0)}/10")
            print(f"   Percentage: {result.get('percentage', 0)}%")
            print(f"   Verdict: {result.get('verdict', 'N/A')}")
            print(f"   Rajju: {result.get('rajju', {}).get('compatible', False)}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Advanced Compatibility
    print(f"\n🔍 Test 3: Advanced Compatibility")
    print(f"   URL: {BASE_URL}/match/advanced")
    try:
        response = requests.get(f"{BASE_URL}/match/advanced", params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            print(f"   ✅ Success!")
            print(f"   Overall Index: {result.get('overall_index', 0)}/100")
            print(f"   Emotional Match: {result.get('emotional_match', 0)}/100")
            print(f"   Communication Match: {result.get('communication_match', 0)}/100")
            print(f"   Moon Distance: {result.get('moon_distance', {}).get('compatibility', 'N/A')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Full Report
    print(f"\n🔍 Test 4: Full Match Report")
    print(f"   URL: {BASE_URL}/match/full-report")
    try:
        response = requests.get(f"{BASE_URL}/match/full-report", params={**params, "include_ai": "true"}, timeout=60)
        if response.status_code == 200:
            data = response.json()
            match_data = data.get("match_data", {})
            overall = match_data.get("overall", {})
            print(f"   ✅ Success!")
            print(f"   Overall Score: {overall.get('score', 0)}/100")
            print(f"   Verdict: {overall.get('verdict', 'N/A')}")
            print(f"   Recommendation: {overall.get('recommendation', 'N/A')[:60]}...")
            
            # Check AI report
            ai_report = data.get("ai_report", {})
            if ai_report and not ai_report.get("error"):
                print(f"   ✅ AI Report included")
                print(f"   Summary: {ai_report.get('summary', 'N/A')[:60]}...")
            else:
                print(f"   ⚠️  AI Report: {ai_report.get('error', 'Not available')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   - Gun Milan: North Indian system (36 points)")
    print("   - Porutham: South Indian system (10 checks)")
    print("   - Full Report: Complete analysis with AI interpretation")
    print("   - Test in browser: http://localhost:8000/docs")

if __name__ == "__main__":
    test_matching()

