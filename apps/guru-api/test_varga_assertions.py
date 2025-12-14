#!/usr/bin/env python3
"""
Test varga chart assertions - verify house = sign for all planets
"""

import requests
import json
import sys

def test_varga_assertions(api_url: str = None):
    """Test that all varga charts enforce house = sign"""
    
    if api_url is None:
        api_url = "https://guru-api-wytsvpr2eq-uc.a.run.app"
    
    birth_data = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    }
    
    print("=" * 80)
    print("🧪 VARGA CHART ASSERTION TEST")
    print("=" * 80)
    print(f"\n📅 Birth Data: {birth_data['dob']} {birth_data['time']} IST")
    print(f"🌐 API URL: {api_url}")
    
    try:
        response = requests.get(
            f"{api_url}/kundli",
            params=birth_data,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        varga_charts = ["D2", "D3", "D4", "D7", "D9", "D10", "D12"]
        all_pass = True
        errors = []
        
        for chart_type in varga_charts:
            if chart_type not in data:
                continue
            
            chart_data = data[chart_type]
            planets = chart_data.get("planets", {})
            ascendant_house = chart_data.get("ascendant_house")
            ascendant_sign_sanskrit = chart_data.get("ascendant_sign_sanskrit") or chart_data.get("ascendant_sign")
            
            print(f"\n📊 Testing {chart_type}:")
            
            # Test ascendant
            if ascendant_house is not None:
                # Get ascendant sign index from sign name
                sign_map = {
                    "Mesha": 1, "Vrishabha": 2, "Mithuna": 3, "Karka": 4,
                    "Simha": 5, "Kanya": 6, "Tula": 7, "Vrishchika": 8, "Vrischika": 8,
                    "Dhanu": 9, "Makara": 10, "Kumbha": 11, "Meena": 12
                }
                asc_sign_num = sign_map.get(ascendant_sign_sanskrit, 0)
                expected_asc_house = asc_sign_num
                
                if ascendant_house != expected_asc_house:
                    print(f"   ❌ Ascendant: house ({ascendant_house}) != sign ({expected_asc_house})")
                    all_pass = False
                    errors.append(f"{chart_type} Ascendant: house={ascendant_house}, sign={expected_asc_house}")
                else:
                    print(f"   ✅ Ascendant: {ascendant_sign_sanskrit} → House {ascendant_house} [house == sign]")
            
            # Test each planet
            for planet_name, planet_data in planets.items():
                planet_house = planet_data.get("house")
                planet_sign_index = planet_data.get("sign_index")
                
                if planet_sign_index is None or planet_house is None:
                    continue
                
                expected_house = planet_sign_index + 1
                
                if planet_house != expected_house:
                    print(f"   ❌ {planet_name}: house ({planet_house}) != sign ({expected_house})")
                    all_pass = False
                    errors.append(f"{chart_type} {planet_name}: house={planet_house}, sign={expected_house}")
                else:
                    print(f"   ✅ {planet_name}: House {planet_house} [house == sign]")
        
        print("\n" + "=" * 80)
        if all_pass:
            print("✅ ALL ASSERTIONS PASSED - house == sign for all varga charts")
            print("=" * 80)
            return True
        else:
            print("❌ ASSERTION FAILURES FOUND")
            print("=" * 80)
            print("\n📋 Errors:")
            for error in errors:
                print(f"   • {error}")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    api_url = sys.argv[1] if len(sys.argv) > 1 else None
    success = test_varga_assertions(api_url)
    sys.exit(0 if success else 1)

