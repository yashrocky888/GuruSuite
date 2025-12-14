# Monorepo Setup Complete

## ✅ Structure Created

```
GuruSuite/
├── apps/
│   ├── guru-api/          # ALL astro calculations
│   └── guru-web/          # UI rendering ONLY
├── README.md
├── ARCHITECTURE.md
└── .gitignore
```

## ✅ Core Rules Enforced

### API (guru-api)
- ✅ Swiss Ephemeris (sidereal, Lahiri)
- ✅ Runtime assertions: `house == sign` for varga charts
- ✅ Final payload logging for D10, D7, D12
- ✅ Whole Sign system for divisional charts

### UI (guru-web)
- ✅ Uses `planet.house` directly from API
- ✅ Runtime assertions verify no calculations
- ✅ Fixed sign grid for varga charts
- ⚠️ **TODO**: Remove calculation code from `guru-astro-api` module

## ⚠️ Action Required

### Files to Review/Remove in UI:

1. `apps/guru-web/guru-astro-api/src/astro-core/calculators/houseCalculator.ts`
   - **Action**: DELETE or DISABLE all house calculation logic
   - **Reason**: API provides houses, UI should not calculate

2. `apps/guru-web/guru-astro-api/src/services/astroService.ts`
   - **Action**: Remove any calculation logic, keep only API calls
   - **Reason**: All calculations must be in API

3. `apps/guru-web/guru-astro-api/src/astro-core/charts/rashiChartNorth.ts`
   - **Action**: Remove rotation/remapping logic for varga charts
   - **Reason**: Varga charts use fixed sign grid

## Next Steps

1. **Remove UI Calculations**: Delete/disable calculation code in `guru-astro-api`
2. **Lock API Contract**: Ensure API response structure is fixed
3. **Add Tests**: Create verification tests against JHora/Prokerala
4. **Deploy**: Deploy both API and UI with new structure

## Verification

Run tests:
```bash
cd apps/guru-api
python test_d10_prokerala.py
python test_varga_assertions.py
```

Check UI:
- No console errors about calculations
- Planets appear in correct houses (from API)
- Signs match API response exactly

