# UI Fix Prompt - Current Dasha & Final Verification

## Status
✅ Chart display fixed - planets matched to houses by sign
✅ Degree display fixed - all degrees in 0-30° format
❌ **Current Dasha showing "N/A" - needs fix**

## Task
Fix the "Current Dasha: N/A" issue in the dashboard by calculating dasha from Moon's nakshatra.

## API Data Available
The API response includes:
```json
{
  "D1": {
    "Planets": {
      "Moon": {
        "nakshatra_index": 16,  // ← Use this for dasha calculation
        "nakshatra": "Vishakha",
        "sign_sanskrit": "Vrishchika"
      }
    }
  }
}
```

## Fix Required

### Step 1: Create Dasha Utility
**File:** `guru-web/utils/dasha.ts` (create if doesn't exist)

```typescript
/**
 * Calculate current Vimshottari Dasha from Moon's nakshatra
 */
export function calculateCurrentDasha(moonNakshatraIndex: number, birthDate: string): string {
  // Nakshatra to starting Dasha Lord (Vimshottari system - 27 nakshatras)
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
  
  // Dasha periods in years (Vimshottari - 120 years total)
  const dashaPeriods: Record<string, number> = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
  };
  
  // Calculate which dasha we're in (cycles through all 9 dashas)
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
if (d1) {
  const ascendant = d1.Ascendant;
  const planets = d1.Planets || {};
  const moon = planets.Moon;
  
  data = {
    currentDasha: data?.currentDasha || 'N/A',  // ← FIX THIS LINE
    ascendant: ascendant?.sign_sanskrit || ascendant?.sign || 'N/A',
    moonSign: moon?.sign_sanskrit || moon?.sign || 'N/A',
    system: 'Vedic',
    ayanamsa: 'Lahiri'
  };
}
```

**Replace with:**
```typescript
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
```

## Expected Result
- ✅ Dashboard shows: "Current Dasha: Moon Dasha" (or other planet, not "N/A")
- ✅ Calculated from Moon's nakshatra_index
- ✅ Uses Vimshottari Dasha system (120 years cycle)

## Testing
1. Enter birth details
2. Go to dashboard
3. Verify "Current Dasha" shows a planet name (e.g., "Moon Dasha", "Mars Dasha")
4. Should NOT show "N/A"

## Files to Update
1. ✅ Create: `guru-web/utils/dasha.ts`
2. ✅ Update: `guru-web/app/dashboard/page.tsx`

## Notes
- API already provides `nakshatra_index` in `D1.Planets.Moon.nakshatra_index`
- Birth date is available in `birthDetails.date` from Zustand store
- Vimshottari Dasha: 120 years total, 9 planets, cycles through all dashas

