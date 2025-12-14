# D10 (Dasamsa) Testing Guide

## Quick Start

### 1. Run Pytest Tests (Recommended)

```bash
cd apps/guru-api

# Run all D10 golden tests
pytest tests/test_d10_golden.py -v

# Run original D10 accuracy test
pytest tests/test_varga_accuracy.py::test_d10_dasamsa -v

# Run all D10 tests together
pytest tests/test_d10_golden.py tests/test_varga_accuracy.py::test_d10_dasamsa -v

# Run with detailed output
pytest tests/test_d10_golden.py -v --tb=short
```

**Expected Output:**
```
============================= test session starts ==============================
tests/test_d10_golden.py::test_d10_golden[test_case0] PASSED
tests/test_d10_golden.py::test_d10_golden[test_case1] PASSED
...
tests/test_d10_golden.py::test_d10_all_divisions PASSED
======================== 15 passed in 0.08s =========================
```

---

### 2. Test Via API Endpoint

#### Start the API Server

```bash
cd apps/guru-api
python -m uvicorn src.main:app --reload --port 8000
```

#### Test with curl

```bash
# Test the original verification case
curl "http://localhost:8000/api/v1/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata" \
  | jq '.D10'

# Expected D10 results:
# - Ascendant: Karka (Cancer, sign 4)
# - Venus: Kumbha (Aquarius, sign 11)
# - Mars: Meena (Pisces, sign 12)
```

#### Test with Python requests

```python
import requests
import json

url = "http://localhost:8000/api/v1/kundli"
params = {
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.9716,
    "lon": 77.5946,
    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params)
data = response.json()

print("D10 Ascendant:", data["D10"]["ascendant_sign_sanskrit"])
print("D10 Venus:", data["D10"]["planets"]["Venus"]["sign"])
print("D10 Mars:", data["D10"]["planets"]["Mars"]["sign"])
```

---

### 3. Manual Python Test Script

Create a test file `test_d10_manual.py`:

```python
#!/usr/bin/env python3
"""Manual D10 test script"""

from datetime import datetime
from src.utils.timezone import local_to_utc
import swisseph as swe
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.varga_drik import calculate_varga

# Test case: DOB 1995-05-16, 18:38 IST, Bangalore
birth_date = datetime(1995, 5, 16, 18, 38, 0)
birth_dt_utc = local_to_utc(birth_date, 'Asia/Kolkata')
jd = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
                birth_dt_utc.hour + birth_dt_utc.minute/60.0, swe.GREG_CAL)

# Generate kundli
kundli = generate_kundli(jd, 12.9716, 77.5946)

# Expected D10 signs (Prokerala reference)
expected = {
    "Ascendant": 4,   # Cancer (Karka)
    "Sun": 8,          # Scorpio (Vrischika)
    "Moon": 9,         # Sagittarius (Dhanu)
    "Mercury": 12,     # Pisces (Meena)
    "Venus": 11,       # Aquarius (Kumbha)
    "Mars": 12,        # Pisces (Meena)
    "Jupiter": 8,      # Scorpio (Vrischika)
    "Saturn": 8,       # Scorpio (Vrischika)
    "Rahu": 8,         # Scorpio (Vrischika)
    "Ketu": 4,         # Cancer (Karka)
}

print("=" * 70)
print("D10 MANUAL TEST - Bangalore 1995-05-16 18:38 IST")
print("=" * 70)
print()

# Test Ascendant
asc_d1 = kundli["Ascendant"]["degree"]
asc_d10 = calculate_varga(asc_d1, 10)
asc_sign_1 = asc_d10["sign"] + 1
match = "✓" if asc_sign_1 == expected["Ascendant"] else "✗"
print(f"Ascendant: {asc_d10['sign_name']} (sign {asc_sign_1}) - Expected: {expected['Ascendant']} {match}")

# Test Planets
for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]:
    d1_deg = kundli["Planets"][planet]["degree"]
    d10_result = calculate_varga(d1_deg, 10)
    got_sign_1 = d10_result["sign"] + 1
    exp_sign_1 = expected[planet]
    match = "✓" if got_sign_1 == exp_sign_1 else "✗"
    print(f"{planet:8s}: {d10_result['sign_name']:12s} (sign {got_sign_1:2d}) - Expected: {exp_sign_1:2d} {match}")

print()
print("=" * 70)
```

Run it:
```bash
cd apps/guru-api
python3 test_d10_manual.py
```

---

### 4. Verify Against Prokerala

1. Go to: https://www.prokerala.com/astrology/divisional-charts.php
2. Enter birth details:
   - Date: 1995-05-16
   - Time: 18:38
   - Place: Bangalore, India
3. Check D10 (Dasamsa) chart
4. Compare with API results

**Expected Matches:**
- Ascendant: Cancer (Karka)
- Venus: Aquarius (Kumbha)
- Mars: Pisces (Meena)
- All planets should match exactly

---

### 5. Test Different Birth Charts

Use the golden test cases from `tests/test_d10_golden.py`:

```python
# Example: Test Mumbai case
from datetime import datetime
from src.utils.timezone import local_to_utc
import swisseph as swe
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.varga_drik import calculate_varga

birth_date = datetime(1990, 1, 15, 10, 30, 0)
birth_dt_utc = local_to_utc(birth_date, 'Asia/Kolkata')
jd = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
                birth_dt_utc.hour + birth_dt_utc.minute/60.0, swe.GREG_CAL)

kundli = generate_kundli(jd, 19.0760, 72.8777)  # Mumbai

# Check D10 for any planet
venus_d10 = calculate_varga(kundli["Planets"]["Venus"]["degree"], 10)
print(f"Venus D10: {venus_d10['sign_name']} (sign {venus_d10['sign'] + 1})")
```

---

## Test Coverage

The golden tests cover:
- ✅ 12 different birth charts (various locations, times, timezones)
- ✅ Boundary degrees (0°, 3°, 6°, 9°, etc.)
- ✅ Odd/even sign mappings
- ✅ All 10 divisions (0-9)
- ✅ Original verification case (Bangalore 1995-05-16)

---

## Troubleshooting

### Tests Fail
- Check that Swiss Ephemeris is properly installed
- Verify timezone handling is correct
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### API Returns Wrong Results
- Verify the API is using the latest code
- Check that `varga_drik.py` has the correct D10 formula
- Ensure corrections are applied correctly

### Results Don't Match Prokerala
- Verify birth data is exactly the same (date, time, location)
- Check ayanamsa is set to Lahiri
- Ensure timezone conversion is correct

---

## Quick Test Command

```bash
# One-liner to test D10
cd apps/guru-api && pytest tests/test_d10_golden.py::test_d10_golden -k "test_case0" -v
```

This tests the original verification case (Bangalore 1995-05-16).

