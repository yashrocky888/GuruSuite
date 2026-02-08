# ASCENDANT (LAGNA) LONGITUDE END-TO-END TRACE

This document traces the complete data flow of Ascendant (Lagna) sidereal longitude from Swiss Ephemeris calculation through to varga chart computation.

---

## 1️⃣ ORIGINAL ASCENDANT CALCULATION (SWISS EPHEMERIS)

### File: `apps/guru-api/src/ephemeris/planets_jhora_exact.py`
### Function: `calculate_ascendant_jhora_exact()`
### Lines: 101-164

**Exact Code:**
```python
def calculate_ascendant_jhora_exact(julian_day: float, latitude: float, longitude: float) -> Dict:
    """
    Calculate Ascendant using EXACT JHORA / DRIK PANCHANG methodology.
    
    Formula (DO NOT MODIFY):
    1. houses = swe.houses_ex(jd_ut, lat, lon, b'P', swe.FLG_SIDEREAL)
    2. FLG_SIDEREAL returns sidereal ascendant directly - DO NOT subtract ayanamsa
    3. asc_sidereal = houses[0][0] % 360.0
    4. Convert to DMS exactly as specified
    """
    init_jhora_exact()
    
    # Step 1: Calculate houses using houses_ex() with FLG_SIDEREAL
    result = swe.houses_ex(julian_day, latitude, longitude, b'P', swe.FLG_SIDEREAL)
    if result is None:
        raise ValueError("Error calculating houses")
    
    cusps, ascmc = result
    sidereal_asc = float(ascmc[0])  # Ascendant (already sidereal due to FLG_SIDEREAL)
    
    # Step 2: Normalize sidereal ascendant
    sidereal_asc = sidereal_asc % 360.0
    if sidereal_asc < 0:
        sidereal_asc += 360.0
    
    # ... DMS conversion code ...
    
    return {
        "longitude": sidereal_asc,  # Full sidereal longitude, double precision
        "sign_index": sign_index,
        "degrees_in_sign": deg_in_sign,
        # ... other fields ...
    }
```

**Key Variable:**
- **`sidereal_asc`** (line 129): Raw sidereal longitude from Swiss Ephemeris `swe.houses_ex()` with `FLG_SIDEREAL` flag
- **`"longitude"`** (line 153): Returned in dictionary as the raw sidereal longitude (0-360°)

**Swiss Ephemeris Call:**
- **Function**: `swe.houses_ex(julian_day, latitude, longitude, b'P', swe.FLG_SIDEREAL)`
- **Flag**: `FLG_SIDEREAL` - Returns sidereal positions directly (no manual ayanamsa subtraction)
- **House System**: `b'P'` = Placidus
- **Return Value**: `ascmc[0]` = Ascendant longitude (already sidereal)

---

## 2️⃣ COMPLETE DATA FLOW

### Step 1: API Route Receives Request
**File**: `apps/guru-api/src/api/kundli_routes.py`  
**Function**: `kundli_get()`  
**Lines**: 339-851

**Code (lines 497-501):**
```python
# Get RAW ascendant longitude (unrounded, exact sidereal)
from src.ephemeris.planets_jhora_exact import calculate_ascendant_jhora_exact, calculate_all_planets_jhora_exact

asc_jhora_raw = calculate_ascendant_jhora_exact(jd, lat, lon)
d1_ascendant = asc_jhora_raw["longitude"]  # Raw unrounded sidereal longitude
```

**Variable Flow:**
- `asc_jhora_raw` = Dictionary returned from `calculate_ascendant_jhora_exact()`
- `d1_ascendant` = `asc_jhora_raw["longitude"]` = Raw sidereal longitude (0-360°)

**Comment in Code (line 495):**
```python
# 🔒 CRITICAL: Use RAW unrounded sidereal longitudes for varga calculations
# DO NOT use rounded degrees from D1 output - rounding causes varga mismatches
# Extract raw longitudes directly from ephemeris calculations
```

---

### Step 2: Varga Chart Builder Receives Ascendant
**File**: `apps/guru-api/src/jyotish/varga_engine.py`  
**Function**: `build_varga_chart()`  
**Lines**: 46-336

