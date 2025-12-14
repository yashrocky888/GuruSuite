# UI Fix Guide - Kundli API Integration

## ✅ API Status: WORKING CORRECTLY

The API is returning all data correctly. The issue is in the UI parsing/display logic.

---

## 🔍 What to Check in UI Code

### 1. **Field Name Mapping**

The API returns these exact field names. Make sure UI uses them:

#### For D1 Chart:

**Ascendant:**
```javascript
// ✅ CORRECT
const asc = response.D1.Ascendant;
const degree = asc.degree_dms;        // int (0-360)
const minutes = asc.arcminutes;        // int (0-59)
const seconds = asc.arcseconds;        // int (0-59)
const sign = asc.sign_sanskrit;        // "Vrishchika" (NOT "sign")
const degreesInSign = asc.degrees_in_sign; // float (0-29.999)
const nakshatra = asc.nakshatra;       // "Vishakha"
```

**Planets:**
```javascript
// ✅ CORRECT
const sun = response.D1.Planets.Sun;
const degree = sun.degree_dms;         // int (0-360)
const minutes = sun.arcminutes;         // int (0-59)
const seconds = sun.arcseconds;        // int (0-59)
const sign = sun.sign_sanskrit;        // "Vrishabha" (NOT "sign")
const house = sun.house;               // int (1-12)
const nakshatra = sun.nakshatra;       // "Krittika"
const retro = sun.retro;               // boolean (true/false)
```

### 2. **Common UI Mistakes to Fix**

#### ❌ WRONG:
```javascript
// Don't use English sign name
const sign = planet.sign;  // Returns "Taurus" instead of "Vrishabha"

// Don't use degree field directly for DMS
const dms = planet.degree;  // Returns float, not DMS format

// Don't assume retro field format
if (planet.retro === "℞")  // retro is boolean, not string
```

#### ✅ CORRECT:
```javascript
// Use Sanskrit sign name
const sign = planet.sign_sanskrit;  // "Vrishabha"

// Use DMS fields
const dms = `${planet.degree_dms}° ${planet.arcminutes}' ${planet.arcseconds}"`;

// Check retro as boolean
const retroSymbol = planet.retro ? "℞" : "";
```

### 3. **Divisional Charts Structure**

For D2, D3, D4, D7, D9, D10, D12:

```javascript
// ✅ CORRECT Structure
const d7 = response.D7;
const d7Asc = d7.ascendant;           // float
const d7AscSign = d7.ascendant_sign;  // int (0-11)
const d7Planets = d7.planets;         // object with planet names as keys

// Access planet in divisional chart
const sunD7 = d7.planets.Sun;
const sunD7Degree = sunD7.degree;
const sunD7Sign = sunD7.sign;         // string
const sunD7House = sunD7.house;        // int (1-12)
```

### 4. **Error Handling**

The API now returns detailed error objects:

```javascript
// ✅ CORRECT Error Handling
try {
  const response = await fetch(apiUrl);
  const data = await response.json();
  
  if (!response.ok) {
    // Error response structure
    const error = data.detail;
    console.error('API Error:', {
      error: error.error,        // Error type
      message: error.message,   // Error message
      type: error.type           // Error class name
    });
    throw new Error(error.message || 'API Error');
  }
  
  // Process data...
} catch (error) {
  console.error('❌ API Error:', {
    message: error.message,
    response: error.response?.data,
    status: error.response?.status
  });
}
```

---

## 📋 Complete Field Reference

### D1.Ascendant Fields:
- `degree` (float): Full longitude 0-360
- `degree_dms` (int): Degree part (0-360)
- `arcminutes` (int): Minutes part (0-59)
- `arcseconds` (int): Seconds part (0-59)
- `sign` (string): English name ("Scorpio")
- `sign_sanskrit` (string): Sanskrit name ("Vrishchika") ⭐ **USE THIS**
- `sign_index` (int): 0-11
- `degrees_in_sign` (float): 0-29.999
- `house` (int): 1-12
- `lord` (string): House lord name
- `nakshatra` (string): Nakshatra name
- `nakshatra_index` (int): 0-26
- `pada` (int): 1-4

### D1.Planets[PlanetName] Fields:
- `degree` (float): Full longitude 0-360
- `degree_dms` (int): Degree part (0-360) ⭐ **USE THIS**
- `arcminutes` (int): Minutes part (0-59) ⭐ **USE THIS**
- `arcseconds` (int): Seconds part (0-59) ⭐ **USE THIS**
- `sign` (string): English name ("Taurus")
- `sign_sanskrit` (string): Sanskrit name ("Vrishabha") ⭐ **USE THIS**
- `sign_index` (int): 0-11
- `degrees_in_sign` (float): 0-29.999
- `house` (int): 1-12
- `house_lord` (string): House lord name
- `nakshatra` (string): Nakshatra name
- `nakshatra_index` (int): 0-26
- `pada` (int): 1-4
- `retro` (boolean): true/false ⭐ **USE THIS**
- `speed` (float): Speed in degrees/day

---

## 🧪 Test API Response

Test the API directly to see the exact structure:

```bash
curl "https://guru-api-660206747784.us-central1.run.app/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata"
```

Or in browser:
```
https://guru-api-660206747784.us-central1.run.app/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata
```

---

## ✅ Quick Fix Checklist

- [ ] Use `sign_sanskrit` instead of `sign` for Sanskrit names
- [ ] Use `degree_dms`, `arcminutes`, `arcseconds` for DMS display
- [ ] Check `retro` as boolean (not string)
- [ ] Handle divisional charts structure correctly (`ascendant`, `planets`)
- [ ] Add proper error handling for API responses
- [ ] Check for null/undefined values before accessing nested properties
- [ ] Use optional chaining (`?.`) when accessing nested data

---

## 📞 If Still Having Issues

1. **Check Browser Console**: Look for JavaScript errors
2. **Check Network Tab**: Verify the API response structure
3. **Compare**: Match the actual API response with what UI expects
4. **Test**: Use the test URL above to see exact API response

The API is working correctly - the fix is in the UI code! 🚀

