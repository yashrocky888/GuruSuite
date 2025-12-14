# API Data Structure for South Indian Chart Rendering

## ✅ API Status: CORRECT

The API provides all required data for South Indian chart rendering. The issue is in the UI's chart rendering logic.

---

## 📊 API Response Structure

### Ascendant Data:
```json
{
  "D1": {
    "Ascendant": {
      "sign_sanskrit": "Vrishchika",    // Sanskrit name
      "sign_index": 7,                  // 0-11 (0=Mesha, 7=Vrishchika)
      "degree": 212.2799,               // Full longitude
      "degrees_in_sign": 2.2799,        // Degree within sign
      "degree_dms": 212,                // Degree part
      "arcminutes": 16,                 // Minutes part
      "arcseconds": 47                   // Seconds part
    }
  }
}
```

### Planet Data:
```json
{
  "D1": {
    "Planets": {
      "Sun": {
        "sign_sanskrit": "Vrishabha",   // Sanskrit name
        "sign_index": 1,                 // 0-11 (0=Mesha, 1=Vrishabha)
        "degrees_in_sign": 1.4138,       // Degree within sign
        "degree_dms": 31,                // Degree part
        "arcminutes": 24,                // Minutes part
        "arcseconds": 49                 // Seconds part
      }
      // ... same structure for all planets
    }
  }
}
```

---

## 🎯 Sign Number Mapping

**Use `sign_index + 1` for box mapping (1-12):**

| sign_index | sign_index + 1 | Sign Sanskrit | English Name |
|------------|----------------|---------------|--------------|
| 0 | 1 | Mesha | Aries |
| 1 | 2 | Vrishabha | Taurus |
| 2 | 3 | Mithuna | Gemini |
| 3 | 4 | Karka | Cancer |
| 4 | 5 | Simha | Leo |
| 5 | 6 | Kanya | Virgo |
| 6 | 7 | Tula | Libra |
| 7 | 8 | Vrishchika | Scorpio |
| 8 | 9 | Dhanu | Sagittarius |
| 9 | 10 | Makara | Capricorn |
| 10 | 11 | Kumbha | Aquarius |
| 11 | 12 | Meena | Pisces |

---

## ✅ CORRECT South Indian Chart Rendering Logic

### Fixed Sign Grid (No Rotation):

```javascript
// ✅ CORRECT - Fixed sign grid
const FIXED_SIGN_BOXES = {
  1: "Mesha",      // Aries
  2: "Vrishabha",  // Taurus
  3: "Mithuna",    // Gemini
  4: "Karka",      // Cancer
  5: "Simha",      // Leo
  6: "Kanya",      // Virgo
  7: "Tula",       // Libra
  8: "Vrishchika", // Scorpio
  9: "Dhanu",      // Sagittarius
  10: "Makara",    // Capricorn
  11: "Kumbha",    // Aquarius
  12: "Meena"      // Pisces
};

function renderSouthIndianChart(apiResponse) {
  const d1 = apiResponse.D1;
  const ascendant = d1.Ascendant;
  const planets = d1.Planets;
  
  // Get lagna sign number
  const lagnaSignNumber = ascendant.sign_index + 1;  // 1-12
  
  // Render planets - place based on sign, NOT house
  Object.keys(planets).forEach(planetName => {
    const planet = planets[planetName];
    const planetSignNumber = planet.sign_index + 1;  // 1-12
    const planetDegree = planet.degrees_in_sign;
    const planetSign = planet.sign_sanskrit;
    
    // Place planet in fixed box based on sign
    const boxNumber = planetSignNumber;  // Direct mapping, NO rotation
    
    renderPlanetInBox(boxNumber, {
      name: planetName,
      sign: planetSign,
      degree: planetDegree
    });
    
    // If planet is in lagna sign, also mark as Ascendant location
    if (planetSignNumber === lagnaSignNumber) {
      markAsLagnaBox(boxNumber);
    }
  });
  
  // Render Ascendant label in lagna sign box
  renderAscendantLabel(lagnaSignNumber, {
    sign: ascendant.sign_sanskrit,
    degree: ascendant.degrees_in_sign
  });
}
```

---

## ❌ WRONG Logic (DO NOT USE):

```javascript
// ❌ WRONG - Don't rotate signs based on lagna
const lagnaSignNumber = ascendant.sign_index + 1;
const planetSignNumber = planet.sign_index + 1;
const rotatedBox = ((planetSignNumber - lagnaSignNumber + 12) % 12) + 1;  // ❌ WRONG!

// ❌ WRONG - Don't use house field for South Indian chart placement
const planetHouse = planet.house;  // This is for house-based charts, not South Indian
```

---

## 📋 Complete Example

For the test data (Lagna = Vrishchika, Sign #8):

```javascript
// API Response
const apiData = {
  "D1": {
    "Ascendant": {
      "sign_sanskrit": "Vrishchika",
      "sign_index": 7,  // Sign #8 (7+1)
      "degrees_in_sign": 2.2799
    },
    "Planets": {
      "Sun": {
        "sign_sanskrit": "Vrishabha",
        "sign_index": 1,  // Sign #2 (1+1) → Box 2
        "degrees_in_sign": 1.4138
      },
      "Moon": {
        "sign_sanskrit": "Vrishchika",
        "sign_index": 7,  // Sign #8 (7+1) → Box 8 (same as Lagna)
        "degrees_in_sign": 25.2501
      },
      "Venus": {
        "sign_sanskrit": "Mesha",
        "sign_index": 0,  // Sign #1 (0+1) → Box 1
        "degrees_in_sign": 5.6886
      }
      // ... etc
    }
  }
};

// Rendering (CORRECT):
// Box 1 (Mesha): Venus 5.69°
// Box 2 (Vrishabha): Sun 1.41°
// Box 8 (Vrishchika): Moon 25.25°, Ascendant 2.28° ← Lagna
// ... etc
```

---

## ✅ Verification Checklist

- [ ] Use `sign_index + 1` for box mapping (1-12)
- [ ] NO rotation calculation: `(planetSign - lagnaSign) % 12`
- [ ] NO house-based placement for South Indian charts
- [ ] Fixed sign grid: Aries always in Box 1, Taurus in Box 2, etc.
- [ ] Ascendant label goes in box = `lagnaSignNumber` (sign_index + 1)
- [ ] Planets placed in box = `planetSignNumber` (sign_index + 1)

---

## 🎯 Summary

**The API is correct and provides all required data:**
- ✅ `sign_sanskrit`: For display
- ✅ `sign_index`: 0-11 (convert to 1-12 with `+1`)
- ✅ `degrees_in_sign`: For degree display
- ✅ `degree_dms`, `arcminutes`, `arcseconds`: For DMS format

**The UI needs to:**
- ✅ Use `sign_index + 1` for fixed box mapping (1-12)
- ✅ NO rotation or offset calculations
- ✅ Place planets based on sign, not house
- ✅ Fixed sign grid (Aries=Box 1, Taurus=Box 2, ..., Pisces=Box 12)

**The API provides correct data - the fix is in the UI's rendering logic!** ✅

