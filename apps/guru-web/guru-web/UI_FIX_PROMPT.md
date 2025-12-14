# UI Fix Prompt - API Keys & Current Dasha

## Context
The frontend needs to be updated to:
1. Use correct API keys for displaying planets in charts
2. Fix "Current Dasha N/A" showing null in dashboard

## API Response Structure

### Endpoint
```
GET https://guru-api-660206747784.us-central1.run.app/api/v1/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946
```

### Response Structure
```json
{
  "julian_day": 2449845.5,
  "D1": {
    "Ascendant": {
      "degree": 212.2799,
      "sign": "Vrishchika",
      "sign_sanskrit": "Vrishchika",
      "sign_index": 7,
      "degrees_in_sign": 2.2799,
      "house": 8,
      "lord": "Mars",
      "nakshatra": "Vishakha",
      "nakshatra_index": 16,
      "pada": 2,
      "degree_dms": 212,
      "arcminutes": 16,
      "arcseconds": 47
    },
    "Planets": {
      "Sun": {
        "degree": 31.4138,
        "sign": "Vrishabha",
        "sign_sanskrit": "Vrishabha",
        "sign_index": 1,
        "degrees_in_sign": 1.4138,
        "house": 2,
        "house_lord": "Jupiter",
        "nakshatra": "Krittika",
        "nakshatra_index": 3,
        "pada": 1,
        "retro": false,
        "speed": 0.9856,
        "degree_dms": 31,
        "arcminutes": 24,
        "arcseconds": 49
      },
      "Moon": { /* same structure */ },
      "Mars": { /* same structure */ },
      "Mercury": { /* same structure */ },
      "Jupiter": { /* same structure */ },
      "Venus": { /* same structure */ },
      "Saturn": { /* same structure */ },
      "Rahu": { /* same structure */ },
      "Ketu": { /* same structure */ }
    },
    "Houses": [
      {
        "house": 1,
        "sign": "Vrishchika",
        "sign_sanskrit": "Vrishchika",
        "degree": 212.2799,
        "degrees_in_sign": 2.2799
      },
      // ... 11 more houses
    ]
  },
  "D2": { /* divisional charts */ },
  "D3": { /* divisional charts */ },
  // ... other divisional charts
}
```

## Critical Fixes Required

### 1. Chart Display - Use Correct API Keys

**Current Issue:** Planets are being displayed but may be using wrong keys or not matching house signs correctly.

