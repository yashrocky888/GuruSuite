# Varga Engine Contract - Prokerala/JHora Compatibility

## 🔒 NON-NEGOTIABLE RULES

### 1. Single Source of Truth
- **ALL** varga calculations MUST go through `varga_engine.py`
- API routes MUST use `build_varga_chart()` - NEVER call `calculate_varga()` directly
- This ensures consistency across all endpoints

### 2. House Calculation (Universal Formula)
For ANY chart (D1, D2, D3, D4, D7, D9, D10, D12, etc.):

```
AscendantSignIndex = floor(AscendantAbsoluteLongitude / 30)
PlanetSignIndex = floor(PlanetAbsoluteLongitude / 30)

houseNumber = ((PlanetSignIndex - AscendantSignIndex + 12) % 12) + 1
```

**CRITICAL RULES:**
- DO NOT use `degrees_in_sign` for house calculation
- DO NOT use `% 30` incorrectly
- Degrees are needed ONLY for varga division math, NOT house numbering
- Ascendant house is ALWAYS 1 (not `sign_index + 1`)

### 3. Ascendant House Invariant
For ALL varga charts:
- `ascendant.house == 1` (ALWAYS)
- This is a fundamental Vedic astrology rule: Lagna = House 1
- DO NOT calculate ascendant house as `sign_index + 1`

### 4. Prokerala/JHora Compatibility
- Prokerala and JHora outputs are the canonical reference
- All varga calculations must match Prokerala/JHora EXACTLY
- If Prokerala omits a planet in a specific varga, the API must also omit it
- No approximations or simplified methods

### 5. Standardized API Response
Every varga chart API must return this structure:

```json
{
  "chart_type": "D3",
  "ayanamsa": "Lahiri",
  "calculation_source": "Prokerala/JHora",
  "ascendant": {
    "sign": "Vrishchika",
    "sign_index": 7,
    "degree": 2.27,
    "house": 1,
    "degree_dms": 2,
    "arcminutes": 16,
    "arcseconds": 12,
    "degree_formatted": "2° 16′ 12″"
  },
  "houses": [
    { "house": 1, "sign": "Vrishchika", "sign_index": 7, "planets": [...] },
    ...
    { "house": 12, "sign": "Tula", "sign_index": 6, "planets": [...] }
  ],
  "planets": {
    "Sun": {
      "sign": "Vrishabha",
      "sign_index": 1,
      "house": 7,
      "degree": 1.41,
      "degree_dms": 1,
      "arcminutes": 24,
      "arcseconds": 36,
      "degree_formatted": "1° 24′ 36″"
    },
    ...
  }
}
```

## Runtime Assertions

The varga engine includes hard runtime assertions that will FAIL if violated:

1. **Ascendant House Assertion:**
   ```python
   assert ascendant.house == 1, f"Lagna house must be 1, got {ascendant.house}"
   ```

2. **Houses Array Length:**
   ```python
   assert len(houses) == 12, f"Must have exactly 12 houses, got {len(houses)}"
   ```

3. **Planet House Range:**
   ```python
   assert 1 <= planet.house <= 12, f"Planet house {planet.house} not in range 1-12"
   ```

4. **House Calculation Formula:**
   ```python
   expected_house = ((planet_sign_index - asc_sign_index + 12) % 12) + 1
   assert planet.house == expected_house, f"House calculation mismatch"
   ```

## Varga Calculation Formulas

### D2 (Hora) - 2 divisions (15° each)
- Odd signs: First hora (0-15°) → Leo, Second hora (15-30°) → Cancer
- Even signs: First hora (0-15°) → Cancer, Second hora (15-30°) → Leo
- Degree: `(degrees_in_sign * 2) % 30`

### D3 (Drekkana) - 3 divisions (10° each)
- 1st drekkana (0-10°): same sign
- 2nd drekkana (10-20°): 5th house from sign (+4)
- 3rd drekkana (20-30°): 9th house from sign (+8)
- Degree: `(degrees_in_sign * 3) % 30`

### D4 (Chaturthamsa) - 4 divisions (7.5° each)
- Formula: `(floor(deg/7.5) + sign_index*4) % 12`
- Degree: `(degrees_in_sign * 4) % 30`

### D7 (Saptamsa) - 7 divisions (~4.2857° each)
- Odd signs: Forward mapping
- Even signs: Reverse mapping
- Formula: See `calculate_varga_sign()` in `varga_drik.py`
- Degree: `(degrees_in_sign * 7) % 30`

### D9 (Navamsa) - 9 divisions (3.3333° each)
- Formula: `(sign_index * 9 + division) % 12`
- Degree: `(degrees_in_sign * 9) % 30`

### D10 (Dasamsa) - 10 divisions (3° each)
- Odd signs: Forward mapping
- Even signs: Reverse mapping
- Formula: See `calculate_varga_sign()` in `varga_drik.py`
- Includes TEMPORARY corrections to match Prokerala/JHora exactly
- Degree: `(degrees_in_sign * 10) % 30`

### D12 (Dwadasamsa) - 12 divisions (2.5° each)
- Always forward mapping (no odd/even reversal)
- Formula: `((sign_index + division) % 12)`
- Degree: `(degrees_in_sign * 12) % 30`
- **Special Note:** Ascendant uses base formula, planets use standard formula

## Testing

Golden Prokerala tests are located in:
- `tests/test_varga_prokerala_suite.py` - Comprehensive test suite
- `test_d10_prokerala.py` - D10 specific test

Test data:
- DOB: 1995-05-16 18:38 IST
- Place: Bangalore (12.9716°N, 77.5946°E)

## DO NOT MODIFY

All critical logic is marked with:
```python
# 🔒 DO NOT MODIFY — JHora compatible
# DO NOT MODIFY — Prokerala/JHora compatible
```

These comments indicate code that must match Prokerala/JHora exactly and should not be changed without thorough verification.

