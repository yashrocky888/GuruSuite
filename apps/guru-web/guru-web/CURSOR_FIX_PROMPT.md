# Cursor Fix Prompt - UI Display & Current Dasha

## Task
Fix two issues in the Guru frontend:
1. Ensure chart displays planets using correct API keys
2. Fix "Current Dasha N/A" showing null in dashboard

## API Response Structure

**Endpoint:** `GET https://guru-api-660206747784.us-central1.run.app/api/v1/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946`

**Response Format:**
```json
{
  "D1": {
    "Ascendant": {
      "sign_sanskrit": "Vrishchika",
      "degrees_in_sign": 2.2799,
      "degree_dms": 212,
      "arcminutes": 16,
      "arcseconds": 47,
      "house": 8,
      "nakshatra": "Vishakha",
      "nakshatra_index": 16
    },
    "Planets": {
      "Sun": {
        "sign_sanskrit": "Vrishabha",
        "degrees_in_sign": 1.4138,
        "degree_dms": 31,
        "arcminutes": 24,
        "arcseconds": 49,
        "house": 2,
        "nakshatra": "Krittika",
        "nakshatra_index": 3,
        "retro": false
      },
      "Moon": { /* same structure */ },
      // ... all 9 planets
    },
    "Houses": [
      { "house": 1, "sign_sanskrit": "Vrishchika", "degrees_in_sign": 2.2799 },
      { "house": 2, "sign_sanskrit": "Dhanu", "degrees_in_sign": 1.2108 },
      // ... 12 houses
    ]
  }
}
```

## Fix 1: Chart Display (Verify API Keys)

**Status:** Already fixed in `utils.ts` - planets matched to houses by sign.

**Verify these files use correct keys:**

### `guru-web/components/Chart/ChartContainer.tsx`
- ✅ Should extract: `planet.sign_sanskrit`, `planet.degrees_in_sign`, `planet.degree_dms`, `planet.arcminutes`, `planet.arcseconds`
- ✅ Should extract: `ascendant.sign_sanskrit`, `ascendant.degrees_in_sign`, `ascendant.house`

### `guru-web/components/Chart/utils.ts`
- ✅ Already fixed: Planets matched to houses by matching `planet.sign` to `house.signName`
- ✅ Uses `degrees_in_sign` for display (0-30°)

### `guru-web/components/Chart/SouthIndianChart.tsx` & `NorthIndianChart.tsx`
- ✅ Should display: `planet.degree_dms° planet.degree_minutes' planet.degree_seconds"`
- ✅ Should use `degrees_in_sign` for positioning

## Fix 2: Current Dasha N/A

**Problem:** Dashboard shows "Current Dasha: N/A" because dasha is not in API response.

**Solution:** Calculate dasha from Moon's nakshatra index.

### Step 1: Create Dasha Utility

