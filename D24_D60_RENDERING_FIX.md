# D24-D60 Rendering Fix - Critical UI Fix

## 🚨 Problem

**Error**: `"South Indian chart must have exactly 12 houses, got 0"`

**Root Cause**: D24-D60 are pure sign charts with `Houses: null` (astrologically correct), but the UI was trying to render them using `SouthIndianChart`, which requires 12 houses.

## ✅ Solution

### 1. Single Source of Truth: `isHouseChart()`

Created `chartUtils.ts` with a single source of truth for chart type classification:

```typescript
export function isHouseChart(varga: number): boolean {
  return varga <= 20;
}
```

- **D1-D20**: House-based charts (require 12 houses)
- **D24-D60**: Pure sign charts (no houses, sign-only)

### 2. New Component: `SignChart`

Created `SignChart.tsx` for pure sign charts (D24-D60):
- Renders planets by sign only (no houses)
- Uses fixed sign positions (same layout as South Indian chart)
- No house assertions or calculations
- Sign-only rendering

### 3. Chart Type Switch in `ChartContainer`

Updated `ChartContainer.tsx` to use the correct renderer:

```typescript
if (isPureSignChartType) {
  // D24-D60: Use SignChart (sign-only, no houses)
  <SignChart planets={apiChart.Planets} ascendantSign={ascendantSign} chartType={chartTypeFromData} />
} else if (isHouseBasedChart) {
  // D1-D20: Use house chart components
  chartStyle === 'north' ? <NorthIndianChart ... /> : <SouthIndianChart ... />
}
```

### 4. Safety Guards

Added safety guards to prevent incorrect usage:

**SouthIndianChart.tsx**:
```typescript
if (!houses || houses.length !== 12) {
  throw new Error(
    `FATAL: SouthIndianChart used incorrectly. ` +
    `Expected 12 houses, got ${houses?.length || 0}. ` +
    `Pure sign charts (D24-D60) must use SignChart component instead.`
  );
}
```

**NorthIndianChart.tsx**: Same safety guard added.

### 5. Removed House Assertions for Sign Charts

- Pure sign charts (D24-D60) no longer require houses
- No house count assertions for D24-D60
- No ascendant house assertions for D24-D60
- Sign-only validation

## 📊 Chart Classification

### ✅ House-Based Charts (D1-D20)
- **Components**: `SouthIndianChart`, `NorthIndianChart`
- **Requirements**: 
  - `houses.length === 12`
  - `ascendant.house === 1`
  - Full house-based rendering

### ✅ Pure Sign Charts (D24-D60)
- **Component**: `SignChart`
- **Requirements**:
  - `Houses: null` (valid)
  - Planets by sign only
  - No house structure

## 🎯 Expected Result

- ✅ Clicking D24-D60 shows sign-only charts
- ✅ No runtime errors ("must have exactly 12 houses")
- ✅ D1-D20 unaffected (still use house charts)
- ✅ Visual match with ProKerala for sign charts
- ✅ Clear distinction between house charts and sign charts

## 📝 Files Changed

1. **`apps/guru-web/guru-web/components/Chart/chartUtils.ts`** (NEW)
   - `isHouseChart(varga)`: Single source of truth
   - `getVargaNumber(chartType)`: Extract varga from chart type
   - `isPureSignChart(chartType)`: Check if pure sign chart

2. **`apps/guru-web/guru-web/components/Chart/SignChart.tsx`** (NEW)
   - Sign-only chart renderer for D24-D60
   - Fixed sign positions (no houses)
   - Planets grouped by sign

3. **`apps/guru-web/guru-web/components/Chart/ChartContainer.tsx`**
   - Chart type detection using `isHouseChart()`
   - Conditional rendering: `SignChart` vs house charts
   - Removed house assertions for pure sign charts

4. **`apps/guru-web/guru-web/components/Chart/SouthIndianChart.tsx`**
   - Safety guard: Must have 12 houses
   - Clear error message if used incorrectly

5. **`apps/guru-web/guru-web/components/Chart/NorthIndianChart.tsx`**
   - Safety guard: Must have 12 houses
   - Clear error message if used incorrectly

## 🔒 Principles Enforced

1. **No Fake Houses**: Never add dummy houses for D24-D60
2. **No Dummy Arrays**: Never set empty house arrays
3. **No Sign Rotation**: Fixed sign positions for sign charts
4. **No Lagna-Based Math**: Sign charts don't use house calculations
5. **Single Source of Truth**: `isHouseChart()` determines chart type

## 🧪 Testing

### Test D1-D20 (House Charts)
1. Select D1, D9, D10, D12, D16, D20
2. Verify: House charts render correctly
3. Verify: No errors about missing houses

### Test D24-D60 (Pure Sign Charts)
1. Select D24, D27, D30, D40, D45, D60
2. Verify: Sign-only charts render (no houses)
3. Verify: No "must have exactly 12 houses" error
4. Verify: Planets shown by sign only
5. Verify: No style toggle (sign charts don't have North/South variants)

### Test Safety Guards
1. Try to pass D24 data to `SouthIndianChart` (should throw clear error)
2. Verify: Error message explains the issue clearly

## ✅ Acceptance Criteria Met

- [x] D24-D60 render as sign-only charts
- [x] No "must have exactly 12 houses" errors
- [x] D1-D20 unaffected (still use house charts)
- [x] Safety guards prevent incorrect usage
- [x] Single source of truth for chart type classification
- [x] No fake houses or dummy arrays
- [x] Clear error messages for incorrect usage

