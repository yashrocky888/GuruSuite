# Frontend Fix: Varga Chart House Matching Error

## Problem
Console errors: `❌ No house found with sign X for planet Y` when viewing varga charts (D2, D3, D7, D9, D10, D12).

## Root Cause
The frontend was trying to match planet signs to house signs, but for varga charts:
1. API returns English sign names ("Libra", "Capricorn", etc.) for varga charts
2. Houses array might not contain all 12 signs properly initialized
3. South Indian charts use a **fixed sign grid** where house = sign number (1-12)

## Solution
Fixed `components/Chart/utils.ts` to handle varga charts correctly:

### For Varga Charts (D2, D3, D7, D9, D10, D12):
- **Use fixed sign grid**: House 1 = Mesha, House 2 = Vrishabha, ..., House 12 = Meena
- **Place planets by sign number**: `house = sign_index` (1-12)
- **No sign matching needed**: Direct placement based on planet's sign

### For D1 Charts:
- Keep existing logic (match planet sign to house sign using JHORA/Placidus system)

## Files Changed
1. ✅ `guru-web/components/Chart/utils.ts`
   - Added `isVargaChart` detection
   - Fixed house initialization for varga charts (fixed sign grid)
   - Fixed planet placement logic (use sign number for varga charts)

2. ✅ `guru-web/components/Chart/ChartContainer.tsx`
   - Improved `chartType` detection for divisional charts

## Expected Result
- ✅ No more console errors for varga charts
- ✅ Planets correctly placed in varga charts
- ✅ South Indian chart style works correctly (fixed sign grid)

