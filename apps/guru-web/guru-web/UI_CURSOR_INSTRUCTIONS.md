# UI Cursor Instructions - Final Fixes

## Status
✅ Chart display fixed - planets matched to houses by sign
✅ Degree display fixed - all degrees in 0-30° format  
✅ Divisional charts fixed - handles different API format
❌ **Current Dasha showing "N/A" - needs fix**

## Task
Fix the "Current Dasha: N/A" issue in the dashboard.

## Quick Fix

### Step 1: Create `guru-web/utils/dasha.ts`
```typescript
export function calculateCurrentDasha(moonNakshatraIndex: number, birthDate: string): string {
  const nakshatraDashaLords = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
  ];
  
  if (moonNakshatraIndex === undefined || moonNakshatraIndex === null) return 'N/A';
  
  const startingLord = nakshatraDashaLords[moonNakshatraIndex % 27];
  const birth = new Date(birthDate);
  const now = new Date();
  const yearsSinceBirth = (now.getTime() - birth.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
  
  const dashaPeriods: Record<string, number> = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
  };
  
  const dashaLords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'];
  const startIndex = dashaLords.indexOf(startingLord);
  
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

### Step 2: Update `guru-web/app/dashboard/page.tsx`

Find this section (around line 41-52):
```typescript
if (d1) {
  const ascendant = d1.Ascendant;
  const planets = d1.Planets || {};
  const moon = planets.Moon;
  
  data = {
    currentDasha: data?.currentDasha || 'N/A',  // ← FIX THIS
    ascendant: ascendant?.sign_sanskrit || ascendant?.sign || 'N/A',
    moonSign: moon?.sign_sanskrit || moon?.sign || 'N/A',
    // ...
  };
}
```

Replace with:
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
- Dashboard shows: "Current Dasha: Moon Dasha" (or other planet, not "N/A")
- Uses Moon's `nakshatra_index` from API
- Calculates Vimshottari Dasha from birth date

## Files to Update
1. ✅ Create: `guru-web/utils/dasha.ts`
2. ✅ Update: `guru-web/app/dashboard/page.tsx` (around line 41-52)

## API Data Available
```json
{
  "D1": {
    "Planets": {
      "Moon": {
        "nakshatra_index": 16,  // ← Use this
        "nakshatra": "Vishakha"
      }
    }
  }
}
```

