# Astro Core Engine

## CRITICAL ARCHITECTURAL RULES

### RULE 1: Calculation Pipeline (MANDATORY)

For EVERY planet and ascendant:

1. **UTC Birth Time**: Convert local time to UTC
2. **Timezone Offset**: Apply timezone offset correctly
3. **Julian Day**: Compute using UTC time
4. **Swiss Ephemeris**: Get tropical longitude with `swe.calc_ut()`
5. **Ayanamsa**: Get Lahiri ayanamsa with `swe.get_ayanamsa()`
6. **Sidereal Longitude**: `sidereal = (tropical - ayanamsa) % 360`

**NO SHORTCUTS. NO APPROXIMATIONS.**

### RULE 2: Divisional Charts (VARGA)

**ABSOLUTELY FORBIDDEN:**
- Sign-based shortcuts
- Reusing D1 houses
- UI-based remapping

**CORRECT METHOD:**

For each planet in varga chart:
1. Take D1 sidereal longitude (0-360)
2. Extract degrees in sign: `deg_in_sign = longitude % 30`
3. Divide sign into N equal parts (e.g., D10 = 3° per part)
4. Identify division index: `div_index = floor(deg_in_sign / part_size)`
5. Apply Parashara mapping rules (odd/even sign logic)
6. Calculate final varga sign
7. Calculate final varga longitude
8. **House = Sign** (Whole Sign system)

### RULE 3: Ascendant Per Varga

**CRITICAL**: Ascendant MUST be recalculated separately for each varga chart.

**FORBIDDEN:**
- Reusing D1 ascendant
- Rotating by D1 ascendant
- Using D1 house cusps

**CORRECT:**
- Apply varga formula to D1 ascendant longitude
- Calculate varga ascendant sign
- Calculate varga ascendant longitude
- **House = Sign** for ascendant too

### RULE 4: Swiss Ephemeris Settings

```python
# Set sidereal mode
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Calculate planets (sidereal mode)
flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
lon, lat, dist = swe.calc_ut(jd_ut, planet, flags)

# Calculate ascendant (sidereal mode)
houses = swe.houses_ex(jd_ut, latitude, longitude, b'P', swe.FLG_SIDEREAL)
asc_sidereal = houses[0][0] % 360.0
```

### RULE 5: Validation

Every calculation MUST be validated against:
- JHora software
- Drik Panchang
- Prokerala divisional charts

If mismatch → logic is WRONG.

## Module Structure

- `planets.py`: Planetary position calculations
- `houses.py`: House cusp calculations (D1 only)
- `varga.py`: Divisional chart calculations
- `ascendant.py`: Ascendant calculations