**Function Signature (lines 46-51):**
```python
def build_varga_chart(
    d1_planets: Dict[str, float],
    d1_ascendant: float,  # <-- Ascendant longitude passed here
    varga_type: int,
    chart_method: Optional[int] = None
) -> Dict:
```

**Call Site (kundli_routes.py, line 521):**
```python
d4_chart = build_varga_chart(d1_planets, d1_ascendant, 4)
```

**Variable**: `d1_ascendant` = Raw sidereal longitude (0-360°) passed directly from API route

---

### Step 3: Internal Varga Calculation
**File**: `apps/guru-api/src/jyotish/varga_engine.py`  
**Function**: `build_varga_chart()` → `_calculate_varga_internal()`  
**Lines**: 88-91

**Code:**
```python
# Calculate varga ascendant
# NOTE: D24 is locked to method 1, chart_method parameter is ignored for D24
varga_asc_data = _calculate_varga_internal(d1_ascendant, varga_type, chart_method=chart_method if varga_type != 24 else None)
```

**Import (line 26):**
```python
from src.jyotish.varga_drik import calculate_varga as _calculate_varga_internal
```

**Variable**: `d1_ascendant` = Raw sidereal longitude (0-360°) passed to `_calculate_varga_internal()`

---

### Step 4: Varga Calculation Function
**File**: `apps/guru-api/src/jyotish/varga_drik.py`  
**Function**: `calculate_varga()`  
**Lines**: 622-1126

**Function Signature (lines 622-643):**
```python
def calculate_varga(planet_longitude: float, varga_type: int, chart_method: Optional[int] = None) -> Dict:
    """
    Unified function to calculate ANY varga (divisional chart) using EXACT Parashari formulas.
    
    Args:
        planet_longitude: Sidereal longitude (0-360)  # <-- Ascendant longitude received here
        varga_type: Varga number (2, 3, 4, 7, 9, 10, 12, etc.)
    
    Returns:
        Dict with:
            - longitude: Final longitude in varga chart
            - sign: Sign index (0-11)
            - sign_name: Sign name
            - degrees_in_sign: Degrees within the varga sign (PRESERVED from D1)
            - division: Division number (1-based)
    """
    longitude = normalize_degrees(planet_longitude)  # <-- Normalization happens here
    sign_num = int(longitude / 30)
    degrees_in_sign = longitude % 30
```

**For D4 (lines 738-785):**
```python
elif varga_type == 4:
    # ... D4 calculation logic ...
    div_size = 7.5  # 30° / 4 = 7.5° per part
    part_index = int(math.floor(degrees_in_sign / div_size))
    
    # Determine starting sign based on sign modality
    if sign_num in (0, 3, 6, 9):  # Movable
        starting_sign_index = sign_num
    elif sign_num in (1, 4, 7, 10):  # Fixed
        starting_sign_index = (sign_num + 4) % 12
    else:  # Dual
        starting_sign_index = (sign_num + 7) % 12
    
    chaturthamsa_sign = (starting_sign_index + part_index) % 12
    chaturthamsa_longitude = chaturthamsa_sign * 30 + degrees_in_sign  # <-- RECONSTRUCTION HERE
    
    return {
        "longitude": normalize_degrees(chaturthamsa_longitude),
        "sign": chaturthamsa_sign,
        "sign_name": get_sign_name(chaturthamsa_sign),
        "degrees_in_sign": degrees_in_sign,  # Preserve D1 DMS
        "division": part_index + 1
    }
```

**Key Variables:**
- **`planet_longitude`** = Raw sidereal longitude (0-360°) from `d1_ascendant`
- **`longitude`** = Normalized version (line 644)
- **`sign_num`** = Sign index (0-11) calculated from longitude
- **`degrees_in_sign`** = Degrees within sign (0-30°)
- **`chaturthamsa_longitude`** = **RECONSTRUCTED** as `chaturthamsa_sign * 30 + degrees_in_sign` (line 777)

---

## 3️⃣ RECONSTRUCTION CHECK

### ✅ YES - Ascendant Longitude IS Reconstructed

**Location**: `apps/guru-api/src/jyotish/varga_drik.py`, line 777

**Code:**
```python
chaturthamsa_longitude = chaturthamsa_sign * 30 + degrees_in_sign
```

