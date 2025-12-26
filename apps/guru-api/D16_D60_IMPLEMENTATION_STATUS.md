# D16-D60 Implementation Status

## ⚠️ CRITICAL: Needs Prokerala/JHora Reference Data for Verification

**Current Status:** Implementation complete using BPHS rules and D10/D12 patterns, but **requires Prokerala/JHora reference data** to verify correctness.

## Implementation Summary

All D16-D60 vargas have been implemented following the same structural patterns as D10/D12:

1. **D16, D40, D60:** Use D10 pattern (movable/fixed/dual + parity logic)
2. **D20:** Uses D12 pattern (forward progression)
3. **D24, D45:** Use element-based starting signs
4. **D27:** Uses nakshatra-based progression
5. **D30:** Uses odd/even forward/reverse logic

## Current Test Results

**Test Data:** 1995-05-16, 18:38 IST, Bangalore
**D1 Ascendant:** Vrishchika (Scorpio) - 212.2799°

| Varga | Ascendant Sign | Sign Index | Status |
|-------|---------------|------------|--------|
| D16   | Leo           | 4          | ⚠️ Needs Prokerala verification |
| D20   | Sagittarius   | 8          | ⚠️ Needs Prokerala verification |
| D24   | Leo           | 4          | ⚠️ Needs Prokerala verification |
| D27   | Pisces        | 11         | ⚠️ Needs Prokerala verification |
| D30   | Virgo         | 5          | ⚠️ Needs Prokerala verification |
| D40   | Libra         | 6          | ⚠️ Needs Prokerala verification |
| D45   | Libra         | 6          | ⚠️ Needs Prokerala verification |
| D60   | Scorpio       | 7          | ⚠️ Needs Prokerala verification |

## Next Steps

**REQUIRED ACTION:**
1. Obtain Prokerala/JHora output for test birth data
2. Compare with current implementation
3. Refine formulas to match exactly
4. Update golden tests
5. Lock implementation

**Files Ready for Calibration:**
- `src/jyotish/varga_drik.py` - Core calculation logic
- `tests/test_varga_prokerala_d16_d60_golden.py` - Golden test framework
- `scripts/test_d16_d60_current.py` - Current output generator

---

**Note:** The implementation follows verified D10/D12 patterns and BPHS rules. However, Prokerala/JHora may use refined Drik Siddhānta rules that require calibration with actual reference outputs.

