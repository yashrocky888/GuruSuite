# Prokerala 1:1 Verification Report - D24-D60
## API-Only Verification (NO UI CHANGES)

**Date:** 2024-12-19  
**Status:** ⚠️ VERIFICATION REQUIRED  
**Scope:** API calculations only (`apps/guru-api/src/jyotish/varga_drik.py`)

---

## VERIFICATION METHODOLOGY

### Test Birth Data (Standard Reference)
```
Date: 1995-05-16
Time: 18:38 IST
Place: Bangalore (12.9716°N, 77.5946°E)
Ayanamsa: Lahiri
```

### D1 Reference Data
```
Ascendant: Vrishchika (Scorpio) - 212.2799° (sign_index: 7)
Moon: Vrishchika (Scorpio) - 235.2501° (sign_index: 7)
Sun: Vrishabha (Taurus) - 51.4200° (sign_index: 1)
```

### Verification Checklist
For EACH varga (D24, D27, D30, D40, D45, D60):
- [ ] Ascendant sign matches Prokerala
- [ ] Moon sign matches Prokerala
- [ ] Sun sign matches Prokerala
- [ ] 2-3 additional planets match Prokerala

---

## D24 — CHATURVIMSHAMSA (SIDDHAMSA)

### Current Implementation
**File:** `apps/guru-api/src/jyotish/varga_drik.py` (lines 209-233, 658-695)

**Formula:**
```python
# Step 1: Calculate division index
amsa_size = 30.0 / 24.0  # 1.25° per division
amsa_index = floor(degree_in_sign / 1.25)

# Step 2: Determine start sign
if sign_index % 2 == 1:  # Odd sign
    start_sign = 4  # Leo (Simha)
else:  # Even sign
    start_sign = 0  # Aries (Mesha)

# Step 3: Calculate D24 sign
d24_sign_index = (start_sign + amsa_index) % 12
```

**Classical Source:** Brihat Parashara Hora Shastra (BPHS)  
**Prokerala Match:** ✅ CLAIMED (needs verification)

**Test Case (D1 Ascendant: Scorpio 212.2799°):**
- D1 sign: Scorpio (index 7, ODD)
- Degree in sign: 212.2799 % 30 = 2.2799°
- Division index: floor(2.2799 / 1.25) = 1
- Start sign: Leo (4) [because sign_index 7 is ODD]
- D24 sign: (4 + 1) % 12 = 5 (Virgo)

**Expected Prokerala Output:** ❓ NEEDS VERIFICATION

**Verification Status:** ⚠️ FORMULA IMPLEMENTED, AWAITING PROKERALA COMPARISON

---

## D27 — SAPTAVIMSAMSA (BHAMSA)

### Current Implementation
**File:** `apps/guru-api/src/jyotish/varga_drik.py` (lines 235-253, 697-712)

**Formula:**
```python
# Method 1: Calibration lookup (if available)
calibrated_sign = get_varga_sign_from_calibration(sign_index, amsa_index, "D27")

# Method 2: Fallback formula
varga_longitude = (planet_longitude * 27.0) % 360.0
varga_sign_index = floor(varga_longitude / 30.0)
```

**Classical Source:** BPHS (Nakshatra-based progression)  
**Prokerala Match:** ❓ UNKNOWN (uses calibration lookup)

**Test Case (D1 Ascendant: Scorpio 212.2799°):**
- Varga longitude: (212.2799 * 27) % 360 = 331.5573°
- D27 sign: floor(331.5573 / 30) = 11 (Pisces)

**Expected Prokerala Output:** ❓ NEEDS VERIFICATION

**Verification Status:** ✅ CLASSICAL PARASHARA FORMULA IMPLEMENTED — AWAITING PROKERALA VERIFICATION

**Note:** Calibration lookup removed. Now uses classical Parashara formula: `(sign_index * 27 + amsa_index) % 12` for nakshatra-based progression.

---

## D30 — TRIMSAMSA

### Current Implementation
**File:** `apps/guru-api/src/jyotish/varga_drik.py` (lines 255-273)

**Formula:**
```python
# Method 1: Calibration lookup (if available)
calibrated_sign = get_varga_sign_from_calibration(sign_index, amsa_index, "D30")

# Method 2: Fallback formula
result_0based = (sign_index * 30 + amsa_index) % 12
```

**Classical Source:** BPHS (Odd/even forward/reverse logic)  
**Prokerala Match:** ❓ UNKNOWN (uses calibration lookup)

**Test Case (D1 Ascendant: Scorpio 212.2799°):**
- Degree in sign: 2.2799°
- Division index: floor(2.2799 / 1.0) = 2
- D30 sign: (7 * 30 + 2) % 12 = 212 % 12 = 8 (Sagittarius)

**Expected Prokerala Output:** ❓ NEEDS VERIFICATION

**Verification Status:** ✅ CLASSICAL PARASHARA FORMULA IMPLEMENTED — AWAITING PROKERALA VERIFICATION

**Note:** Calibration lookup removed. Now uses classical Parashara formula: odd signs forward, even signs reverse.

---

## D40 — CHATVARIMSAMSA (KHAVEDAMSA)

### Current Implementation
**File:** `apps/guru-api/src/jyotish/varga_drik.py` (lines 275-293, 714-729)

**Formula:**
```python
# Method 1: Calibration lookup (if available)
calibrated_sign = get_varga_sign_from_calibration(sign_index, amsa_index, "D40")

# Method 2: Fallback formula
varga_longitude = (planet_longitude * 40.0) % 360.0
varga_sign_index = floor(varga_longitude / 30.0)
```

**Classical Source:** BPHS (Similar to D10 pattern)  
**Prokerala Match:** ❓ UNKNOWN (uses calibration lookup)

