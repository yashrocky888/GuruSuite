# House Sign Mismatch Issue

## Problem

The API is returning house numbers for planets that don't match the house signs:

### API Data:
```
Houses:
House 1: Vrishchika (Scorpio)
House 2: Dhanu (Sagittarius)
House 3: Makara (Capricorn)
House 4: Kumbha (Aquarius)
House 5: Meena (Pisces)
House 6: Mesha (Aries)
House 7: Vrishabha (Taurus)
House 8: Mithuna (Gemini)
House 9: Karka (Cancer)
House 10: Simha (Leo)
House 11: Kanya (Virgo)
House 12: Tula (Libra)

Planets:
Sun: House=2, Sign=Vrishabha ❌ (House 2 is Dhanu, not Vrishabha!)
Moon: House=8, Sign=Vrishchika ❌ (House 8 is Mithuna, not Vrishchika!)
Mars: House=5, Sign=Simha ❌ (House 5 is Meena, not Simha!)
Mercury: House=2, Sign=Vrishabha ❌ (House 2 is Dhanu, not Vrishabha!)
Jupiter: House=8, Sign=Vrishchika ❌ (House 8 is Mithuna, not Vrishchika!)
Venus: House=1, Sign=Mesha ❌ (House 1 is Vrishchika, not Mesha!)
Saturn: House=11, Sign=Kumbha ❌ (House 11 is Kanya, not Kumbha!)
Rahu: House=7, Sign=Tula ❌ (House 7 is Vrishabha, not Tula!)
Ketu: House=1, Sign=Mesha ❌ (House 1 is Vrishchika, not Mesha!)
```

## Root Cause

The API's `house` field for planets is NOT matching the house signs. This suggests:
1. The API is calculating houses incorrectly, OR
2. The `house` field represents something else (like sign-based house calculation), OR
3. There's a mismatch between house cusps and planet positions

## Solution

**Option 1: Calculate house from planet sign and house signs**
- Match planet's sign to the house that contains that sign
- Example: Sun is in Vrishabha → Find which house has Vrishabha → House 7

**Option 2: Use API house field but verify against house signs**
- If planet's sign matches house sign, use API house
- If not, calculate house from sign matching

**Option 3: Fix API house calculation**
- The backend needs to calculate houses correctly based on house cusps

## Expected Behavior

For professional astrology apps using Placidus system:
- A planet's house is determined by which house cusp it falls between
- A planet's sign is its zodiac sign position
- These are independent - a planet can be in House 2 but Sign Vrishabha if House 2's cusp is in Dhanu but the planet is in Vrishabha

## Current UI Behavior

The UI is currently using the API's `house` field directly, which causes planets to appear in houses with different signs, making the chart look incorrect.

