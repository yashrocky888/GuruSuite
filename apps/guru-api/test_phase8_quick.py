#!/usr/bin/env python3
"""
Quick Test Script for Phase 8: AI Guru Interpretation Layer
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

def test_ai_daily():
    """Test AI daily prediction endpoint."""
    print("="*70)
    print("  PHASE 8: AI GURU INTERPRETATION - QUICK TEST")
    print("="*70)
    
    print(f"\n📅 Testing with birth details:")
    print(f"   Date: {BIRTH_DETAILS['dob']}")
    print(f"   Time: {BIRTH_DETAILS['time']}")
    print(f"   Location: {BIRTH_DETAILS['lat']}, {BIRTH_DETAILS['lon']}")
    
    # Test 1: AI Daily Prediction
    print(f"\n🔍 Test 1: AI Daily Prediction")
    print(f"   URL: {BASE_URL}/ai/daily")
    print(f"   ⚠️  Note: This requires OpenAI API key or Ollama running")
    try:
        response = requests.get(f"{BASE_URL}/ai/daily", params=BIRTH_DETAILS, timeout=60)
        if response.status_code == 200:
            data = response.json()
            prediction = data.get('prediction', {})
            print(f"   ✅ Success!")
            print(f"   AI Used: {prediction.get('ai_used', 'unknown')}")
            print(f"   Summary: {prediction.get('summary', 'N/A')}")
            print(f"   Lucky Color: {prediction.get('lucky_color', 'N/A')}")
            print(f"   Best Time: {prediction.get('best_time', 'N/A')}")
            print(f"   Planet in Focus: {prediction.get('planet_in_focus', 'N/A')}")
            print(f"   Energy Rating: {prediction.get('energy_rating', 0)}/100")
            print(f"\n   What to Do:")
            for item in prediction.get('what_to_do', [])[:3]:
                print(f"     • {item}")
            print(f"\n   What to Avoid:")
            for item in prediction.get('what_to_avoid', [])[:2]:
                print(f"     • {item}")
            print(f"\n   Morning Message:")
            print(f"     {prediction.get('morning_message', 'N/A')[:100]}...")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"   ⚠️  Request timed out (AI may be processing)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Note: AI endpoint may work but needs OpenAI API key or Ollama")
    
    # Test 2: AI Morning Message
    print(f"\n🔍 Test 2: AI Morning Message")
    print(f"   URL: {BASE_URL}/ai/morning")
    try:
        response = requests.get(f"{BASE_URL}/ai/morning", params=BIRTH_DETAILS, timeout=30)
        if response.status_code == 200:
            data = response.json()
            morning = data.get('morning_message', {})
            print(f"   ✅ Success!")
            print(f"   Blessing: {morning.get('blessing', 'N/A')}")
            print(f"   Lucky Color: {morning.get('lucky_color', 'N/A')}")
            print(f"   Focus: {morning.get('focus', 'N/A')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   - AI endpoints work with OpenAI API key (set OPENAI_API_KEY env var)")
    print("   - Or use local Ollama: ollama serve (then set use_local=true)")
    print("   - Without AI, endpoints return default structured responses")
    print("   - Test in browser: http://localhost:8000/docs")

if __name__ == "__main__":
    test_ai_daily()

