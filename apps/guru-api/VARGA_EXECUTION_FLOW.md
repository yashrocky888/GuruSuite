# Varga Execution Flow - Single Source of Truth

## 🎯 ARCHITECTURAL PRINCIPLE

**API routes MUST NEVER compute varga directly.**
All varga calculations MUST go through `varga_engine.py` - the single authoritative source.

## 📋 WHY THIS EXISTS

### Problem (PROVEN):
- API routes were directly calling `calculate_varga()`
- `varga_houses.py` was recomputing varga independently
- Multiple layers re-derived sign/house independently
- This broke Prokerala/JHora consistency

### Solution:
- **ONE authoritative engine**: `varga_engine.py`
- **Runtime guard**: Prevents direct `calculate_varga()` calls from API routes
- **Atomic computation**: Sign and house computed together
- **Consistency guaranteed**: Same input → same output, always

## 🔄 EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                    API ROUTE LAYER                           │
│  (apps/guru-api/src/api/kundli_routes.py)                   │
│                                                               │
│  ❌ FORBIDDEN: calculate_varga()                             │
│  ❌ FORBIDDEN: calculate_varga_houses()                       │
│  ✅ REQUIRED: build_varga_chart() from varga_engine.py       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Calls
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              AUTHORITATIVE ENGINE LAYER                      │
│  (apps/guru-api/src/jyotish/varga_engine.py)                 │
│                                                               │
│  ✅ build_varga_chart(d1_planets, d1_ascendant, varga_type) │
│     - Computes sign AND house together atomically            │
│     - Uses Whole Sign system (house = sign)                  │
│     - Returns structured output                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Uses (internal only)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  INTERNAL COMPUTATION LAYER                  │
│  (apps/guru-api/src/jyotish/varga_drik.py)                   │
│                                                               │
│  ✅ calculate_varga() - INTERNAL ONLY                        │
│     - Runtime guard prevents API route calls                │
│     - Contains VERIFIED D10 logic with Prokerala corrections │
│     - Used ONLY by varga_engine.py                           │
└─────────────────────────────────────────────────────────────┘
```

## 📝 API ROUTE USAGE

### ✅ CORRECT (Required):

```python
from src.jyotish.varga_engine import build_varga_chart

# Prepare D1 data
d1_ascendant = base_kundli["Ascendant"]["degree"]
d1_planets = {
    planet_name: planet_info["degree"]
    for planet_name, planet_info in base_kundli["Planets"].items()
}

# Build varga chart using authoritative engine
d10_chart = build_varga_chart(d1_planets, d1_ascendant, 10)

# Use result
ascendant_sign = d10_chart["ascendant"]["sign"]
venus_house = d10_chart["planets"]["Venus"]["house"]
```

### ❌ FORBIDDEN (Will raise RuntimeError):

```python
from src.jyotish.varga_drik import calculate_varga  # ❌ DO NOT IMPORT

# This will raise RuntimeError in API routes
varga_data = calculate_varga(d1_ascendant, 10)  # ❌ BLOCKED
```

## 🛡️ RUNTIME GUARD

The `calculate_varga()` function in `varga_drik.py` includes a runtime guard that:

- ✅ **Allows** calls from `varga_engine.py`
- ✅ **Allows** calls from `varga_houses.py` (legacy internal helper)
- ✅ **Allows** calls from test files
- ❌ **BLOCKS** calls from API route files (`api/` or `routes.py`)
- ⚠️ **Warns** on other calls (deprecation path)

If an API route tries to call `calculate_varga()` directly:
```
RuntimeError: ARCHITECTURAL VIOLATION: calculate_varga() called directly from ...
API routes MUST use build_varga_chart() from varga_engine.py instead.
```

## ✅ CONSISTENCY GUARANTEES

### Same Input → Same Output

For the same D1 input, these endpoints MUST return IDENTICAL D10:
- `GET /api/v1/kundli` → D10
- `POST /api/v1/kundli/dasamsa` → D10
- Direct `build_varga_chart()` call → D10

### Whole Sign System

For ALL varga charts:
- **House = Sign** (1-based house = 0-based sign_index + 1)
- No house cusp calculations for varga
- No rotation or remapping

### Prokerala/JHora Matching

D10 calculation uses VERIFIED logic:
- Longitude slicing (not sign-based shortcuts)
- Parashara mapping with specific corrections
- Matches Prokerala/JHora exactly for test case:
  - DOB: 1995-05-16 18:38 Bangalore
  - Ascendant: Cancer (House 4)
  - Venus: Aquarius (House 11)
  - Mars: Pisces (House 12)

## 🧪 TESTING

Run consistency tests:
```bash
cd apps/guru-api
pytest tests/test_varga_consistency.py -v
```

Tests verify:
1. D10 matches Prokerala exactly
2. Same input produces identical results across endpoints
3. House = sign for all varga charts
4. Runtime guard prevents API route violations

## 📚 FILES

### Authoritative Engine:
- `src/jyotish/varga_engine.py` - **USE THIS** from API routes

### Internal Helpers (DO NOT USE from API routes):
- `src/jyotish/varga_drik.py` - Core varga computation (internal)
- `src/jyotish/varga_houses.py` - Legacy house helper (internal)

### API Routes:
- `src/api/kundli_routes.py` - Main kundli endpoint (uses engine)
- `src/api/kundli_routes.py` - Navamsa/Dasamsa endpoints (use engine)

## 🔒 ENFORCEMENT

1. **Runtime Guard**: Blocks direct `calculate_varga()` calls from API routes
2. **Code Review**: Check imports - no `varga_drik` imports in `api/` files
3. **Tests**: `test_varga_consistency.py` verifies consistency
4. **Documentation**: This file explains the architecture

## 🎯 BENEFITS

1. **Consistency**: Same input always produces same output
2. **Maintainability**: One place to fix varga logic
3. **Prokerala Match**: Verified D10 logic preserved
4. **Architecture**: Clear separation of concerns
5. **Testing**: Easy to verify correctness

---

**Last Updated**: 2025-12-14  
**Maintained By**: Architecture Team  
**Status**: Enforced via runtime guard

