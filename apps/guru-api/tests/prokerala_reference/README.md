# Prokerala Reference Data

This directory contains immutable JSON snapshots of Prokerala reference data for golden verification tests.

## Reference Birth Data (Single Source of Truth)

- **DOB:** 1995-05-16
- **Time:** 18:38 IST
- **Place:** Bangalore (12.9716°N, 77.5946°E)
- **Ayanamsa:** Lahiri

## File Structure

Each varga has a corresponding JSON file:
- `D1.json` - Rashi (main chart)
- `D2.json` - Hora
- `D3.json` - Drekkana
- `D4.json` - Chaturthamsa
- `D7.json` - Saptamsa
- `D9.json` - Navamsa
- `D10.json` - Dasamsa
- `D12.json` - Dwadasamsa
- `D16.json` - Shodasamsa
- `D20.json` - Vimshamsa
- `D24.json` - Chaturvimsamsa
- `D27.json` - Saptavimsamsa
- `D30.json` - Trimsamsa
- `D40.json` - Chatvarimsamsa
- `D45.json` - Panchavimsamsa
- `D60.json` - Shashtiamsa

## JSON Format

Each JSON file follows this structure:

```json
{
  "varga_type": "D10",
  "birth_data": {
    "dob": "1995-05-16",
    "time": "18:38:00",
    "timezone": "Asia/Kolkata",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "ayanamsa": "Lahiri"
  },
  "Ascendant": {
    "sign": "Cancer",
    "sign_index": 3,
    "house": 1,
    "degree": 25,
    "minute": 15,
    "second": 0,
    "degrees_in_sign": 25.25
  },
  "Planets": {
    "Sun": {
      "sign": "Scorpio",
      "sign_index": 7,
      "house": 8,
      "degree": 12,
      "minute": 30,
      "second": 0,
      "degrees_in_sign": 12.5
    },
    ...
  }
}
```

## Extraction Instructions

1. Go to Prokerala.com
2. Enter birth data: 1995-05-16, 18:38 IST, Bangalore
3. Select the varga chart (e.g., D10 Dasamsa)
4. Extract for EACH planet:
   - Sign name (e.g., "Scorpio")
   - House number (1-12)
   - Degrees, minutes, seconds (exact values)
5. Populate the corresponding JSON file
6. Verify against JHora if available

## Verification Rules

- **NO ROUNDING:** Use exact degrees, minutes, seconds from Prokerala
- **NO ASSUMPTIONS:** If data is missing, mark as null and investigate
- **IMMUTABLE:** Once verified, these files are NEVER changed
- **CODE FIXES ONLY:** If tests fail, fix the code, NOT the JSON files
