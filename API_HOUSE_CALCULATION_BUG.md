# 🐛 API HOUSE CALCULATION BUG - IDENTIFIED

## Problem Summary

From console logs, the API is returning **WRONG house numbers** for planets:

**WRONG (from API):**
- Venus: `house: 1` → Should be `6`
- Ketu: `house: 1` → Should be `6`
- Sun: `house: 2` → Should be `7`
- Mercury: `house: 2` → Should be `7`
- Mars: `house: 5` → Should be `10`
- Rahu: `house: 7` → Should be `12`
- Saturn: `house: 11` → Should be `4`

**CORRECT (from user's data):**
- Moon: `house: 8` ✅ (API returns this correctly)
- Jupiter: `house: 8` ✅ (API returns this correctly)

**Also WRONG:**
- House 8 sign: `Mithuna` → Should be `Vrischika`

## Root Cause

The API's `get_planet_house_jhora()` function is using the correct formula:
```python
house = ((planet_sign_index - ascendant_sign_index + 12) % 12) + 1
```

But the **planet degrees** being passed to this function might be wrong, OR the **ascendant degree** is wrong.

## Next Steps

1. Add logging to `get_planet_house_jhora()` to see what degrees it receives
2. Verify planet degrees from `calculate_all_planets_jhora_exact()`
3. Verify ascendant degree from `calculate_ascendant_jhora_exact()`
4. Fix the house calculation if degrees are wrong

## UI Status

✅ **UI is 100% correct** - it's displaying exactly what the API returns.
The problem is entirely in the API's house calculation logic.
