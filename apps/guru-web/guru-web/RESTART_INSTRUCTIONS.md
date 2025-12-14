# Restart Instructions - Fix Chart Data Mismatch

## Issue
Jupiter showing in wrong sign (Dhanu instead of Vrishchika/Scorpio)

## Steps to Fix

### 1. Clear Browser Cache
**In Browser:**
- Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux) for hard refresh
- Or open DevTools (F12) → Right-click refresh button → "Empty Cache and Hard Reload"

### 2. Clear Frontend Store (Zustand)
**In Browser Console:**
```javascript
// Clear kundli store
localStorage.clear();
sessionStorage.clear();
// Then refresh the page
```

### 3. Restart Frontend Dev Server
```bash
# Stop current server (Ctrl+C in the terminal running it)
# Then restart:
cd guru-web
npm run dev
```

### 4. Verify API Response
```bash
# Check if API returns correct data
curl "http://localhost:8000/api/v1/kundli" | python3 -m json.tool | grep -A 5 "Jupiter"
```

### 5. Check Console Logs
**In Browser DevTools Console:**
- Look for:
  - `=== CHART CONTAINER DEBUG ===`
  - `Raw chartData:`
  - `Planet Jupiter: API says house=... sign=...`
  - `Final normalized houses:`

### 6. If Still Wrong
1. Check the `Raw chartData` in console
2. Verify it has `data.kundli.Planets.Jupiter.sign = "Scorpio"`
3. Check if `convertToSanskritSign` is converting correctly
4. Verify `Houses` array is being used

## Quick Fix Command
```bash
# Restart frontend
cd guru-web
pkill -f "next dev"
npm run dev
```

Then hard refresh browser: `Cmd+Shift+R`