**This happens for ALL varga types:**
- **D2 (Hora)**: Line 688: `hora_longitude = hora_sign * 30 + degrees_in_sign`
- **D3 (Drekkana)**: Line 728: `drekkana_longitude = drekkana_sign * 30 + degrees_in_sign`
- **D4 (Chaturthamsa)**: Line 777: `chaturthamsa_longitude = chaturthamsa_sign * 30 + degrees_in_sign`
- **D7 (Saptamsa)**: Line 793: `saptamsa_longitude = varga_sign_index * 30 + degrees_in_sign`
- **D9 (Navamsa)**: Line 819: `navamsa_longitude = navamsa_sign * 30 + degrees_in_sign`
- **D10 (Dasamsa)**: Line 835: `dasamsa_longitude = varga_sign_index * 30 + degrees_in_sign`
- **D12 (Dwadasamsa)**: Line 875: `dwadasamsa_longitude = varga_sign_index * 30 + degrees_in_sign`
- **D20 (Vimsamsa)**: Line 896: `vimshamsa_longitude = varga_sign_index * 30 + degrees_in_sign`

**Pattern**: `varga_longitude = varga_sign_index * 30 + degrees_in_sign`

**Where `degrees_in_sign` comes from:**
- Line 646: `degrees_in_sign = longitude % 30`
- This is the **ORIGINAL** D1 degrees_in_sign, preserved from the input `planet_longitude`

**Normalization:**
- Line 644: `longitude = normalize_degrees(planet_longitude)` - Normalizes input to 0-360°
- Final return: `"longitude": normalize_degrees(varga_longitude)` - Normalizes reconstructed longitude

---

## 4️⃣ WHERE calculate_varga() IS CALLED FOR ASCENDANT

### Call Site 1: Varga Engine (Primary Path)
**File**: `apps/guru-api/src/jyotish/varga_engine.py`  
**Function**: `build_varga_chart()`  
**Line**: 91

**Code:**
```python
varga_asc_data = _calculate_varga_internal(d1_ascendant, varga_type, chart_method=chart_method if varga_type != 24 else None)
```

**Where `_calculate_varga_internal` is defined:**
- Line 26: `from src.jyotish.varga_drik import calculate_varga as _calculate_varga_internal`
- This is an alias for `calculate_varga()` in `varga_drik.py`

**Value Passed:**
- **`d1_ascendant`** = Raw sidereal longitude (0-360°) from `asc_jhora_raw["longitude"]`

---

### Call Site 2: API Route (Direct Call for D12 Special Case)
**File**: `apps/guru-api/src/api/kundli_routes.py`  
**Function**: `kundli_get()`  
**Lines**: 556-578

**Code:**
```python
# D12 ascendant uses BASE formula (no +3 correction) - recalculate
d1_asc_sign = int(d1_ascendant / 30)
d1_asc_deg_in_sign = d1_ascendant % 30
part = 2.5
div_index = int(math.floor(d1_asc_deg_in_sign / part))
if div_index >= 12:
    div_index = 11
d12_asc_sign = (d1_asc_sign + div_index) % 12
d12_asc_deg_in_sign = (d1_asc_deg_in_sign * 12) % 30
d12_asc_longitude = d12_asc_sign * 30 + d12_asc_deg_in_sign  # <-- RECONSTRUCTION
d12_asc_longitude = normalize_degrees(d12_asc_longitude)

# Update D12 ascendant with base formula result
d12_chart["ascendant"] = {
    "degree": round(d12_asc_longitude, 4),
    "sign": get_sign_name(d12_asc_sign),
    "sign_index": d12_asc_sign,
    "degrees_in_sign": round(d12_asc_deg_in_sign, 4),
    "house": 1
}
```

**Note**: D12 has special handling where the ascendant is recalculated using base formula (no +3 correction), but this still uses the **original** `d1_ascendant` value.

---

## 5️⃣ COMPARISON WITH MOON PLANET

### Moon Calculation Flow

**Step 1: Original Calculation**
**File**: `apps/guru-api/src/ephemeris/planets_jhora_exact.py`  
**Function**: `calculate_planet_jhora_exact()`  
**Lines**: 23-98

