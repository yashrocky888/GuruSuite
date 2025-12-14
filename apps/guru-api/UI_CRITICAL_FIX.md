# UI Cursor Instructions - Final Fixes

## Status
✅ Chart display fixed - planets matched to houses by sign
✅ Degree display fixed - all degrees in 0-30° format  
✅ Divisional charts fixed - handles different API format
❌ **Current Dasha showing "N/A" - needs fix**

## Task
Fix the "Current Dasha: N/A" issue in the dashboard.

## ✅ API Provides current_dasha (Preferred Method)

The API response now includes `current_dasha` field:
```json
{
  "current_dasha": {
    "mahadasha": "Venus",
    "antardasha": "Mercury",
    "display": "Venus Dasha - Mercury Antardasha"
  },
  "D1": { ... }
}
```

**Use API value first, calculate only as fallback.**

## Quick Fix

### Option 1: Use API Value (Recommended)

### Step 1: Update `guru-web/app/dashboard/page.tsx`
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

Replace with (Option 1 - Use API value):
```typescript
// Get kundli response (includes current_dasha)
const kundliResponse = await getKundli(userId, birthDetails);

if (kundliResponse?.D1) {
  const d1 = kundliResponse.D1;
  const ascendant = d1.Ascendant;
  const planets = d1.Planets || {};
  const moon = planets.Moon;
  
  // Use current_dasha from API (preferred - more accurate)
  let currentDasha = kundliResponse.current_dasha?.display || 'N/A';
  
  // Fallback: Calculate if API doesn't provide it
  if (currentDasha === 'N/A' && moon?.nakshatra_index !== undefined && moon?.nakshatra_index !== null && birthDetails?.date) {
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

### Option 2: Calculate from nakshatra_index (Fallback Only)

### Step 1: Create `guru-web/utils/dasha.ts` (only if not using API value)

## Expected Result
- ✅ Dashboard shows: "Current Dasha: Venus Dasha - Mercury Antardasha" (or other, not "N/A")
- ✅ Uses `current_dasha.display` from API (preferred)
- ✅ Falls back to calculation if API value missing

## Files to Update
1. ✅ Update: `guru-web/app/dashboard/page.tsx` (use `current_dasha` from API)
2. ⚠️ Optional: Create `guru-web/utils/dasha.ts` (only for fallback calculation)

## API Data Available

**Primary (Recommended):**
```json
{
  "current_dasha": {
    "mahadasha": "Venus",
    "antardasha": "Mercury",
    "display": "Venus Dasha - Mercury Antardasha"
  }
}
```

**Fallback (if current_dasha missing):**
```json
{
  "D1": {
    "Planets": {
      "Moon": {
        "nakshatra_index": 17,  // ← Use for calculation fallback
        "nakshatra": "Jyeshtha"
      }
    }
  }
}
```

## Recommendation
✅ **Use Option 1** - API provides `current_dasha.display` directly
✅ More accurate (uses Drik Panchang/JHORA methodology)
✅ Simpler code (no calculation needed)
✅ Includes antardasha information