**Fix Required:**
- ✅ **ALREADY FIXED:** Planets are matched to houses by sign (not by API's `house` field)
- ✅ **ALREADY FIXED:** Uses `degrees_in_sign` for display (0-30°)
- ✅ **ALREADY FIXED:** Uses `degree_dms`, `arcminutes`, `arcseconds` for DMS format

**Verify these keys are used:**
- Planet sign: `planet.sign_sanskrit` or `planet.sign` (Sanskrit name)
- Planet degree: `planet.degrees_in_sign` (0-30° for display)
- Planet DMS: `planet.degree_dms`, `planet.arcminutes`, `planet.arcseconds`
- House sign: From `D1.Houses[houseNumber-1].sign_sanskrit` or `D1.Houses[houseNumber-1].sign`
- Ascendant: `D1.Ascendant.sign_sanskrit`, `D1.Ascendant.degrees_in_sign`, `D1.Ascendant.house`

**Files to check:**
- `guru-web/components/Chart/ChartContainer.tsx` - Planet extraction
- `guru-web/components/Chart/utils.ts` - House normalization (already fixed)
- `guru-web/components/Chart/SouthIndianChart.tsx` - Display formatting
- `guru-web/components/Chart/NorthIndianChart.tsx` - Display formatting

### 2. Dashboard - Current Dasha N/A Fix

**Current Issue:** Dashboard shows "Current Dasha: N/A" because:
1. `/api/v1/dashboard` endpoint returns 404 (doesn't exist)
2. Dasha data is not in the kundli response
3. Need to calculate or fetch dasha separately

**Fix Required:**

**Option A: Calculate Dasha from Moon Nakshatra**
- Extract Moon's nakshatra from `D1.Planets.Moon.nakshatra` or `D1.Planets.Moon.nakshatra_index`
- Calculate current dasha based on birth date and Moon's nakshatra
- Use Vimshottari Dasha system (120 years cycle)

**Option B: Fetch from Dasha Endpoint**
- Check if `/api/v1/dasha` endpoint exists
- If exists, fetch dasha data: `GET /api/v1/dasha?user_id={userId}`
- Extract `currentDasha` from response

**Option C: Calculate Client-Side (Recommended)**
- Use Moon's nakshatra index: `D1.Planets.Moon.nakshatra_index`
- Calculate dasha based on birth date
- Display format: "Moon Dasha" or "Mars Dasha" etc.

**Implementation in `guru-web/app/dashboard/page.tsx`:**

```typescript
// In fetchDashboard function, after extracting kundli data:
if (d1) {
  const moon = planets.Moon;
  const moonNakshatraIndex = moon?.nakshatra_index;
  
  // Calculate current dasha from Moon's nakshatra
  let currentDasha = 'N/A';
  if (moonNakshatraIndex !== undefined && birthDetails?.date) {
    currentDasha = calculateCurrentDasha(moonNakshatraIndex, birthDetails.date);
  }
  
  data = {
    currentDasha: currentDasha,
    ascendant: ascendant?.sign_sanskrit || ascendant?.sign || 'N/A',
    moonSign: moon?.sign_sanskrit || moon?.sign || 'N/A',
    system: 'Vedic',
    ayanamsa: 'Lahiri'
  };
}
```

**Dasha Calculation Function (create in `guru-web/utils/dasha.ts`):**

```typescript
/**
 * Calculate current Vimshottari Dasha from Moon's nakshatra
 * Vimshottari Dasha: 120 years cycle
 * Each nakshatra has a starting dasha lord
 */
export function calculateCurrentDasha(moonNakshatraIndex: number, birthDate: string): string {
  // Nakshatra to Dasha Lord mapping (starting from Ashwini)
  const nakshatraDashaLords = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', // 0-8
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', // 9-17
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'  // 18-26
  ];
  
  // Dasha periods in years
  const dashaPeriods: Record<string, number> = {
    'Ketu': 7,
    'Venus': 20,
    'Sun': 6,
    'Moon': 10,
    'Mars': 7,
    'Rahu': 18,
    'Jupiter': 16,
    'Saturn': 19,
    'Mercury': 17
  };
  
  // Get starting dasha lord for Moon's nakshatra
  const startingLord = nakshatraDashaLords[moonNakshatraIndex % 27];
  
  // Calculate years since birth
  const birth = new Date(birthDate);
  const now = new Date();
  const yearsSinceBirth = (now.getTime() - birth.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
  
  // Calculate which dasha period we're in (simplified - assumes starting from birth)
  // For accurate calculation, need to know exact dasha start time
  // This is a simplified version - for production, use proper dasha calculation library
  
  return `${startingLord} Dasha`; // Simplified - return starting lord
}
```

**Or use existing dasha endpoint if available:**
```typescript
// Try to fetch from dasha endpoint
try {
  const dashaData = await getDasha(userId);
  currentDasha = dashaData.currentDasha || 'N/A';
} catch (error) {
  // Fallback to calculation
  currentDasha = calculateCurrentDasha(moonNakshatraIndex, birthDetails.date);
}
```

## Files to Update

1. **`guru-web/app/dashboard/page.tsx`**
   - Fix `currentDasha` extraction/calculation
   - Ensure it uses `D1.Planets.Moon.nakshatra_index` for dasha calculation

2. **`guru-web/utils/dasha.ts`** (create if doesn't exist)
   - Add `calculateCurrentDasha` function
   - Or use existing dasha calculation if available

3. **Verify Chart Components:**
   - `guru-web/components/Chart/ChartContainer.tsx` - Already fixed
   - `guru-web/components/Chart/utils.ts` - Already fixed (uses sign matching)
   - `guru-web/components/Chart/SouthIndianChart.tsx` - Verify DMS display
   - `guru-web/components/Chart/NorthIndianChart.tsx` - Verify DMS display

## Testing

After fixes:
1. ✅ All 9 planets should appear in correct houses (matched by sign)
2. ✅ Ascendant should show correct degree (2° 16' 47", not 212°)
3. ✅ Dashboard should show Current Dasha (e.g., "Moon Dasha" or "Mars Dasha")
4. ✅ Ascendant and Moon Sign should display correctly

## API Keys Summary

**For Planets:**
- `sign_sanskrit` or `sign` - Sanskrit sign name
- `degrees_in_sign` - Degree in sign (0-30°) for display
- `degree_dms` - Degree part (integer)
- `arcminutes` - Minutes part (integer)
- `arcseconds` - Seconds part (integer)
- `house` - House number (but don't use for placement - use sign matching instead)
- `nakshatra` - Nakshatra name
- `nakshatra_index` - Nakshatra index (0-26) for dasha calculation
- `retro` - Retrograde status (boolean)

**For Ascendant:**
- `sign_sanskrit` or `sign` - Sanskrit sign name
- `degrees_in_sign` - Degree in sign (0-30°) for display
- `degree_dms`, `arcminutes`, `arcseconds` - DMS components
- `house` - House number (use for placement)

**For Houses:**
- `house` - House number (1-12)
- `sign_sanskrit` or `sign` - Sign in that house
- `degrees_in_sign` - Degree of house cusp in sign

