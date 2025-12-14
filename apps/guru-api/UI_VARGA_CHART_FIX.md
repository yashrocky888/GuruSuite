# UI Fix for Varga Charts (Divisional Charts)

## CRITICAL REQUIREMENT

For ALL divisional charts (D2, D3, D4, D7, D9, D10, D12), the UI MUST:

1. **Use API data ONLY** - Do NOT calculate or infer houses
2. **Render planets using `planet.house`** from API response
3. **Do NOT rotate charts** - Whole Sign system means house = sign
4. **Do NOT compute bhavas** - API provides house directly

## API Response Structure

The API now returns for each varga chart:

```json
{
  "D10": {
    "ascendant": 112.799,
    "ascendant_sign": "Cancer",
    "ascendant_sign_sanskrit": "Karka",
    "ascendant_house": 4,  // house = sign (Whole Sign system)
    "chartType": "D10",
    "planets": {
      "Sun": {
        "sign": "Scorpio",
        "sign_index": 7,
        "house": 8,  // house = sign (7 + 1)
        "degree": 224.194,
        "degrees_in_sign": 14.194
      },
      "Moon": {
        "sign": "Sagittarius",
        "sign_index": 8,
        "house": 9,  // house = sign (8 + 1)
        "degree": 252.503,
        "degrees_in_sign": 12.503
      }
      // ... all planets have house = sign
    }
  }
}
```

## UI Implementation Rules

### ✅ CORRECT Implementation

```typescript
// For divisional charts, use house directly from API
const planetHouse = planet.house; // Already calculated by API
const ascendantHouse = chartData.ascendant_house; // From API

// Render planet in the house specified by API
renderPlanet(planet, planetHouse);

// Do NOT calculate houses
// Do NOT rotate by ascendant
// Do NOT use house cusps
```

### ❌ FORBIDDEN Actions

```typescript
// ❌ DO NOT calculate houses
const calculatedHouse = calculateHouse(planet.longitude, ascendant);

// ❌ DO NOT rotate charts
const rotatedHouse = (planet.sign - ascendant.sign + 1) % 12;

// ❌ DO NOT use house cusps
const houseFromCusp = findHouseFromCusp(planet.longitude, houseCusps);

// ❌ DO NOT infer house from sign
const inferredHouse = planet.sign_index + 1; // API already provides house
```

## Chart Style Differences

### South Indian Chart (Fixed Sign Grid)
- Signs are fixed in positions (House 1 = Mesha, House 2 = Vrishabha, etc.)
- Planets placed by their `house` value from API
- Ascendant label moves to `ascendant_house` position

### North Indian Chart (Rotating House Grid)
- For D1: Houses rotate based on ascendant
- **For varga charts**: Still use `house` from API, but visual style may differ
- **CRITICAL**: Do NOT rotate varga charts - use API house directly

## Example: D10 Chart Rendering

```typescript
// Get D10 data from API
const d10Data = apiResponse.D10;

// Get ascendant house
const ascendantHouse = d10Data.ascendant_house; // e.g., 4 (Cancer)

// Render each planet
d10Data.planets.forEach(planet => {
  const planetHouse = planet.house; // e.g., Sun = 8, Moon = 9
  renderPlanetInHouse(planet, planetHouse);
});

// Do NOT do this:
// const calculatedHouse = calculateHouseFromSign(planet.sign_index); // ❌
```

## Verification

For DOB: 1995-05-16 18:38 Bangalore

Expected D10 houses (from API):
- Ascendant: House 4 (Cancer)
- Sun: House 8 (Scorpio)
- Moon: House 9 (Sagittarius)
- Mercury: House 12 (Pisces)
- Jupiter: House 8 (Scorpio)
- Saturn: House 8 (Scorpio)
- Rahu: House 8 (Scorpio)
- Ketu: House 4 (Cancer)

**The UI must render these exact house numbers from the API response.**

## Summary

1. ✅ Use `planet.house` from API for all varga charts
2. ✅ Use `ascendant_house` from API for ascendant position
3. ❌ Do NOT calculate houses in UI
4. ❌ Do NOT rotate charts for varga charts
5. ❌ Do NOT use house cusps or bhavas

**All house assignments come from the API - the UI only renders what the API provides.**