**Test Case (D1 Ascendant: Scorpio 212.2799°):**
- Varga longitude: (212.2799 * 40) % 360 = 91.196°
- D40 sign: floor(91.196 / 30) = 3 (Cancer)

**Expected Prokerala Output:** ❓ NEEDS VERIFICATION

**Verification Status:** ✅ CLASSICAL PARASHARA FORMULA IMPLEMENTED — AWAITING PROKERALA VERIFICATION

**Note:** Calibration lookup removed. Now uses D10/D16 pattern (movable/fixed/dual + parity).

---

## D45 — AKSHAVEDAMSA

### Current Implementation
**File:** `apps/guru-api/src/jyotish/varga_drik.py` (lines 295-313, 731-745)

**Formula:**
```python
# Method 1: Calibration lookup (if available)
calibrated_sign = get_varga_sign_from_calibration(sign_index, amsa_index, "D45")

# Method 2: Fallback formula
varga_longitude = (planet_longitude * 45.0) % 360.0
varga_sign_index = floor(varga_longitude / 30.0)
```

**Classical Source:** BPHS (Element-based starting signs, similar to D24)  
**Prokerala Match:** ❓ UNKNOWN (uses calibration lookup)

**Test Case (D1 Ascendant: Scorpio 212.2799°):**
- Varga longitude: (212.2799 * 45) % 360 = 152.5955°
- D45 sign: floor(152.5955 / 30) = 5 (Virgo)

**Expected Prokerala Output:** ❓ NEEDS VERIFICATION

**Verification Status:** ✅ CLASSICAL PARASHARA FORMULA IMPLEMENTED — AWAITING PROKERALA VERIFICATION

**Note:** Calibration lookup removed. Now uses D10/D16 pattern (movable/fixed/dual + parity).

---

## D60 — SHASHTIAMSHA

### Current Implementation
**File:** `apps/guru-api/src/jyotish/varga_drik.py` (lines 315-331, 746-760)

**Formula:**
```python
# Step 1: Calculate division index
amsa_size = 30.0 / 60.0  # 0.5° per division
amsa_index = floor(degree_in_sign / 0.5)

# Step 2: D60 sign index = division_index % 12
d60_sign_index = amsa_index % 12
```

**Classical Source:** Classical Parashara (Prokerala standard)  
**Prokerala Match:** ✅ CLAIMED (needs verification)

**Test Case (D1 Ascendant: Scorpio 212.2799°):**
- Degree in sign: 2.2799°
- Division index: floor(2.2799 / 0.5) = 4
- D60 sign: 4 % 12 = 4 (Leo)

**Expected Prokerala Output:** ❓ NEEDS VERIFICATION

**Verification Status:** ⚠️ FORMULA IMPLEMENTED, AWAITING PROKERALA COMPARISON

---

## VERIFICATION WORKFLOW

### Step 1: Get Prokerala Reference Data
1. Visit: https://www.prokerala.com/astrology/divisional-charts.php
2. Enter test birth data: 1995-05-16, 18:38 IST, Bangalore
3. Extract for each varga (D24, D27, D30, D40, D45, D60):
   - Ascendant sign
   - Moon sign
   - Sun sign
   - 2-3 additional planets

### Step 2: Compare with GuruSuite API
1. Call GuruSuite API with same birth data
2. Extract varga chart data for D24-D60
3. Compare sign-by-sign:
   - Ascendant sign
   - Moon sign
   - Sun sign
   - Other planets

### Step 3: Document Mismatches
For each mismatch:
- Document expected (Prokerala) vs actual (GuruSuite)
- Identify which formula step is incorrect
- Note the classical source rule

### Step 4: Fix in API Only
- **File to modify:** `apps/guru-api/src/jyotish/varga_drik.py`
- **Function to modify:** `calculate_varga_sign()` or `calculate_varga()`
- **DO NOT modify:** UI components, rendering logic, or frontend

### Step 5: Re-verify
- Run same test birth data
- Confirm all signs match Prokerala
- Update this document with ✅ VERIFIED status

---

## CURRENT STATUS SUMMARY

| Varga | Formula Type | Classical Source | Prokerala Match | Status |
|-------|-------------|------------------|-----------------|--------|
| D24 | Classical Parashara (odd/even) | BPHS | ⚠️ Needs verification | Formula implemented |
| D27 | Calibration lookup + fallback | BPHS | ⚠️ Needs verification | Uses lookup table |
| D30 | Calibration lookup + fallback | BPHS | ⚠️ Needs verification | Uses lookup table |
| D40 | Calibration lookup + fallback | BPHS | ⚠️ Needs verification | Uses lookup table |
| D45 | Calibration lookup + fallback | BPHS | ⚠️ Needs verification | Uses lookup table |
| D60 | Classical Parashara (modulo) | Classical Parashara | ⚠️ Needs verification | Formula implemented |

---

## NEXT ACTIONS

1. **IMMEDIATE:** Get Prokerala reference data for test birth chart
2. **COMPARE:** Run GuruSuite API and compare outputs
3. **FIX:** Update formulas in `varga_drik.py` if mismatches found
4. **VERIFY:** Re-test and confirm 100% match
5. **LOCK:** Mark as ✅ PROKERALA VERIFIED once confirmed

---

## IMPORTANT NOTES

- **NO UI CHANGES:** All fixes must be in API only
- **SINGLE SOURCE OF TRUTH:** API is authoritative, UI only renders
- **CLASSICAL SOURCE:** All formulas must trace to BPHS or standard Parashara
- **PROKERALA DEFAULT:** Match Prokerala's default mode (not alternative modes)

---

**Last Updated:** 2024-12-19  
**Next Review:** After Prokerala reference data obtained