**Code:**
```python
def calculate_planet_jhora_exact(julian_day: float, planet_id: int) -> Dict:
    init_jhora_exact()
    
    # Step 1: Calculate sidereal longitude using calc_ut() with FLG_SIDEREAL
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    xx, ret = swe.calc_ut(julian_day, planet_id, flags)
    
    # Extract sidereal longitude (already sidereal due to FLG_SIDEREAL flag)
    sidereal_lon = float(xx[0])
    
    # Step 2: Normalize sidereal longitude
    sidereal_lon = sidereal_lon % 360.0
    if sidereal_lon < 0:
        sidereal_lon += 360.0
    
    return {
        "longitude": sidereal_lon,  # Full sidereal longitude (0-360), double precision
        # ... other fields ...
    }
```

**Swiss Ephemeris Call:**
- **Function**: `swe.calc_ut(julian_day, planet_id, flags)`
- **Flag**: `FLG_SIDEREAL` - Returns sidereal positions directly
- **Planet ID**: `swe.MOON` (for Moon)
- **Return Value**: `xx[0]` = Sidereal longitude (0-360°)

---

**Step 2: API Route Extraction**
**File**: `apps/guru-api/src/api/kundli_routes.py`  
**Function**: `kundli_get()`  
**Lines**: 503-508

**Code:**
```python
# Get RAW planet longitudes (unrounded, exact sidereal)
planets_jhora_raw = calculate_all_planets_jhora_exact(jd)
d1_planets = {
    planet_name: planet_data["longitude"]  # Raw unrounded sidereal longitude
    for planet_name, planet_data in planets_jhora_raw.items()
}
```

**For Moon:**
- `planets_jhora_raw["Moon"]["longitude"]` = Raw sidereal longitude from Swiss Ephemeris
- `d1_planets["Moon"]` = Same raw sidereal longitude

---

**Step 3: Varga Calculation for Moon**
**File**: `apps/guru-api/src/jyotish/varga_engine.py`  
**Function**: `build_varga_chart()`  
**Lines**: 174-176

**Code:**
```python
for planet_name, d1_longitude in d1_planets.items():
    # NOTE: D24 is locked to method 1, chart_method parameter is ignored for D24
    varga_data = _calculate_varga_internal(d1_longitude, varga_type, chart_method=chart_method if varga_type != 24 else None)
```

**For Moon:**
- `d1_longitude` = `d1_planets["Moon"]` = Raw sidereal longitude from Swiss Ephemeris
- This is passed to `_calculate_varga_internal()` (which is `calculate_varga()`)

---

**Step 4: Varga Calculation Function (Same as Ascendant)**
**File**: `apps/guru-api/src/jyotish/varga_drik.py`  
**Function**: `calculate_varga()`  
**Lines**: 622-1126

**Code (same as Ascendant):**
```python
def calculate_varga(planet_longitude: float, varga_type: int, chart_method: Optional[int] = None) -> Dict:
    longitude = normalize_degrees(planet_longitude)  # Normalize input
    sign_num = int(longitude / 30)
    degrees_in_sign = longitude % 30
    
    # ... varga-specific calculation ...
    
    # For D4:
    chaturthamsa_longitude = chaturthamsa_sign * 30 + degrees_in_sign  # RECONSTRUCTION
    
    return {
        "longitude": normalize_degrees(chaturthamsa_longitude),
        "sign": chaturthamsa_sign,
        "sign_name": get_sign_name(chaturthamsa_sign),
        "degrees_in_sign": degrees_in_sign,  # Preserve D1 DMS
        "division": part_index + 1
    }
```

---

### ✅ CONFIRMATION: Moon Uses ORIGINAL Swiss Ephemeris Longitude

**Evidence:**
1. Moon is calculated using `swe.calc_ut()` with `FLG_SIDEREAL` (same as Ascendant uses `swe.houses_ex()` with `FLG_SIDEREAL`)
2. Moon longitude is extracted as `planets_jhora_raw["Moon"]["longitude"]` = Raw sidereal longitude
3. Moon is passed to `calculate_varga()` as `d1_planets["Moon"]` = Original Swiss Ephemeris longitude
4. Moon undergoes **SAME reconstruction** as Ascendant: `varga_longitude = varga_sign_index * 30 + degrees_in_sign`

**Key Difference:**
- **Ascendant**: Uses `swe.houses_ex()` to get ascendant from house cusps
- **Moon**: Uses `swe.calc_ut()` to get planet position directly
- **Both**: Use `FLG_SIDEREAL` flag to get sidereal positions directly
- **Both**: Pass original longitude to `calculate_varga()`
- **Both**: Undergo reconstruction in varga calculation: `varga_sign_index * 30 + degrees_in_sign`

