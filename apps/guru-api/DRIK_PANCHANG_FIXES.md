# Drik Panchang & JHORA Compatibility Fixes

## Status: IN PROGRESS

This document tracks all fixes applied to match Drik Panchang and JHORA exactly.

## ✅ COMPLETED FIXES

### 1. Planetary Positions (Phase 2)
- ✅ Fixed SWE flags: `FLG_SWIEPH | FLG_SIDEREAL | FLG_TRUEPOS | FLG_SPEED`
- ✅ Using TRUE NODE (not mean node) for Rahu/Ketu
- ✅ Lahiri Ayanamsa enforced globally
- ✅ Proper IST → UTC → JD conversion with seconds precision
- ✅ Correct Rashi, Nakshatra, Pada calculations
- ✅ Retrograde detection based on speed < 0
- ✅ All longitudes normalized 0-360

### 2. Core Drik Panchang Engine
- ✅ Created `src/jyotish/drik_panchang_engine.py`
- ✅ Global configuration for Drik Panchang standards
- ✅ Unified planet calculation method
- ✅ Unified house calculation method

### 3. Divisional Charts (Partial)
- ✅ Created `src/jyotish/varga_drik.py` with JHORA-compatible formulas
- ✅ Fixed Navamsa (D9) calculation with correct odd/even sign pattern
- ✅ Fixed Dasamsa (D10) calculation
- ✅ Fixed Dwadasamsa (D12) calculation
- ⚠️ Still need: D2 (Hora), D3 (Drekkana), D7 (Saptamsa), D20, D30, D40, D45, D60

## 🔄 IN PROGRESS

### 4. House Calculations
- ⚠️ Need to verify Placidus calculations match JHORA exactly
- ⚠️ Need to implement Whole Sign house system correctly
- ⚠️ Need to ensure house cusps match JHORA to decimal precision

### 5. Vimshottari Dasha
- ⚠️ Need to verify balance calculation matches JHORA exactly
- ⚠️ Need to verify antardasha calculations
- ⚠️ Need to verify pratyantardasha calculations

## 📋 PENDING FIXES

### 6. Shadbala Engine
- ⚠️ Need to verify all 6 balas match JHORA:
  - Sthana Bala (Positional)
  - Dig Bala (Directional)
  - Kala Bala (Temporal)
  - Cheshta Bala (Motional)
  - Naisargika Bala (Natural)
  - Drik Bala (Aspectual)

### 7. Yoga Detection
- ⚠️ Need to verify all yoga rules match JHORA definitions
- ⚠️ Need to ensure correct house-based yoga detection
- ⚠️ Need to verify Raj Yogas, Dhan Yogas, etc.

### 8. Transit Engine (Gochar)
- ⚠️ Need to verify transit calculations use same sidereal logic
- ⚠️ Need to ensure house placements match D1 exactly
- ⚠️ Need to verify transit + dasha integration

### 9. Rashi Charts
- ⚠️ Need to implement North Indian chart format correctly
- ⚠️ Need to implement South Indian chart format correctly
- ⚠️ Need to ensure both match JHORA display exactly

### 10. Additional Divisional Charts
- ⚠️ D2 (Hora)
- ⚠️ D3 (Drekkana)
- ⚠️ D7 (Saptamsa)
- ⚠️ D20 (Vimshamsa)
- ⚠️ D30 (Trimsamsa)
- ⚠️ D40, D45, D60 (optional)

## 🧪 VALIDATION REQUIRED

Test with birth data:
- **Date:** 16-05-1995
- **Time:** 18:38
- **Place:** Bangalore

Verify against Drik Panchang & JHORA:
- ✅ Planet degrees
- ⚠️ House cusps
- ⚠️ Navamsa chart
- ⚠️ Dasamsa chart
- ⚠️ Dasha timeline
- ⚠️ Nakshatra/Pada
- ⚠️ Retrograde states
- ⚠️ Rahu/Ketu (TRUE NODE)

## 📝 NOTES

- All calculations must use Swiss Ephemeris ONLY
- All calculations must use Lahiri Ayanamsa
- All calculations must use TRUE NODE (not mean node)
- All time conversions must account for IST (no DST)
- All longitudes must be normalized 0-360
- All nakshatra calculations: 13.333333333 degrees per nakshatra
- All pada calculations: 3.333333333 degrees per pada

