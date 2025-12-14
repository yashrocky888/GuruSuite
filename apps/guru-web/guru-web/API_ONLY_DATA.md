# API-Only Data Policy ✅

## Rule: ALL Data Must Come From API

**No calculations on the frontend** - Only chart styling and rendering.

## What Changed

### ✅ Removed All Calculations

1. **House Signs**: No longer calculated from lagna
   - **Before**: Used `getSignForHouse()` as fallback when house had no planets
   - **After**: Only uses sign from API planet data
   - **If API doesn't provide**: House shows "Unknown" (no calculation)

2. **Planet Data**: No defaults or fallbacks
   - **Before**: Used defaults like `house: 1`, `sign: 'Mesha'`, `degree: 0`
   - **After**: Only uses exact values from API
   - **If API missing data**: Planet is filtered out (not displayed)

3. **Lagna/Ascendant**: No defaults
   - **Before**: Defaulted to `lagna: 1`, `lagnaSign: 'Mesha'`
   - **After**: Uses API values only, `undefined` if not provided

### ✅ API Data Flow

```
API Response → ChartContainer → normalizeKundliData() → Chart Components
     ↓              ↓                    ↓                    ↓
  Exact data    No defaults      API-only mapping      Pure rendering
```

### ✅ Validation

- **Planets**: Must have `name`, `sign`, `house`, `degree` from API
- **Missing data**: Filtered out (not displayed with wrong defaults)
- **House signs**: Only from planet data in that house
- **Empty houses**: Show "Unknown" sign (not calculated)

### ✅ What Frontend Does Now

**ONLY:**
- ✅ Chart styling (colors, positions, layout)
- ✅ Data mapping (API format → chart format)
- ✅ Rendering (SVG, React components)

**NEVER:**
- ❌ Calculate house signs
- ❌ Calculate planet positions
- ❌ Calculate degrees
- ❌ Use defaults/fallbacks for missing data

## Example

**API Response:**
```json
{
  "planets": [
    {"name": "Sun", "sign": "Vrishabha", "house": 6, "degree": 31.42}
  ]
}
```

**Frontend:**
- ✅ Uses `house: 6` directly → Places Sun in House 6
- ✅ Uses `sign: "Vrishabha"` directly → Shows "Vrishabha" in House 6
- ✅ Uses `degree: 31.42` directly → Displays "31.42°"
- ❌ Does NOT calculate house sign from lagna
- ❌ Does NOT use defaults if data missing

## Status: ✅ COMPLETE

All calculations removed. Frontend is now **pure rendering** of API data.

