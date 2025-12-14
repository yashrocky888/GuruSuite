# Frontend Fix: Ascendant Sign Display Issue

## Problem
Ascendant sign is showing incorrectly:
- **D1**: Shows "Mithuna" instead of "Vrishchika"
- **D9**: Shows "Mesha" instead of "Karka"

## Root Cause
The UI is displaying the **house cusp sign** instead of the **Ascendant planet's sign**. In Placidus house system:
- House 8 cusp = Mithuna (from API Houses array)
- Ascendant planet sign = Vrishchika (from API Ascendant.sign_sanskrit)

These are **different** and the UI must use the **Ascendant planet's sign**, not the house cusp sign.

## API Response Structure

### D1 Chart:
```json
{
  "D1": {
    "Ascendant": {
      "sign_sanskrit": "Vrishchika",  // ← USE THIS
      "sign": "Scorpio",
      "house": 8,
      "degree": 212.2799,
      "degrees_in_sign": 2.2799
    },
    "Houses": [
      { "house": 8, "sign_sanskrit": "Mithuna", "sign": "Gemini" },  // ← House cusp sign (different!)
      ...
    ]
  }
}
```

### D9 Chart:
```json
{
  "D9": {
    "ascendant_sign_sanskrit": "Karka",  // ← USE THIS
    "ascendant_sign": "Cancer",
    "ascendant": 110.5191,
    "planets": { ... }
  }
}
```

## Fix Instructions

### Step 1: Fix Ascendant Planet Sign in Chart Display

**File:** `components/Chart/SouthIndianChart.tsx` (or wherever planets are rendered)

**Problem:** The chart is likely displaying the house's sign instead of the planet's sign.

**Solution:** When rendering the Ascendant planet, use the planet's `sign` property, NOT the house's `signName`.

```typescript
// ❌ WRONG - Using house sign
const ascendantSign = house.signName; // This is "Mithuna" (house cusp sign)

// ✅ CORRECT - Using planet sign
const ascendantPlanet = house.planets.find(p => p.name === 'Ascendant');
const ascendantSign = ascendantPlanet?.sign; // This is "Vrishchika" (planet sign)
```

### Step 2: Fix Display Label

**File:** `components/Chart/ChartContainer.tsx`

**Current code (line 440-455):**
```typescript
let ascendantSignName = (chartData as any).ascendant_sign_sanskrit
  || ascendantHouse?.planets.find(p => p.name === 'Ascendant')?.sign
  || ...
```

**This should work, but verify the data flow:**

1. Check if `chartData.D1?.Ascendant?.sign_sanskrit` exists
2. Check if `ascendantHouse?.planets.find(p => p.name === 'Ascendant')?.sign` is correct
3. Add console.log to debug:

```typescript
const ascendantHouse = houses.find(h => h.planets.some(p => p.name === 'Ascendant'));
const ascendantPlanet = ascendantHouse?.planets.find(p => p.name === 'Ascendant');

console.log('🔍 DEBUG Ascendant Sign:', {
  'chartData.D1.Ascendant.sign_sanskrit': (chartData as any).D1?.Ascendant?.sign_sanskrit,
  'ascendantPlanet.sign': ascendantPlanet?.sign,
  'ascendantHouse.signName': ascendantHouse?.signName,
  'final ascendantSignName': ascendantSignName
});
```

### Step 3: Verify Normalization

**File:** `components/Chart/utils.ts`

**Check line 382-390:** The Ascendant planet should have `sign: ascendantSign` where `ascendantSign = apiData.lagnaSignSanskrit`.

Add debug log:
```typescript
houses[houseIndex].planets.push({
  name: 'Ascendant',
  abbr: 'Asc',
  sign: ascendantSign, // Should be "Vrishchika"
  // ...
});
console.log('🔍 DEBUG: Ascendant planet added:', {
  house: validHouse,
  planetSign: ascendantSign,  // Should be "Vrishchika"
  houseCuspSign: houses[houseIndex].signName,  // Will be "Mithuna" (different!)
});
```

## Expected Behavior

### D1 Chart:
- **Ascendant planet sign**: Vrishchika ✅
- **House 8 cusp sign**: Mithuna (different, this is OK)
- **Display should show**: "Vrishchika" (planet sign, not house sign)

### D9 Chart:
- **Ascendant sign**: Karka ✅
- **Display should show**: "Karka"

## Testing

1. Open D1 chart
2. Check console for: `📍 Ascendant: House=8 (from API), Sign=Vrishchika`
3. Verify display shows: "Lagna: Vrishchika" (not "Mithuna")
4. Open D9 chart
5. Verify display shows: "Lagna: Karka" (not "Mesha")

## Key Point

**In Placidus house system, house cusp signs and planet signs can be different. Always use the planet's sign for display, not the house cusp sign.**

