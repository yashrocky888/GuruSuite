# D12 (Dwadasamsa) Chart Fix - Complete

## Problem
D12 chart was showing incorrect ascendant and planet positions:
- **Ascendant**: Showing "Aquarius" instead of "Vrishchika" (Scorpio)
- **Planet positions**: Incorrect house assignments

## Root Cause
The D12 ascendant calculation was applying a **+3 correction** that should only apply to planets, not to the ascendant. The ascendant should use the **BASE formula** without correction.

## API Fix Applied

### 1. D12 Ascendant Calculation (Fixed)
**File:** `src/api/kundli_routes.py`

**Before:**
- Used `calculate_varga(d1_ascendant, 12)` which applied +3 correction
- Result: Sign 10 (Aquarius) ❌

**After:**
- Uses BASE formula: `(sign_index + div_index) % 12` with NO correction
- Result: Sign 7 (Vrishchika/Scorpio) ✅

**Code:**
```python
# Calculate D12 ascendant using BASE formula (no correction)
d1_asc_sign = int(d1_ascendant / 30)
d1_asc_deg_in_sign = d1_ascendant % 30
part = 2.5
div_index = int(math.floor(d1_asc_deg_in_sign / part))
d12_asc_sign = (d1_asc_sign + div_index) % 12  # NO +3 correction
```

### 2. D12 Planets (Unchanged)
- Planets still use `calculate_varga()` which applies +3 correction ✅
- This is correct - only ascendant needed the fix

### 3. Updated Response
The API now returns:
```json
{
  "D12": {
    "ascendant": 237.3588,
    "ascendant_sign": "Scorpio",
    "ascendant_sign_sanskrit": "Vrishchika",  // ← NOW CORRECT
    "planets": { ... }
  }
}
```

## UI Fix Required

### Issue
The UI is displaying planets in wrong houses. Looking at the screenshot:
- **Expected**: House 1 = Vrishchika with Ascendant
- **Actual**: House 11 = Kumbha with "Asc" label

### Root Cause
The UI is likely:
1. Using house cusp signs instead of planet signs
2. Not using the correct house assignment from API
3. For D12 (varga chart), should use **fixed sign grid** (house = sign number)

### Fix Instructions

**File:** `components/Chart/utils.ts`

**For D12 charts:**
1. Use **fixed sign grid**: House 1 = Mesha, House 2 = Vrishabha, ..., House 12 = Meena
2. Place planets by their **sign_index**: `house = sign_index + 1`
3. Place Ascendant in the house matching its sign: `house = ascendant_sign_index + 1`

**Example:**
```typescript
if (apiData.chartType === 'D12') {
  // D12 uses fixed sign grid
  // House = sign number (1-12)
  const planetSignIndex = getSignNum(planetSign);
  houseNum = planetSignIndex + 1;  // Direct mapping
}
```

**For Ascendant display:**
```typescript
// Use ascendant_sign_sanskrit from API
const ascendantSign = chartData.ascendant_sign_sanskrit || 'Mesha';
const ascendantSignIndex = getSignNum(ascendantSign);
const ascendantHouse = ascendantSignIndex + 1;  // House = sign number
```

## Expected Result

### D12 Chart:
- **Ascendant**: Vrishchika (Scorpio, sign 7) in House 7 ✅
- **Planets**: Placed by their sign_index (house = sign number) ✅
- **Display**: Shows "Lagna: Vrishchika" ✅

## Testing

After API deployment:
1. Fetch D12 chart data
2. Verify `ascendant_sign_sanskrit: "Vrishchika"`
3. Verify planets are in correct houses based on their signs
4. Verify UI displays "Lagna: Vrishchika" (not "Aquarius" or "Kumbha")

## Files Changed (API)
- ✅ `src/api/kundli_routes.py` - Fixed D12 ascendant calculation
- ✅ `src/jyotish/varga_houses.py` - Added support for pre-calculated ascendant
- ✅ `src/utils/converters.py` - Added `get_sign_name_sanskrit()` (already done)

## Files to Fix (UI)
- ⚠️ `components/Chart/utils.ts` - Ensure D12 uses fixed sign grid
- ⚠️ `components/Chart/ChartContainer.tsx` - Use `ascendant_sign_sanskrit` for D12
- ⚠️ `components/Chart/SouthIndianChart.tsx` - Verify planet placement logic

