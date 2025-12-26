# UI ASSERTIONS - ARCHITECTURAL CONTRACT

## 🎯 PRINCIPLE: UI PERFORMS ZERO ASTROLOGY

The UI is a **pure renderer** that displays exactly what the API sends. No calculations, no inferences, no fallbacks.

## ✅ RUNTIME ASSERTIONS

### 1. API Contract Enforcement

**Location**: `components/Chart/ChartContainer.tsx`

```typescript
// RUNTIME ASSERTION: Ascendant.house must be 1 (API contract)
if (kundli.Ascendant.house !== undefined && kundli.Ascendant.house !== 1) {
  throw new Error(`API VIOLATION: Ascendant.house must be 1, got ${kundli.Ascendant.house}`);
}
```

**Enforced in**:
- `ChartContainer.tsx` - Validates API response
- `utils.ts` - Validates before normalization
- `NorthIndianChart.tsx` - Validates before rendering
- `SouthIndianChart.tsx` - Validates before rendering

### 2. Houses Array Validation

**Location**: `components/Chart/utils.ts`

```typescript
// RUNTIME ASSERTION: API must provide exactly 12 houses
if (!apiData.houses || !Array.isArray(apiData.houses) || apiData.houses.length !== 12) {
  throw new Error(`API must provide exactly 12 houses. Got: ${apiData.houses?.length || 0}`);
}
```

### 3. Planets Validation

**Location**: `components/Chart/utils.ts`

```typescript
// RUNTIME ASSERTION: All planets must have required fields
apiData.planets.forEach((planet) => {
  if (!planet.name) throw new Error(`Planet missing name: ${JSON.stringify(planet)}`);
  if (!planet.sign) throw new Error(`Planet ${planet.name} missing sign`);
  if (planet.house === undefined || planet.house < 1 || planet.house > 12) {
    throw new Error(`Planet ${planet.name} has invalid house: ${planet.house}`);
  }
});
```

### 4. Ascendant in House 1 Validation

**Location**: `components/Chart/ChartContainer.tsx`

```typescript
// RUNTIME ASSERTION: Ascendant must be in house 1
const ascendantHouse = normalizedHouses.find(h => 
  h.planets.some(p => p.name === 'Ascendant' || p.abbr === 'Asc')
);
if (!ascendantHouse) {
  throw new Error('Ascendant must be present in normalized houses');
}
if (ascendantHouse.houseNumber !== 1) {
  throw new Error(`Ascendant must be in house 1, found in house ${ascendantHouse.houseNumber}`);
}
```

## 🔒 API IS SINGLE SOURCE OF TRUTH

### Data Flow

```
API Response (JSON)
  ↓
ChartContainer (extracts D1/D9/D10)
  ↓
normalizeKundliData() (maps API → UI format)
  ↓
Chart Components (render only)
```

### API Response Structure (CANONICAL)

```json
{
  "D1": {
    "Ascendant": {
      "sign": "Cancer",
      "sign_index": 4,
      "house": 1,
      "degree": 123.45
    },
    "Houses": [
      { "house": 1, "sign": "Cancer", "sign_index": 4 },
      { "house": 2, "sign": "Leo", "sign_index": 5 },
      ...
      { "house": 12, "sign": "Gemini", "sign_index": 3 }
    ],
    "Planets": {
      "Sun": { "sign": "Taurus", "house": 11, "degree": 45.67 },
      "Moon": { "sign": "Scorpio", "house": 5, "degree": 234.56 },
      ...
    }
  },
  "D9": { ... },
  "D10": { ... }
}
```

### UI Usage Rules

1. **Houses**: Use `API.Houses[]` array directly (no calculation)
2. **Planets**: Use `API.Planets[planet].house` directly (no inference)
3. **Ascendant**: Use `API.Ascendant.house` (always = 1)
4. **Signs**: Use `API.Houses[house].sign` or `API.Planets[planet].sign` (no calculation)

## ❌ FORBIDDEN UI OPERATIONS

1. ❌ Calculate house signs from lagna
2. ❌ Rotate or remap houses
3. ❌ Infer planet houses from signs
4. ❌ Create fallback houses if API data missing
5. ❌ Use modulo(12) for house calculations
6. ❌ Calculate degrees or positions

## ✅ ALLOWED UI OPERATIONS

1. ✅ Read API response fields
2. ✅ Map API format to UI display format
3. ✅ Render SVG/HTML based on API data
4. ✅ Format degrees for display (DMS conversion)
5. ✅ Style charts (colors, positions, layout)

## 🧪 TESTING

### Golden Test Case

**DOB**: 1995-05-16  
**Time**: 18:38  
**Place**: Bangalore

**Expected D10 (Prokerala)**:
- Ascendant: Cancer (House 1)
- Venus: Aquarius (House 11)
- Mars: Pisces (House 12)

**Verification**:
1. API returns correct data ✅
2. UI displays exactly what API sends ✅
3. No "N/A" or "Data Error" ✅
4. North & South charts match ✅

## 📝 FILES WITH ASSERTIONS

1. `components/Chart/ChartContainer.tsx` - API response validation
2. `components/Chart/utils.ts` - Data normalization validation
3. `components/Chart/NorthIndianChart.tsx` - Rendering validation
4. `components/Chart/SouthIndianChart.tsx` - Rendering validation
5. `app/dashboard/page.tsx` - Dashboard data validation

## 🎯 ENFORCEMENT

All assertions **throw errors** (fail fast) if violated. This ensures:
- API contract is never broken
- UI never displays incorrect data
- Bugs are caught immediately
- System remains locked to Prokerala/JHora truth

**Status**: ✅ All assertions implemented and enforced.
