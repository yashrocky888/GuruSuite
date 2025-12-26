# ASTRO UI CONTRACT - ARCHITECTURAL LOCK

## 🎯 PRINCIPLE: UI PERFORMS ZERO ASTROLOGY

The UI is a **pure renderer** that displays exactly what the API sends. No calculations, no inferences, no fallbacks.

## ✅ API CONTRACT (CANONICAL STRUCTURE)

### Standard Chart Response

```json
{
  "Ascendant": {
    "sign": "Cancer",
    "sign_sanskrit": "Karka",
    "sign_index": 3,
    "house": 1,
    "degree": 123.45,
    "degrees_in_sign": 3.45
  },
  "Houses": [
    { "house": 1, "sign": "Cancer", "sign_sanskrit": "Karka", "sign_index": 3 },
    { "house": 2, "sign": "Leo", "sign_sanskrit": "Simha", "sign_index": 4 },
    ...
    { "house": 12, "sign": "Gemini", "sign_sanskrit": "Mithuna", "sign_index": 2 }
  ],
  "Planets": {
    "Sun": { "sign": "Taurus", "sign_sanskrit": "Vrishabha", "sign_index": 1, "house": 11, "degree": 45.67 },
    "Moon": { "sign": "Scorpio", "sign_sanskrit": "Vrishchika", "sign_index": 7, "house": 5, "degree": 234.56 },
    ...
  }
}
```

### Full Kundli Response (Multiple Charts)

```json
{
  "D1": { "Ascendant": {...}, "Houses": [...], "Planets": {...} },
  "D2": { "Ascendant": {...}, "Houses": [...], "Planets": {...} },
  "D9": { "Ascendant": {...}, "Houses": [...], "Planets": {...} },
  "D10": { "Ascendant": {...}, "Houses": [...], "Planets": {...} },
  "D12": { "Ascendant": {...}, "Houses": [...], "Planets": {...} },
  "current_dasha": { "display": "Moon Dasha - Mars Antardasha" }
}
```

## 🔒 HARD RUNTIME ASSERTIONS

### 1. Ascendant House Assertion

**Location**: `components/Chart/ChartContainer.tsx`

```typescript
// RUNTIME ASSERTION: Ascendant.house must be 1 (API contract)
if (chart.Ascendant?.house !== undefined && chart.Ascendant.house !== 1) {
  throw new Error(`FATAL: Ascendant.house must be 1, got ${chart.Ascendant.house}`);
}
```

**Enforced in**:
- `ChartContainer.tsx` - Validates API response
- `NorthIndianChart.tsx` - Validates before rendering
- `SouthIndianChart.tsx` - Validates before rendering
- `app/dashboard/page.tsx` - Validates before display

### 2. Houses Array Assertion

**Location**: `components/Chart/ChartContainer.tsx`

```typescript
// RUNTIME ASSERTION: Must have exactly 12 houses
if (!chart.Houses || !Array.isArray(chart.Houses) || chart.Houses.length !== 12) {
  throw new Error(`FATAL: Invalid house data. Expected 12 houses, got ${chart.Houses?.length || 0}`);
}
```

### 3. Planets House Assertion

**Location**: `components/Chart/ChartContainer.tsx`

```typescript
// RUNTIME ASSERTION: All planets must have house
Object.entries(chart.Planets).forEach(([name, planet]: [string, any]) => {
  if (planet.house === undefined || planet.house < 1 || planet.house > 12) {
    throw new Error(`FATAL: Planet ${name} has invalid house: ${planet.house}`);
  }
});
```

## 🚫 FORBIDDEN UI OPERATIONS

1. ❌ Calculate house signs from lagna
2. ❌ Rotate or remap houses
3. ❌ Infer planet houses from signs
4. ❌ Create fallback houses if API data missing
5. ❌ Use modulo(12) for house calculations
6. ❌ Calculate degrees or positions
7. ❌ Normalize or transform API data (except minimal rendering format)

## ✅ ALLOWED UI OPERATIONS

1. ✅ Read API response fields directly
2. ✅ Map API format to minimal rendering format (house number, sign name, planet list)
3. ✅ Render SVG/HTML based on API data
4. ✅ Format degrees for display (DMS conversion for display only)
5. ✅ Style charts (colors, positions, layout)

## 📊 DIRECT RENDERING PATTERN

### North Indian Chart

```typescript
// For each house position (static):
for (const [houseNum, polygonPoints] of Object.entries(northPolygonPoints)) {
  const house = apiChart.Houses.find(h => h.house === parseInt(houseNum));
  const planets = Object.entries(apiChart.Planets)
    .filter(([_, p]) => p.house === parseInt(houseNum));
  
  drawHouse(houseNum, house.sign, planets);
}
```

### South Indian Chart

```typescript
// For each sign position (static):
for (const [signKey, rect] of Object.entries(southRectPositions)) {
  const house = apiChart.Houses.find(h => 
    (h.sign_sanskrit || h.sign).toLowerCase() === signKey
  );
  const planets = Object.entries(apiChart.Planets)
    .filter(([_, p]) => p.house === house.house);
  
  drawSignBox(signKey, house.house, house.sign, planets);
}
```

## 🧪 GOLDEN TEST CASE

**DOB**: 1995-05-16  
**Time**: 18:38  
**Place**: Bangalore

**Expected D10 (Prokerala)**:
- Ascendant: Cancer/Karka (House 1, Sign Index 3)
- Venus: Aquarius/Kumbha (House 11, Sign Index 10)
- Mars: Pisces/Meena (House 12, Sign Index 11)

**Verification**:
1. API returns correct data ✅
2. UI displays exactly what API sends ✅
3. No "N/A" or "Data Error" ✅
4. North & South charts match ✅

## 📝 FILES WITH DIRECT RENDERING

1. `components/Chart/ChartContainer.tsx` - Extracts chart from API, minimal transformation
2. `components/Chart/NorthIndianChart.tsx` - Renders directly from houses array
3. `components/Chart/SouthIndianChart.tsx` - Renders directly from houses array
4. `app/dashboard/page.tsx` - Extracts from D1 directly

## 🎯 ENFORCEMENT

All assertions **throw errors** (fail fast) if violated. This ensures:
- API contract is never broken
- UI never displays incorrect data
- Bugs are caught immediately
- System remains locked to Prokerala/JHora truth

**Status**: ✅ All assertions implemented. System locked.
