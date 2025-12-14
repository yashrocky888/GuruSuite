#!/usr/bin/env python3
"""
Fetch Kundli JSON from API
Usage: python fetch_kundli.py [user_id]
"""

import sys
import json
import requests

API_BASE_URL = "http://localhost:8000"

def fetch_kundli_json(user_id=None):
    """Fetch kundli JSON from API"""
    url = f"{API_BASE_URL}/api/v1/kundli"
    params = {"user_id": user_id} if user_id else {}
    
    try:
        print(f"🌐 Fetching kundli from: {url}")
        print(f"📋 Parameters: {params}")
        print("")
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print("✅ Complete API Response:")
        print("=" * 80)
        print(json.dumps(data, indent=2))
        print("=" * 80)
        
        # Summary
        if data.get("success"):
            kundli = data.get("data", {}).get("kundli", {})
            print("\n📊 Response Summary:")
            print(f"  Success: {data.get('success')}")
            if kundli.get("Ascendant"):
                asc = kundli["Ascendant"]
                print(f"  Ascendant: {asc.get('sign_sanskrit', 'N/A')} {asc.get('degree', 0):.4f}°")
            print(f"  Planets: {len(kundli.get('Planets', {}))} planets")
            print(f"  Houses: {len(kundli.get('Houses', []))} houses")
            print(f"  System: {kundli.get('system', 'N/A')}")
            print(f"  Ayanamsa: {kundli.get('ayanamsa', 'N/A')}")
            
            # Divisional charts
            divisional_charts = [k for k in kundli.keys() if k.startswith('D')]
            if divisional_charts:
                print(f"  Divisional Charts: {', '.join(divisional_charts)}")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching kundli: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            try:
                print(f"Response data: {e.response.text}")
            except:
                pass
        return None

if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "test"
    fetch_kundli_json(user_id)

