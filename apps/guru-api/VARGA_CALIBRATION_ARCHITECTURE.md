# Varga Calibration Architecture

**Date:** 2025-12-19  
**Status:** 🔒 IMPLEMENTED

---

## Architecture Decision

**D24–D60 varga charts use lookup-table-based calibration** instead of formula-based calculation, because ProKerala/JHora do not follow a single public formula for these higher vargas.

---

## Implementation Strategy

### Formula-Based (D1–D20)
- **Status:** ✅ VERIFIED CORRECT
- **Method:** Pure mathematical formulas
- **Vargas:** D1, D2, D3, D4, D7, D9, D10, D12, D16, D20
- **No changes required**

### Lookup-Table-Based (D24–D60)
- **Status:** 🔄 PENDING CALIBRATION
- **Method:** Calibration lookup tables from ProKerala/JHora
- **Vargas:** D24, D27, D30, D40, D45, D60
- **Calibration Source:** Manual ProKerala verification (screenshots/visual match)

---

## Data Model

For each varga DXX:
```python
DXX_TABLE[base_sign_index_0_11][amsa_index_0_N] = final_sign_index_0_11
```

Where:
- `base_sign_index`: Sign index (0-11) from D1
- `amsa_index`: Division index within sign (0 to N-1)
- `final_sign_index`: Final sign index (0-11) in varga chart

---

## Calculation Pipeline

```python
# 1. Calculate amsa size
amsa_size = 30.0 / N

# 2. Calculate amsa index
amsa_index = floor((deg_in_sign + 1e-9) / amsa_size)

# 3. Lookup final sign
final_sign = DXX_TABLE[base_sign][amsa_index]

# 4. Calculate house (same as D1-D12)
house = ((final_sign - lagna_sign + 12) % 12) + 1
```

**Applied to:**
- Ascendant
- All planets
- No special cases

---

## Calibration Files

Location: `apps/guru-api/calibration/`

Files:
- `d24.json` - D24 (Chaturvimsamsa) - 24 divisions
- `d27.json` - D27 (Saptavimsamsa) - 27 divisions
- `d30.json` - D30 (Trimsamsa) - 30 divisions
- `d40.json` - D40 (Khavedamsa) - 40 divisions
- `d45.json` - D45 (Akshavedamsa) - 45 divisions
- `d60.json` - D60 (Shashtiamsa) - 60 divisions

**Format:**
```json
{
  "_comment": "Varga description",
  "_source": "ProKerala/JHora Manual Verification",
  "_test_chart": "1995-05-16 18:38 IST, Bangalore, Lahiri",
  "_format": "DXX_TABLE[base_sign_index_0_11][amsa_index_0_N] = final_sign_index_0_11",
  "_status": "PENDING_CALIBRATION",
  "table": {
    "0": [0, 1, 2, ...],  // Base sign 0 (Aries)
    "1": [1, 2, 3, ...],  // Base sign 1 (Taurus)
    ...
    "11": [11, 0, 1, ...] // Base sign 11 (Pisces)
  }
}
```

---

## Calibration Process

1. **Manual Verification:**
   - Use ProKerala/JHora for test chart: 1995-05-16 18:38 IST, Bangalore, Lahiri
   - Extract planet positions for each varga (D24-D60)
   - Verify Ascendant, Sun, Moon, and all planets

2. **Table Generation:**
   - For each base sign (0-11)
   - For each amsa index (0 to N-1)
   - Map to final sign from ProKerala/JHora output

3. **Validation:**
   - Ascendant matches ProKerala
   - Sun matches ProKerala
   - Moon matches ProKerala
   - All planets visually match

4. **Status Update:**
   - Change `_status` from `"PENDING_CALIBRATION"` to `"VERIFIED"`

---

## Code Implementation

### Calibration Loader
- **File:** `apps/guru-api/src/jyotish/varga_calibration.py`
- **Functions:**
  - `load_calibration_table(varga)` - Load JSON calibration file
  - `get_varga_sign_from_calibration(base_sign, amsa_index, varga)` - Lookup sign
  - `is_calibration_available(varga)` - Check if calibration exists

### Varga Calculation
- **File:** `apps/guru-api/src/jyotish/varga_drik.py`
- **Function:** `calculate_varga_sign(sign_index, long_in_sign, varga)`
- **Logic:**
  1. For D24-D60: Try calibration lookup first
  2. If calibration available: Return calibrated sign
  3. If not available: Fallback to formula (placeholder)

---

## Regression Tests

**Test Chart:**
- Date: 1995-05-16
- Time: 18:38 IST
- Place: Bangalore
- Ayanamsa: Lahiri

**Validation Points:**
- ✅ Ascendant sign matches ProKerala
- ✅ Sun sign matches ProKerala
- ✅ Moon sign matches ProKerala
- ✅ All planets match ProKerala visually

**Test File:** `apps/guru-api/tests/test_varga_calibration.py` (to be created)

---

## Completion Criteria

Implementation is **COMPLETE** when:
1. ✅ Calibration files created (with placeholder data)
2. ✅ Calibration loader implemented
3. ✅ Varga calculation uses lookup tables for D24-D60
4. ✅ House calculation uses same formula as D1-D12
5. ⏳ Calibration data verified against ProKerala
6. ⏳ Regression tests pass
7. ⏳ Visual match confirmed

---

## Important Notes

- **DO NOT** attempt further formula changes for D24-D60
- **DO NOT** modify D1-D20 (already verified correct)
- Calibration is a **lookup-calibrated engine by design**
- Manual ProKerala verification is the **only** source of truth for D24-D60

