# Divisional Charts Fix - API & UI

## Problem
Divisional charts (D2, D3, D4, D7, D9, D10, D12) are not displaying correctly because:
1. **API Issue**: Returns different structure than D1
2. **UI Issue**: Doesn't handle divisional chart format properly

## API Response Comparison

### D1 (Working):
```json
{
  "D1": {
    "Ascendant": {
      "sign_sanskrit": "Vrishchika",
      "degrees_in_sign": 2.2799,
      "degree_dms": 212,
      "arcminutes": 16,
      "arcseconds": 47,
      "house": 8
    },
    "Planets": {
      "Sun": {
        "sign_sanskrit": "Vrishabha",
        "degrees_in_sign": 1.4138,
        "degree_dms": 31,
        "arcminutes": 24,
        "arcseconds": 49
      }
    },
    "Houses": [...]
  }
}
```

### D2/D3/D9 (Not Working):
```json
{
  "D2": {
    "ascendant": 94.5598,  // ❌ Just a float, not an object
    "ascendant_sign": "Cancer",  // ❌ English, not Sanskrit
    "planets": {
      "Sun": {
        "sign": "Taurus",  // ❌ English, not sign_sanskrit
        "degrees_in_sign": 2.8276,  // ✅ Has this
        "house": 2
        // ❌ Missing: degree_dms, arcminutes, arcseconds
      }
    }
    // ❌ Missing: Houses array
  }
}
```

## Fix Required

### Option 1: Fix API (Recommended)
Update backend to return same structure as D1 for all divisional charts.

### Option 2: Fix UI (Workaround)
Update UI to handle current API format and convert it to expected format.

## UI Fix Implementation

Update `guru-web/components/Chart/ChartContainer.tsx` to handle divisional chart format:

```typescript
// Around line 201-220, in the else block for divisional charts:

} else {
  // Handle divisional chart format: { ascendant: float, ascendant_sign: string, planets: {...} }
  // OR: { chartType: "D9", lagnaSign: "...", planets: [...], houses: [...] }
  
  // Check for divisional chart format: { ascendant, ascendant_sign, planets }
  if ((chartData as any).ascendant !== undefined && typeof (chartData as any).ascendant === 'number') {
    // Divisional chart format: ascendant is a float, need to convert
    const ascendantDegree = (chartData as any).ascendant;
    const ascendantSign = (chartData as any).ascendant_sign || 'Mesha';
    
    // Convert English sign to Sanskrit
    const sanskritSign = convertToSanskritSign(ascendantSign);
    const signIndex = getSignNum(sanskritSign);
    const degreesInSign = ascendantDegree % 30;
    
    // Calculate DMS from degrees_in_sign
    const degreeDms = Math.floor(degreesInSign);
    const minutes = Math.floor((degreesInSign - degreeDms) * 60);
    const seconds = Math.floor(((degreesInSign - degreeDms) * 60 - minutes) * 60);
    
    ascendantData = {
      sign: sanskritSign,
      sign_sanskrit: sanskritSign,
      degree: ascendantDegree,
      degree_dms: degreeDms,
      arcminutes: minutes,
      arcseconds: seconds,
      degrees_in_sign: degreesInSign,
      house: 1, // Default, will be calculated from sign matching
    };
    
    // Extract planets from object
    if ((chartData as any).planets && typeof (chartData as any).planets === 'object') {
      const planetsEntries = Object.entries((chartData as any).planets);
      
      planetsArray = planetsEntries.map(([name, data]: [string, any]) => {
        // Convert English sign to Sanskrit
        const englishSign = data.sign || '';
        const sanskritSign = convertToSanskritSign(englishSign);
        const displayDegree = data.degrees_in_sign !== undefined 
          ? data.degrees_in_sign 
          : (data.degree % 30);
        
        // Calculate DMS from degrees_in_sign
        const degreeInSign = displayDegree;
        const degreeDms = Math.floor(degreeInSign);
        const minutes = Math.floor((degreeInSign - degreeDms) * 60);
        const seconds = Math.floor(((degreeInSign - degreeDms) * 60 - minutes) * 60);
        
        return {
          name,
          sign: sanskritSign,
          house: data.house || 1,
          degree: displayDegree,
          degrees_in_sign: displayDegree,
          degree_dms: degreeDms,
          degree_minutes: minutes,
          degree_seconds: seconds,
          total_degree: data.degree,
          retrograde: data.retro || false,
          nakshatra: data.nakshatra,
          pada: data.pada,
        };
      });
    }
    
    // Generate houses array from ascendant sign (whole sign system)
    const lagnaSignNum = signIndex;
    for (let i = 1; i <= 12; i++) {
      const houseSignNum = getSignForHouse(i, lagnaSignNum);
      housesArray.push({
        house: i,
        sign: getSignName(houseSignNum),
        sign_sanskrit: getSignName(houseSignNum),
        degree: 0,
        degrees_in_sign: 0,
      });
    }
  } else {
    // Legacy format handling
    planetsArray = (chartData as any).planets || [];
    // ... existing code
  }
}
```

## API Fix (Backend)

Update `guru-api/varga_calculations.py` or `guru-api/api_routes.py` to return same structure as D1:

```python
# Instead of returning:
{
    "ascendant": 94.5598,
    "ascendant_sign": "Cancer",
    "planets": {...}
}

# Return:
{
    "Ascendant": {
        "sign_sanskrit": "Karka",
        "degrees_in_sign": 4.5598,
        "degree_dms": 4,
        "arcminutes": 33,
        "arcseconds": 35,
        "house": 1,
        "degree": 94.5598
    },
    "Planets": {
        "Sun": {
            "sign_sanskrit": "Vrishabha",
            "degrees_in_sign": 2.8276,
            "degree_dms": 2,
            "arcminutes": 49,
            "arcseconds": 39,
            "house": 2,
            "degree": 32.8276
        },
        # ... all planets
    },
    "Houses": [
        {"house": 1, "sign_sanskrit": "Karka", "degrees_in_sign": 4.5598},
        # ... 12 houses
    ]
}
```

## Recommendation

**Fix UI first** (workaround) - handles current API format
**Then fix API** (proper solution) - returns consistent structure