**File:** `guru-web/utils/dasha.ts` (create if doesn't exist)

```typescript
/**
 * Calculate current Vimshottari Dasha from Moon's nakshatra
 */
export function calculateCurrentDasha(moonNakshatraIndex: number, birthDate: string): string {
  // Nakshatra to starting Dasha Lord (Vimshottari system)
  const nakshatraDashaLords = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
  ];
  
  if (moonNakshatraIndex === undefined || moonNakshatraIndex === null) {
    return 'N/A';
  }
  
  // Get starting dasha lord for Moon's nakshatra
  const startingLord = nakshatraDashaLords[moonNakshatraIndex % 27];
  
  // Calculate years since birth
  const birth = new Date(birthDate);
  const now = new Date();
  const yearsSinceBirth = (now.getTime() - birth.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
  
  // Dasha periods in years (Vimshottari)
  const dashaPeriods: Record<string, number> = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
  };
  
  // Calculate which dasha we're in (simplified - cycles through all 9 dashas)
  let totalYears = 0;
  const dashaLords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'];
  const startIndex = dashaLords.indexOf(startingLord);
  
  // Find current dasha by cycling through periods
  let currentDashaIndex = startIndex;
  let remainingYears = yearsSinceBirth;
  
  while (remainingYears > 0) {
    const currentLord = dashaLords[currentDashaIndex % 9];
    const period = dashaPeriods[currentLord];
    
    if (remainingYears <= period) {
      return `${currentLord} Dasha`;
    }
    
    remainingYears -= period;
    currentDashaIndex++;
  }
  
  return `${startingLord} Dasha`;
}
```

### Step 2: Update Dashboard

**File:** `guru-web/app/dashboard/page.tsx`

**Find this section (around line 34-52):**
```typescript
// If dashboard API doesn't have data, extract from kundli
if (!data || !data.ascendant || !data.moonSign) {
  try {
    const kundliResponse = await getKundli(userId, birthDetails);
    
    // Extract D1 chart data
    const d1 = (kundliResponse as any).D1 || (kundliResponse as any).data?.kundli?.D1;
    
    if (d1) {
      const ascendant = d1.Ascendant;
      const planets = d1.Planets || {};
      const moon = planets.Moon;
      
      data = {
        currentDasha: data?.currentDasha || 'N/A',  // ← FIX THIS
        ascendant: ascendant?.sign_sanskrit || ascendant?.sign || 'N/A',
        moonSign: moon?.sign_sanskrit || moon?.sign || 'N/A',
        system: 'Vedic',
        ayanamsa: 'Lahiri'
      };
    }
  } catch (kundliError) {
    console.warn('Could not fetch kundli for dashboard:', kundliError);
  }
}
```

**Replace with:**
```typescript
// If dashboard API doesn't have data, extract from kundli
if (!data || !data.ascendant || !data.moonSign) {
  try {
    const kundliResponse = await getKundli(userId, birthDetails);
    
    // Extract D1 chart data
    const d1 = (kundliResponse as any).D1 || (kundliResponse as any).data?.kundli?.D1;
    
    if (d1) {
      const ascendant = d1.Ascendant;
      const planets = d1.Planets || {};
      const moon = planets.Moon;
      
      // Calculate current dasha from Moon's nakshatra
      let currentDasha = 'N/A';
      if (moon?.nakshatra_index !== undefined && moon?.nakshatra_index !== null && birthDetails?.date) {
        const { calculateCurrentDasha } = await import('@/utils/dasha');
        currentDasha = calculateCurrentDasha(moon.nakshatra_index, birthDetails.date);
      }
      
      data = {
        currentDasha: currentDasha,  // ← FIXED
        ascendant: ascendant?.sign_sanskrit || ascendant?.sign || 'N/A',
        moonSign: moon?.sign_sanskrit || moon?.sign || 'N/A',
        system: 'Vedic',
        ayanamsa: 'Lahiri'
      };
    }
  } catch (kundliError) {
    console.warn('Could not fetch kundli for dashboard:', kundliError);
  }
}
```

## Summary

1. ✅ **Chart Display:** Already fixed - verify keys are used correctly
2. ✅ **Current Dasha:** Create `utils/dasha.ts` and update `dashboard/page.tsx`

## Testing

After fixes:
- ✅ Dashboard shows Current Dasha (e.g., "Moon Dasha", "Mars Dasha")
- ✅ Chart displays all planets in correct houses
- ✅ Ascendant shows correct degree (2° 16' 47")

## API Keys Reference

**Planets:**
- `sign_sanskrit` - Sign name
- `degrees_in_sign` - Degree in sign (0-30°)
- `degree_dms`, `arcminutes`, `arcseconds` - DMS format
- `nakshatra_index` - For dasha calculation (0-26)

**Ascendant:**
- `sign_sanskrit` - Sign name
- `degrees_in_sign` - Degree in sign (0-30°)
- `house` - House number

**Houses:**
- `sign_sanskrit` - Sign in house
- `house` - House number (1-12)

