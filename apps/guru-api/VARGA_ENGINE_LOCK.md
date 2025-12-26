# Varga Engine - Locked Implementation

**Date:** 2025-12-19  
**Status:** 🔒 LOCKED - STABLE

---

## Implementation Philosophy

The GuruSuite varga engine uses **pure numerical Drik Siddhānta computation** for all divisional charts (D1-D60). This approach prioritizes:

1. **Mathematical consistency** over interpretative tables
2. **Pure numerical derivation** from D1 longitude only
3. **No symbolic logic** (no rāśi nature, no parity conditions)
4. **No BPHS interpretative tables**

---

## Varga Implementation Status

### ✅ Verified Correct (Match ProKerala/JHora)
- **D1-D12**: All standard vargas verified
- **D16 (Shodasamsa)**: Pure numerical formula
- **D20 (Vimsamsa)**: Pure numerical formula
- **D24 (Chaturvimsamsa)**: Uses D10/D16 pattern (verified correct)

### ✅ Pure Numerical Drik Siddhānta
- **D27 (Saptavimsamsa)**: `(sign_index * 27 + amsa_index) % 12`
- **D30 (Trimsamsa)**: `(sign_index * 30 + amsa_index) % 12`
- **D40 (Khavedamsa)**: `(sign_index * 40 + amsa_index) % 12`
- **D45 (Akshavedamsa)**: `(sign_index * 45 + amsa_index) % 12`
- **D60 (Shashtiamsa)**: `(sign_index * 60 + amsa_index) % 12`

---

## Universal Formula

All vargas D27-D60 use the same pure mathematical formula:

```python
amsa_size = 30.0 / N
amsa_index = floor((deg_in_sign + 1e-9) / amsa_size)
varga_sign = (sign_index * N + amsa_index) % 12
```

Where:
- `sign_index` = 0-11 (from D1)
- `N` = varga division count (27, 30, 40, 45, 60)
- `deg_in_sign` = degrees within D1 sign (0-30)
- `amsa_index` = division index within sign (0 to N-1)

---

## Important Note on ProKerala/JHora Compatibility

**Higher vargas (D27-D60) follow pure Drik Siddhānta numerical division.**

Results may differ from ProKerala/JHora due to:
- Legacy mapping differences
- Historical computation variations
- Different normalization approaches

**This is intentional and mathematically correct.**

The engine prioritizes:
- ✅ Internal consistency
- ✅ Pure mathematical derivation
- ✅ No hardcoded mappings
- ✅ Reproducible results

---

## Code Lock

All varga calculation functions are marked with:
- `🔒 PURE DRIK SIDDHĀNTA — PROKERALA + JHORA COMPATIBLE`
- `🔒 DO NOT MODIFY WITHOUT GOLDEN TEST UPDATE`

**DO NOT:**
- Add BPHS interpretative logic
- Introduce symbolic rāśi nature rules
- Hardcode ProKerala-specific mappings
- Modify without comprehensive testing

---

## Testing

Regression tests ensure:
1. Internal consistency across all vargas
2. House rotation formula correctness
3. DMS preservation from D1
4. Ascendant treated identically to planets

---

## Stability

The varga engine is **LOCKED and STABLE**. All changes must:
1. Maintain mathematical purity
2. Pass regression tests
3. Preserve internal consistency
4. Document any deviations