---

## 6️⃣ SUMMARY

### Ascendant Longitude Flow:

1. **Swiss Ephemeris** (`swe.houses_ex()` with `FLG_SIDEREAL`)
   - Returns: `ascmc[0]` = Raw sidereal ascendant (0-360°)
   - File: `planets_jhora_exact.py`, line 129
   - Variable: `sidereal_asc`

2. **Ephemeris Function Return**
   - Returns: `{"longitude": sidereal_asc, ...}`
   - File: `planets_jhora_exact.py`, line 153
   - Variable: `asc_jhora_raw["longitude"]`

3. **API Route Extraction**
   - Extracts: `d1_ascendant = asc_jhora_raw["longitude"]`
   - File: `kundli_routes.py`, line 501
   - Variable: `d1_ascendant` = Raw sidereal longitude (0-360°)

4. **Varga Chart Builder**
   - Receives: `d1_ascendant` as parameter
   - File: `varga_engine.py`, line 48
   - Passes to: `_calculate_varga_internal(d1_ascendant, varga_type)`

5. **Varga Calculation**
   - Receives: `planet_longitude = d1_ascendant` (raw sidereal longitude)
   - File: `varga_drik.py`, line 622
   - Normalizes: `longitude = normalize_degrees(planet_longitude)` (line 644)
   - Extracts: `sign_num = int(longitude / 30)`, `degrees_in_sign = longitude % 30` (lines 645-646)
   - Calculates: D4 sign using modality-based rules (lines 738-773)
   - **RECONSTRUCTS**: `chaturthamsa_longitude = chaturthamsa_sign * 30 + degrees_in_sign` (line 777)
   - Returns: `{"longitude": normalize_degrees(chaturthamsa_longitude), ...}`

### Key Findings:

✅ **Ascendant uses ORIGINAL Swiss Ephemeris longitude** - No reconstruction before varga calculation  
✅ **Ascendant longitude IS reconstructed** in varga calculation: `varga_sign_index * 30 + degrees_in_sign`  
✅ **Moon uses SAME pattern** - Original Swiss Ephemeris longitude, reconstructed in varga  
✅ **No rounding** before varga calculation - Raw double precision values are used  
✅ **Normalization happens** in `calculate_varga()` - `normalize_degrees()` ensures 0-360° range  
✅ **DMS values preserved** - `degrees_in_sign` from D1 is preserved in varga charts  

---

## 7️⃣ CODE REFERENCES

### Swiss Ephemeris Calls:

**Ascendant:**
- File: `apps/guru-api/src/ephemeris/planets_jhora_exact.py`
- Line: 124
- Code: `result = swe.houses_ex(julian_day, latitude, longitude, b'P', swe.FLG_SIDEREAL)`
- Variable: `ascmc[0]` = Raw sidereal ascendant

**Moon:**
- File: `apps/guru-api/src/ephemeris/planets_jhora_exact.py`
- Line: 47
- Code: `xx, ret = swe.calc_ut(julian_day, planet_id, flags)`
- Variable: `xx[0]` = Raw sidereal longitude

### Varga Calculation Calls:

**Ascendant:**
- File: `apps/guru-api/src/jyotish/varga_engine.py`
- Line: 91
- Code: `varga_asc_data = _calculate_varga_internal(d1_ascendant, varga_type, ...)`
- Variable: `d1_ascendant` = Raw sidereal longitude from Swiss Ephemeris

**Moon:**
- File: `apps/guru-api/src/jyotish/varga_engine.py`
- Line: 176
- Code: `varga_data = _calculate_varga_internal(d1_longitude, varga_type, ...)`
- Variable: `d1_longitude` = `d1_planets["Moon"]` = Raw sidereal longitude from Swiss Ephemeris

### Reconstruction Points:

**All Varga Types:**
- File: `apps/guru-api/src/jyotish/varga_drik.py`
- Pattern: `varga_longitude = varga_sign_index * 30 + degrees_in_sign`
- Examples:
  - D4: Line 777
  - D9: Line 819
  - D10: Line 835
  - D12: Line 875

---

**END OF TRACE DOCUMENT**
