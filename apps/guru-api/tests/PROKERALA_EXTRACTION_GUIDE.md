# Prokerala Data Extraction Guide

## Overview

This guide explains how to extract Prokerala reference data for the golden verification tests.

## Reference Birth Data (SINGLE SOURCE OF TRUTH)

- **DOB:** 1995-05-16
- **Time:** 18:38 IST (18:38:00)
- **Place:** Bangalore (12.9716°N, 77.5946°E)
- **Ayanamsa:** Lahiri

## Step-by-Step Extraction Process

### 1. Navigate to Prokerala.com

Go to: https://www.prokerala.com/astrology/birth-chart/

### 2. Enter Birth Data

- **Date:** 16 May 1995
- **Time:** 18:38
- **Place:** Bangalore, Karnataka, India
- **Ayanamsa:** Lahiri (verify this is selected)

### 3. For Each Varga Chart

Navigate to the divisional chart section and select each varga:

- D1 (Rashi) - Main chart
- D2 (Hora)
- D3 (Drekkana)
- D4 (Chaturthamsa)
- D7 (Saptamsa)
- D9 (Navamsa)
- D10 (Dasamsa)
- D12 (Dwadasamsa)
- D16 (Shodasamsa)
- D20 (Vimshamsa)
- D24 (Chaturvimsamsa)
- D27 (Saptavimsamsa)
- D30 (Trimsamsa)
- D40 (Chatvarimsamsa)
- D45 (Panchavimsamsa)
- D60 (Shashtiamsa)

### 4. Extract Data for Each Planet

For **EACH** planet (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu) and **Ascendant**, extract:

1. **Sign Name** (e.g., "Scorpio", "Cancer")
2. **House Number** (1-12)
3. **Degrees** (0-29)
4. **Minutes** (0-59)
5. **Seconds** (0-59)

**Example:**
- Planet: Sun
- Sign: Scorpio
- House: 8
- Degree: 12
- Minute: 30
- Second: 0

### 5. Populate JSON File

Open the corresponding JSON file in `tests/prokerala_reference/` (e.g., `D10.json`) and fill in the data:

```json
{
  "Planets": {
    "Sun": {
      "sign": "Scorpio",
      "sign_index": 7,
      "house": 8,
      "degree": 12,
      "minute": 30,
      "second": 0,
      "degrees_in_sign": 12.5
    }
  }
}
```

**Important Notes:**
- `sign_index`: 0=Aries, 1=Taurus, 2=Gemini, 3=Cancer, 4=Leo, 5=Virgo, 6=Libra, 7=Scorpio, 8=Sagittarius, 9=Capricorn, 10=Aquarius, 11=Pisces
- `degrees_in_sign`: Convert DMS to decimal: `degree + minute/60.0 + second/3600.0`
- `house`: Must be 1-12 (Whole Sign system)
- Ascendant house is ALWAYS 1

### 6. Verification Checklist

After populating each JSON file:

- [ ] All planets have sign name
- [ ] All planets have sign_index (0-11)
- [ ] All planets have house (1-12)
- [ ] All planets have degree, minute, second
- [ ] Ascendant house is 1
- [ ] degrees_in_sign is calculated correctly
- [ ] Birth data matches reference (1995-05-16, 18:38 IST, Bangalore)

### 7. Cross-Check with JHora (Optional)

If you have access to JHora software:
1. Enter the same birth data
2. Generate the same varga chart
3. Compare results with Prokerala
4. If there are discrepancies, note them in the JSON file's "note" field

## Common Issues

### Issue: Prokerala shows different house numbers

**Solution:** Verify you're using Whole Sign house system. In Prokerala, check the house system setting.

### Issue: Sign index mismatch

**Solution:** Double-check the sign name to index mapping:
- Aries = 0
- Taurus = 1
- Gemini = 2
- Cancer = 3
- Leo = 4
- Virgo = 5
- Libra = 6
- Scorpio = 7
- Sagittarius = 8
- Capricorn = 9
- Aquarius = 10
- Pisces = 11

### Issue: DMS values don't match

**Solution:** 
- Ensure you're reading the exact values (no rounding)
- Check if Prokerala shows seconds (some may only show degrees and minutes)
- Verify the ayanamsa is set to Lahiri

## Testing After Population

Once you've populated a JSON file:

```bash
cd apps/guru-api
pytest tests/test_golden_verification.py::test_d10_prokerala_golden -v
```

Replace `d10` with the varga you're testing.

## Priority Order

If you can't populate all vargas at once, prioritize:

1. **D10** (Dasamsa) - Already partially populated
2. **D9** (Navamsa) - Most commonly used
3. **D7** (Saptamsa) - Important for relationships
4. **D12** (Dwadasamsa) - Important for parents
5. **D3** (Drekkana) - Important for siblings
6. **D4** (Chaturthamsa) - Important for property
7. **D2** (Hora) - Important for wealth
8. **D16, D20, D24, D27, D30, D40, D45, D60** - Less commonly used but still important

## Final Lock

Once ALL varga tests pass:
- Add lock comment to verified varga formulas:
  ```python
  # 🔒 GOLDEN VERIFIED — PROKERALA + JHORA
  ```
- Freeze varga engine logic permanently
- Document any known discrepancies in the JSON files
