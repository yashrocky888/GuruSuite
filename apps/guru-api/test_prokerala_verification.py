#!/usr/bin/env python3
"""
Test API output against Prokerala ground truth data.
Birth: 16-05-1995, 18:38 IST, Bangalore (Lahiri)
"""

import requests
import json

# Prokerala Ground Truth Data
PROKERALA_TRUTH = {
    "D24": {
        "Ascendant": "Leo",      # index 4
        "Sun": "Leo",            # index 4
        "Moon": "Aries",         # index 0
        "Mars": "Virgo",         # index 5
        "Mercury": "Sagittarius", # index 8
        "Jupiter": "Virgo",      # index 5
        "Venus": "Sagittarius",  # index 8
        "Saturn": "Gemini",      # index 2
        "Rahu": "Pisces",        # index 11
        "Ketu": "Pisces",        # index 11
    },
    "D27": {
        "Ascendant": "Pisces",   # index 11
        "Sun": "Leo",            # index 4
        "Moon": "Scorpio",       # index 7
        "Mars": "Gemini",        # index 2
        "Mercury": "Aquarius",   # index 10
        "Jupiter": "Taurus",     # index 1
        "Venus": "Virgo",        # index 5
        "Saturn": "Sagittarius", # index 8
        "Rahu": "Cancer",        # index 3
        "Ketu": "Capricorn",     # index 9
    },
    "D30": {
        "Ascendant": "Taurus",   # index 1
        "Sun": "Taurus",         # index 1
        "Moon": "Scorpio",       # index 7
        "Mars": "Aries",         # index 0
        "Mercury": "Capricorn",  # index 9
        "Jupiter": "Pisces",     # index 11
        "Venus": "Aquarius",     # index 10
        "Saturn": "Libra",       # index 6
        "Rahu": "Sagittarius",   # index 8
        "Ketu": "Sagittarius",   # index 8
    },
    "D40": {
        "Ascendant": "Capricorn", # index 9
        "Sun": "Sagittarius",    # index 8
        "Moon": "Aries",         # index 0
        "Mars": "Capricorn",     # index 9
        "Mercury": "Pisces",     # index 11
        "Jupiter": "Libra",      # index 6
        "Venus": "Sagittarius",  # index 8
        "Saturn": "Gemini",      # index 2
        "Rahu": "Taurus",        # index 1
        "Ketu": "Taurus",        # index 1
    },
    "D45": {
        "Ascendant": "Scorpio",  # index 7
        "Sun": "Libra",          # index 6
        "Moon": "Virgo",         # index 5
        "Mars": "Scorpio",       # index 7
        "Mercury": "Taurus",     # index 1
        "Jupiter": "Sagittarius", # index 8
        "Venus": "Sagittarius",  # index 8
        "Saturn": "Pisces",      # index 11
        "Rahu": "Leo",           # index 4
        "Ketu": "Leo",           # index 4
    },
    "D60": {
        "Ascendant": "Pisces",   # index 11
        "Sun": "Cancer",         # index 3
        "Moon": "Capricorn",     # index 9
        "Mars": "Sagittarius",   # index 8
        "Mercury": "Capricorn",  # index 9
        "Jupiter": "Sagittarius", # index 8
        "Venus": "Pisces",       # index 11
        "Saturn": "Scorpio",     # index 7
        "Rahu": "Cancer",        # index 3
        "Ketu": "Capricorn",     # index 9
    },
}

# Sign name to index mapping
SIGN_TO_INDEX = {
    "Aries": 0, "Taurus": 1, "Gemini": 2, "Cancer": 3,
    "Leo": 4, "Virgo": 5, "Libra": 6, "Scorpio": 7,
    "Sagittarius": 8, "Capricorn": 9, "Aquarius": 10, "Pisces": 11
}

def test_api_against_prokerala():
    """Test API output against Prokerala ground truth"""
    
    api_url = "https://guru-api-660206747784.asia-south1.run.app/api/v1/kundli"
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    }
    
    print("=" * 80)
    print("🧪 PROKERALA VERIFICATION TEST")
    print("=" * 80)
    print(f"\n📅 Birth Data: {params['dob']} {params['time']} IST")
    print(f"🌐 API URL: {api_url}\n")
    
    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract kundli data
        kundli = data.get("data", {}).get("kundli", {})
        if not kundli:
            kundli = data
        
        total_mismatches = 0
        total_tests = 0
        
        for varga in ["D24", "D27", "D30", "D40", "D45", "D60"]:
            if varga not in kundli:
                print(f"\n❌ {varga} not found in API response")
                continue
            
            chart = kundli[varga]
            prokerala = PROKERALA_TRUTH[varga]
            
            print(f"\n{'=' * 80}")
            print(f"📊 {varga} VERIFICATION")
            print(f"{'=' * 80}")
            
            mismatches = []
            matches = []
            
            # Check Ascendant
            asc_prokerala = prokerala["Ascendant"]
            asc_api = chart.get("Ascendant", {})
            asc_api_sign = asc_api.get("sign_sanskrit") or asc_api.get("sign", "")
            asc_api_index = asc_api.get("sign_index", -1)
            asc_prokerala_index = SIGN_TO_INDEX.get(asc_prokerala, -1)
            
            total_tests += 1
            if asc_api_index == asc_prokerala_index:
                matches.append(f"Ascendant: {asc_prokerala} ✅")
            else:
                mismatches.append(f"Ascendant: Expected {asc_prokerala} (index {asc_prokerala_index}), Got {asc_api_sign} (index {asc_api_index}) ❌")
                total_mismatches += 1
            
            # Check Planets
            planets = chart.get("Planets", {})
            for planet_name, prokerala_sign in prokerala.items():
                if planet_name == "Ascendant":
                    continue
                
                planet_data = planets.get(planet_name, {})
                api_sign = planet_data.get("sign_sanskrit") or planet_data.get("sign", "")
                api_index = planet_data.get("sign_index", -1)
                prokerala_index = SIGN_TO_INDEX.get(prokerala_sign, -1)
                
                total_tests += 1
                if api_index == prokerala_index:
                    matches.append(f"{planet_name}: {prokerala_sign} ✅")
                else:
                    mismatches.append(f"{planet_name}: Expected {prokerala_sign} (index {prokerala_index}), Got {api_sign} (index {api_index}) ❌")
                    total_mismatches += 1
            
            # Print results
            if matches:
                print("\n✅ MATCHES:")
                for match in matches:
                    print(f"   {match}")
            
            if mismatches:
                print("\n❌ MISMATCHES:")
                for mismatch in mismatches:
                    print(f"   {mismatch}")
            
            if not mismatches:
                print(f"\n🎉 {varga}: 100% MATCH WITH PROKERALA!")
            else:
                match_rate = (len(matches) / (len(matches) + len(mismatches))) * 100
                print(f"\n⚠️  {varga}: {match_rate:.1f}% match ({len(matches)}/{len(matches) + len(mismatches)})")
        
        print(f"\n{'=' * 80}")
        print(f"📊 OVERALL RESULTS")
        print(f"{'=' * 80}")
        print(f"Total Tests: {total_tests}")
        print(f"Total Mismatches: {total_mismatches}")
        print(f"Match Rate: {((total_tests - total_mismatches) / total_tests * 100):.1f}%")
        
        if total_mismatches == 0:
            print("\n🎉 ALL VARGA CHARTS MATCH PROKERALA 100%!")
        else:
            print(f"\n⚠️  {total_mismatches} mismatches found. Formulas need correction.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_against_prokerala()

