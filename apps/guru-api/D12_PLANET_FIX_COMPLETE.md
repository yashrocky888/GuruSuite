# D12 Planet Position Fix - Complete

## Problem
D12 chart was showing incorrect planet positions:
- **Mercury**: Showing "Aries" instead of "Capricorn (Makara)"
- **Saturn**: Showing "Pisces" instead of "Capricorn (Makara)"
- **All planets**: Incorrect signs due to wrong D12 calculation formula

## Root Cause
The D12 planet calculation was applying a **+3 correction** that was incorrect. The base formula `(sign_index + div_index) % 12` already gives the correct answer, so no correction is needed.

## API Fix Applied

### File: `src/jyotish/varga_drik.py`

**Before:**
```python
# Applied +3 correction to all planets (except Sun which got +5)
temp_sign = (start + div_index) % 12
temp_sign = (temp_sign + 3) % 12  # ❌ WRONG CORRECTION
```

**After:**
```python
# Base formula is correct - no correction needed
temp_sign = (start + div_index) % 12  # ✅ CORRECT
return temp_sign
```

### Result

**Before Fix:**
- Mercury D12: Aries (sign 0) ❌
- Saturn D12: Pisces (sign 11) ❌

**After Fix:**
- Mercury D12: Capricorn (Makara, sign 9) ✅
- Saturn D12: Capricorn (Makara, sign 9) ✅

## All D12 Planet Positions (Fixed)

| Planet   | D1 Sign    | D12 Sign      | D12 Longitude | Status |
|----------|------------|---------------|---------------|--------|
| Sun      | Taurus     | Taurus        | 47.03°        | ✅     |
| Moon     | Scorpio    | Virgo         | 153.00°       | ✅     |
| Mercury  | Taurus     | **Capricorn** | 295.45°       | ✅ **FIXED** |
| Venus    | Aries      | Gemini        | 68.39°        | ✅     |
| Mars     | Leo        | Leo           | 147.04°       | ✅     |
| Jupiter  | Scorpio    | Gemini        | 74.21°        | ✅     |
| Saturn   | Aquarius   | **Capricorn** | 286.80°       | ✅ **FIXED** |
| Rahu     | Libra      | Aquarius      | 320.79°       | ✅     |
| Ketu     | Aries      | Leo           | 140.79°       | ✅     |

## House Assignments

In South Indian chart (fixed sign grid):
- **House 10 = Makara (Capricorn)**
- Mercury and Saturn are now correctly in Capricorn sign
- They will be displayed in House 10 (Makara) ✅

## Deployment

**Status:** ✅ Deployed
**Service URL:** `https://guru-api-wytsvpr2eq-uc.a.run.app`
**Revision:** `guru-api-00057-6nc`
**Date:** 2025-12-14

## Testing

1. Navigate to D12 chart in UI
2. Verify:
   - ✅ Mercury is in Capricorn (Makara, House 10)
   - ✅ Saturn is in Capricorn (Makara, House 10)
   - ✅ Ascendant is Vrishchika (Scorpio, House 8)
   - ✅ All other planets are in correct signs

## Summary

The D12 calculation now uses the **base formula without any correction**, which matches the correct JHORA/Drik Panchang calculation. All planets are now in their correct signs, matching the screenshot reference.

---

**Fix Applied:** 2025-12-14
**Deployment:** Complete ✅

