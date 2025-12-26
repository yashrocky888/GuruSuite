# PHASE 8 — GOLDEN VERIFICATION SETUP COMPLETE

## ✅ What Was Created

### 1. Prokerala Reference Directory Structure
- **Location:** `tests/prokerala_reference/`
- **Files Created:**
  - `README.md` - Directory documentation
  - `D1.json` through `D60.json` - JSON template files for all 16 varga types
  - `D10.json` - Partially populated with known reference data

### 2. Golden Verification Test Suite
- **Location:** `tests/test_golden_verification.py`
- **Features:**
  - Loads Prokerala reference data from JSON files
  - Compares API output against Prokerala for ALL vargas
  - Exact comparison: Sign name, House number, Degrees+Minutes+Seconds
  - Automatic test generation for all varga types
  - Skips tests when reference data is incomplete
  - Tolerance: 1 arcsecond for DMS comparison

### 3. Prokerala Extraction Guide
- **Location:** `tests/PROKERALA_EXTRACTION_GUIDE.md`
- **Contents:**
  - Step-by-step instructions for extracting data from Prokerala
  - JSON file format documentation
  - Common issues and solutions
  - Priority order for populating vargas

### 4. Varga Engine Updates
- **Location:** `src/jyotish/varga_drik.py`
- **Changes:**
  - Added D20 (Vimshamsa) to main `calculate_varga()` function
  - Added D30 (Trimsamsa) to main `calculate_varga()` function
  - Both now use the unified varga calculation path

## 📋 Test Structure

### Test Functions Generated
For each varga type (D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60):
- `test_d{N}_prokerala_golden()` - Main verification test

### Additional Tests
- `test_all_vargas_have_reference_files()` - Verifies JSON files exist
- `test_reference_data_structure()` - Validates JSON structure

## 🔍 Verification Process

### Step 1: Populate Prokerala Reference Data
1. Go to Prokerala.com
2. Enter birth data: 1995-05-16, 18:38 IST, Bangalore
3. For each varga, extract:
   - Sign name
   - Sign index (0-11)
   - House number (1-12)
   - Degrees, minutes, seconds
4. Populate corresponding JSON file

### Step 2: Run Tests
```bash
cd apps/guru-api
pytest tests/test_golden_verification.py -v
```

### Step 3: Fix Mismatches
- If ANY test fails:
  1. Identify which rule/formula caused the mismatch
  2. Fix ONLY that rule in `varga_drik.py`
  3. Re-run ALL previous varga tests
  4. NEVER change the JSON files to match code

### Step 4: Lock Verified Formulas
Once ALL tests pass:
- Add lock comment to verified formulas:
  ```python
  # 🔒 GOLDEN VERIFIED — PROKERALA + JHORA
  ```
- Freeze varga engine logic permanently

## 📊 Current Status

### ✅ Completed
- [x] Directory structure created
- [x] JSON template files created for all vargas
- [x] Golden verification test suite created
- [x] Prokerala extraction guide created
- [x] D20 and D30 added to main calculate_varga() function
- [x] D10 reference data partially populated

### ⏳ Pending
- [ ] Populate Prokerala reference data for all vargas
- [ ] Run golden tests and fix any mismatches
- [ ] Add lock comments to verified formulas
- [ ] Final verification and documentation

## 🎯 Next Steps

1. **Extract Prokerala Data:**
   - Start with D10 (already partially done)
   - Then D9, D7, D12 (most commonly used)
   - Then remaining vargas

2. **Run Tests:**
   ```bash
   pytest tests/test_golden_verification.py::test_d10_prokerala_golden -v
   ```

3. **Fix Any Mismatches:**
   - Identify the formula causing the issue
   - Fix in `varga_drik.py`
   - Re-run tests

4. **Lock System:**
   - Once all tests pass, add lock comments
   - Document any known discrepancies

## 📝 Important Notes

### NON-NEGOTIABLE RULES
1. **Tests are NEVER changed to match code**
2. **Code is ALWAYS changed to match Prokerala**
3. **No "close enough"** - exact match required
4. **No averaging** - use exact values
5. **No fallback logic** - fix the root cause

### Reference Data Format
Each JSON file contains:
```json
{
  "varga_type": "D10",
  "birth_data": {...},
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
    "Sun": {...},
    "Moon": {...},
    ...
  }
}
```

### Sign Index Mapping
- 0 = Aries
- 1 = Taurus
- 2 = Gemini
- 3 = Cancer
- 4 = Leo
- 5 = Virgo
- 6 = Libra
- 7 = Scorpio
- 8 = Sagittarius
- 9 = Capricorn
- 10 = Aquarius
- 11 = Pisces

## 🔒 Final Lock Criteria

The varga engine will be locked when:
1. ✅ ALL varga tests pass (D1-D60)
2. ✅ ALL planets verified (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu, Ascendant)
3. ✅ Sign names match exactly
4. ✅ House numbers match exactly
5. ✅ Degrees+Minutes+Seconds match within 1 arcsecond tolerance
6. ✅ Lock comments added to all verified formulas

---

**Status:** Framework ready. Awaiting Prokerala data population.
