# Cursor UI Fix Prompt - Ascendant Sign Display

## Copy this prompt to Cursor UI:

```
Fix the Ascendant sign display issue in the chart components.

PROBLEM:
- D1 chart shows "Mithuna" but should show "Vrishchika"
- D9 chart shows "Mesha" but should show "Karka"

ROOT CAUSE:
The UI is displaying the house cusp sign instead of the Ascendant planet's sign. 
In Placidus house system, these can be different:
- House 8 cusp sign = Mithuna (from API Houses array)
- Ascendant planet sign = Vrishchika (from API Ascendant.sign_sanskrit)

FIX REQUIRED:

1. In components/Chart/SouthIndianChart.tsx (or wherever planets are rendered):
   - When displaying Ascendant, use the planet's sign property, NOT the house's signName
   - Example: const ascendantSign = ascendantPlanet?.sign; // NOT house.signName

2. In components/Chart/ChartContainer.tsx:
   - Verify ascendantSignName calculation uses:
     a. chartData.D1?.Ascendant?.sign_sanskrit (for D1)
     b. chartData.ascendant_sign_sanskrit (for divisional charts)
     c. ascendantPlanet?.sign from normalized houses
   - Add console.log to debug which value is being used

3. In components/Chart/utils.ts:
   - Verify the Ascendant planet object has sign: "Vrishchika" (not "Mithuna")
   - The planet.sign should come from apiData.lagnaSignSanskrit

API DATA STRUCTURE:
- D1: { D1: { Ascendant: { sign_sanskrit: "Vrishchika", house: 8 } } }
- D9: { D9: { ascendant_sign_sanskrit: "Karka" } }

EXPECTED RESULT:
- Display should show "Vrishchika" for D1, "Karka" for D9
- Use planet's sign, not house cusp sign

Add debug logs to trace the data flow and fix any place where house.signName is used instead of planet.sign for Ascendant display.
```

## Quick Fix Checklist:

- [ ] Check `SouthIndianChart.tsx` - use `planet.sign` not `house.signName` for Ascendant
- [ ] Check `NorthIndianChart.tsx` - same fix
- [ ] Verify `ChartContainer.tsx` ascendantSignName calculation
- [ ] Add debug logs to trace data flow
- [ ] Test D1 shows "Vrishchika"
- [ ] Test D9 shows "Karka"

