# Planet Mapping Fix Guide

## Problem Analysis

### API Data (Correct):
```
Ascendant: House=8, Sign=Vrishchika, Degree=2.2799
Sun: House=2, Sign=Vrishabha, Degree=1.4138
Moon: House=8, Sign=Vrishchika, Degree=25.2501
Mars: House=5, Sign=Simha, Degree=2.2504
Mercury: House=2, Sign=Vrishabha, Degree=22.1178
Jupiter: House=8, Sign=Vrishchika, Degree=18.6872
Venus: House=1, Sign=Mesha, Degree=5.6886
Saturn: House=11, Sign=Kumbha, Degree=28.8956
Rahu: House=7, Sign=Tula, Degree=10.7944
Ketu: House=1, Sign=Mesha, Degree=10.7944

Houses:
House 1: Vrishchika
House 2: Dhanu
House 3: Makara
House 4: Kumbha
House 5: Meena
House 6: Mesha
House 7: Vrishabha
House 8: Mithuna
House 9: Karka
House 10: Simha
House 11: Kanya
House 12: Tula
```

### Expected Chart Display:
- **House 1 (Vrishchika)**: Venus (5.69°), Ketu (10.79°)
- **House 2 (Dhanu)**: Sun (1.41°), Mercury (22.12°)
- **House 5 (Meena)**: Mars (2.25°)
- **House 7 (Vrishabha)**: Rahu (10.79°)
- **House 8 (Mithuna)**: Moon (25.25°), Jupiter (18.69°), Ascendant (2.28°)
- **House 11 (Kanya)**: Saturn (28.90°)

### Current UI Issue (from screenshot):
- **House 1 (Vrishchika)**: Ketu (5.69°) ❌ Missing Venus
- **House 2 (Dhanu)**: Mercury (22.12°), Sun (1.41°) ✅ Correct
- **House 5 (Meena)**: Mars (2.25°) ✅ Correct
- **House 7 (Vrishabha)**: Rahu (10.79°) ✅ Correct
- **House 8 (Mithuna)**: Jupiter (18.69°), Moon (25.25°), Ascendant (212° 16' 47") ✅ Correct (but Ascendant degree format wrong)
- **House 11 (Kanya)**: Saturn (28.90°) ✅ Correct

## Root Cause

1. **Venus missing from House 1**: Planet extraction or filtering issue
2. **Ascendant degree format**: Showing total degree (212°) instead of degrees in sign (2.28°)

## Fix Strategy

1. **Ensure all planets are extracted**: Check planet extraction logic in `ChartContainer.tsx`
2. **Fix Ascendant degree display**: Use `degrees_in_sign` (2.28°) instead of total degree (212°)
3. **Add debug logging**: Log all planets being mapped to houses
4. **Verify house mapping**: Ensure planets are placed in correct houses using `planet.house` from API

