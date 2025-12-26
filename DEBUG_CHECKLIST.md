# 🔍 DEBUG CHECKLIST - UI PLANET PLACEMENT

## Step 1: Check Browser Console Logs

After restarting the frontend server, open browser console and look for:

1. **"API HOUSES ARRAY:"**
   - Should show: `[{house: 1, sign: "Vrischika"}, {house: 2, sign: "Dhanu"}, ...]`
   - Verify House 8 sign: Should be "Vrischika" (NOT "Mithuna")

2. **"API PLANETS WITH HOUSES:"**
   - Should show: `[{name: "Moon", sign: "Vrischika", house: 8}, ...]`
   - Verify Moon house: Should be `8` (NOT `1`)
   - Verify Jupiter house: Should be `8` (NOT `1`)
   - Verify Venus house: Should be `6` (NOT `1`)
   - Verify Ketu house: Should be `6` (NOT `1`)

3. **"House X (Sign): Planet1 (sign), Planet2 (sign)"**
   - House 1 (Vrischika): Should show only "Ascendant"
   - House 6 (Mesha): Should show "Venus, Ketu"
   - House 7 (Vrishabha): Should show "Sun, Mercury"
   - House 8 (Vrischika): Should show "Moon, Jupiter"

## Step 2: If API Data is Wrong

If console shows wrong house numbers from API:
- **Problem is in API**, not UI
- Check API endpoint: `/api/kundli`
- Verify API is using correct house calculation logic
- Check if API server needs restart

## Step 3: If API Data is Correct but UI Shows Wrong

If console shows correct API data but UI displays wrong:
- **Problem is in UI rendering**
- Check if planets are being filtered correctly
- Verify `planet.house === apiHouse.house` matching logic
- Check if there's a caching issue

## Step 4: Restart Frontend Server

```bash
cd apps/guru-web/guru-web
# Stop current server (Ctrl+C)
rm -rf .next  # Clear cache
npm run dev   # Restart
```

Then hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

## Expected Console Output (CORRECT)

```
API HOUSES ARRAY: [
  {house: 1, sign: "Vrischika"},
  {house: 2, sign: "Dhanu"},
  ...
  {house: 6, sign: "Mesha"},
  {house: 7, sign: "Vrishabha"},
  {house: 8, sign: "Vrischika"},  ← Should be Vrischika, NOT Mithuna
  ...
]

API PLANETS WITH HOUSES: [
  {name: "Moon", sign: "Vrischika", house: 8},      ← Should be house 8
  {name: "Jupiter", sign: "Vrischika", house: 8},  ← Should be house 8
  {name: "Venus", sign: "Mesha", house: 6},        ← Should be house 6
  {name: "Ketu", sign: "Mesha", house: 6},         ← Should be house 6
  {name: "Sun", sign: "Vrishabha", house: 7},     ← Should be house 7
  {name: "Mercury", sign: "Vrishabha", house: 7}, ← Should be house 7
  ...
]

House 1 (Vrischika): Ascendant (Vrischika)
House 6 (Mesha): Venus (Mesha), Ketu (Mesha)
House 7 (Vrishabha): Sun (Vrishabha), Mercury (Vrishabha)
House 8 (Vrischika): Moon (Vrischika), Jupiter (Vrischika)
```
