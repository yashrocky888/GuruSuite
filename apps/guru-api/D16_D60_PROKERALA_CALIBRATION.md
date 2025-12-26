# D16-D60 Prokerala/JHora Calibration Guide

## Status: ⚠️ NEEDS PROKERALA REFERENCE DATA

**Current State:**
- D1-D12: ✅ VERIFIED - Match Prokerala/JHora exactly
- D16-D60: ⚠️ IMPLEMENTED with BPHS rules, but need Prokerala calibration

## Problem Statement

Prokerala/JHora use a **refined Drik Siddhānta implementation** that differs from raw BPHS textbook rules for higher vargas (D16-D60). The current implementation uses BPHS formulas, but Prokerala/JHora may use:

1. **Ascendant re-derivation** - Special handling for ascendant calculation
2. **Correct sign start offsets** - Refined offset calculations beyond textbook
3. **Proper odd/even handling** - Consistent parity logic
4. **Movable/Fixed/Dual logic** - Refined nature-based rules
5. **Consistent modulo math** - Normalization steps
6. **Carry-forward normalization** - Additional correction steps

## Current Implementation

### D16 (Shodasamsa)
- **Pattern:** Uses D10 pattern (movable/fixed/dual + parity)
- **Formula:** `(sign_index + start_offset + div_index) % 12`
- **Current Output (Test Data):** Leo (sign_index: 4)
- **Prokerala Expected:** ❓ NEEDS VERIFICATION

### D20 (Vimsamsa)
- **Pattern:** Uses D12 pattern (forward progression)
- **Formula:** `((rasi_sign - 1 + div_index) % 12) + 1`
- **Current Output (Test Data):** Sagittarius (sign_index: 8)
- **Prokerala Expected:** ❓ NEEDS VERIFICATION

### D24 (Chaturvimsamsa)
- **Pattern:** Element-based starting signs
- **Formula:** `(start_sign + div_index) % 12`
- **Current Output (Test Data):** Leo (sign_index: 4)
- **Prokerala Expected:** ❓ NEEDS VERIFICATION

### D27 (Saptavimsamsa)
- **Pattern:** Nakshatra-based progression
- **Formula:** `(sign_index * 27 + div_index) % 12`
- **Current Output (Test Data):** Pisces (sign_index: 11)
- **Prokerala Expected:** ❓ NEEDS VERIFICATION

### D30 (Trimsamsa)
- **Pattern:** Odd/even forward/reverse
- **Formula:** Odd: `(sign_index + div_index) % 12`, Even: `(sign_index - div_index) % 12`
- **Current Output (Test Data):** Virgo (sign_index: 5)
- **Prokerala Expected:** ❓ NEEDS VERIFICATION

### D40 (Khavedamsa)
- **Pattern:** Uses D10 pattern (movable/fixed/dual + parity)
- **Formula:** `(sign_index + start_offset + div_index) % 12`
- **Current Output (Test Data):** Libra (sign_index: 6)
- **Prokerala Expected:** ❓ NEEDS VERIFICATION

### D45 (Akshavedamsa)
- **Pattern:** Element-based starting signs (same as D24)
- **Formula:** `(start_sign + div_index) % 12`
- **Current Output (Test Data):** Libra (sign_index: 6)
- **Prokerala Expected:** ❓ NEEDS VERIFICATION

### D60 (Shashtiamsa)
- **Pattern:** Uses D10 pattern (movable/fixed/dual + parity)
- **Formula:** `(sign_index + start_offset + div_index) % 12`
- **Current Output (Test Data):** Scorpio (sign_index: 7)
- **Prokerala Expected:** ❓ NEEDS VERIFICATION

## Test Data

**Birth Details:**
- Date: 1995-05-16
- Time: 18:38 IST
- Location: Bangalore (12.9716°N, 77.5946°E)
- Ayanamsa: Lahiri

**D1 Reference:**
- Ascendant: Vrishchika (Scorpio) - 212.2799°
- Moon: Vrishchika (Scorpio) - 235.2501°
- Rahu: Tula (Libra) - 190.7944°

## Calibration Steps

1. **Get Prokerala/JHora Reference Data:**
   - For each varga (D16-D60), get exact sign placements for:
     - Ascendant
     - Moon
     - Rahu
     - All other planets (optional but recommended)

2. **Update Golden Test Suite:**
   - File: `tests/test_varga_prokerala_d16_d60_golden.py`
   - Fill in `PROKERALA_REFERENCE` dictionary with actual values

3. **Refine Formulas:**
   - Compare current output with Prokerala
   - Identify discrepancies
   - Adjust formulas to match Prokerala exactly
   - Apply same refinements as D10/D12 (if applicable)

4. **Verify All Planets:**
   - Not just Ascendant, Moon, Rahu
   - All 9 planets must match Prokerala

5. **Lock Implementation:**
   - Once verified, add `🔒 PROKERALA + JHORA VERIFIED` comments
   - Mark as GOLD STANDARD

## Files to Update

1. `src/jyotish/varga_drik.py` - Core varga calculation logic
2. `tests/test_varga_prokerala_d16_d60_golden.py` - Golden test suite
3. This file - Update with verified results

## Next Steps

**IMMEDIATE ACTION REQUIRED:**
1. Get Prokerala/JHora output for test birth data (1995-05-16 18:38 Bangalore)
2. Update `PROKERALA_REFERENCE` in golden test file
3. Run tests to identify mismatches
4. Refine formulas to match exactly
5. Verify and lock implementation

---

**Note:** The current implementation follows BPHS rules and uses the same structural patterns as D10/D12. However, Prokerala/JHora may use refined rules that require calibration with actual reference data.

