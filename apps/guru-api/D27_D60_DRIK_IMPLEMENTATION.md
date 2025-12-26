# D27-D60 Drik Siddhānta Implementation

**Date:** 2025-12-19  
**Status:** ⚠️ IMPLEMENTED - AWAITING PROKERALA VERIFICATION

---

## Implementation Summary

Each varga now uses its own specific Drik Siddhānta logic, not universal formulas.

---

## D27 (Saptavimsamsa/Bhamsa) ✅ IMPLEMENTED

**Formula:** Nakshatra-pada aligned progression
```python
amsa_size = 30.0 / 27.0  # ~1.111°
amsa_index = floor((deg_in_sign + 1e-9) / amsa_size)
varga_sign = (sign_index * 27 + amsa_index) % 12
```

**Logic:** Each division corresponds to a nakshatra pada. Standard Drik Siddhānta formula.

**Test Results (1995-05-16 18:38 IST, Bangalore):**
- Ascendant: Pisces (index: 11)
- Sun: Leo (index: 4)
- Moon: Scorpio (index: 7)

---

## D30 (Trimsamsa) ✅ IMPLEMENTED

**Formula:** Odd/even directional logic (classical Drik Siddhānta)
```python
amsa_size = 30.0 / 30.0  # 1.0°
amsa_index = floor((deg_in_sign + 1e-9) / amsa_size)

if sign_index % 2 == 0:  # Odd sign (0-indexed)
    varga_sign = (sign_index + amsa_index) % 12  # FORWARD
else:  # Even sign
    varga_sign = (sign_index - amsa_index + 12) % 12  # REVERSE
```

**Logic:** 
- Odd signs (0, 2, 4, 6, 8, 10): Forward progression
- Even signs (1, 3, 5, 7, 9, 11): Reverse progression

**Test Results (1995-05-16 18:38 IST, Bangalore):**
- Ascendant: Virgo (index: 5)
- Sun: Aries (index: 0)
- Moon: Libra (index: 6)

---

## D40 (Khavedamsa/Chatvarimsamsa) ✅ IMPLEMENTED

**Formula:** D10/D16/D24 pattern (movable/fixed/dual + parity)
```python
amsa_size = 30.0 / 40.0  # 0.75°
amsa_index = floor((deg_in_sign + 1e-9) / amsa_size)

# Sign nature + parity logic (same as D10/D16/D24)
if sign_index in (0, 3, 6, 9):  # Movable
    start_offset = 0 if is_odd else 8
elif sign_index in (1, 4, 7, 10):  # Fixed
    start_offset = 0 if is_odd else 8
else:  # Dual
    start_offset = 4 if is_odd else 8

varga_sign = (sign_index + start_offset + amsa_index) % 12
```

**Test Results (1995-05-16 18:38 IST, Bangalore):**
- Ascendant: Libra (index: 6)
- Sun: Aquarius (index: 10)
- Moon: Aries (index: 0)

---

## D45 (Akshavedamsa) ✅ IMPLEMENTED

**Formula:** D10/D16/D24/D40 pattern (movable/fixed/dual + parity)
```python
amsa_size = 30.0 / 45.0  # ~0.6667°
amsa_index = floor((deg_in_sign + 1e-9) / amsa_size)

# Sign nature + parity logic (same as D10/D16/D24/D40)
# (Same offset calculation as D40)

varga_sign = (sign_index + start_offset + amsa_index) % 12
```

**Test Results (1995-05-16 18:38 IST, Bangalore):**
- Ascendant: Libra (index: 6)
- Sun: Pisces (index: 11)
- Moon: Leo (index: 4)

---

## D60 (Shashtiamsa) ✅ IMPLEMENTED

**Formula:** D10/D16/D24/D40/D45 pattern (movable/fixed/dual + parity)
```python
amsa_size = 30.0 / 60.0  # 0.5°
amsa_index = floor((deg_in_sign + 1e-9) / amsa_size)

# Sign nature + parity logic (same as D10/D16/D24/D40/D45)
# (Same offset calculation as D40/D45)

varga_sign = (sign_index + start_offset + amsa_index) % 12
```

**Test Results (1995-05-16 18:38 IST, Bangalore):**
- Ascendant: Scorpio (index: 7)
- Sun: Pisces (index: 11)
- Moon: Virgo (index: 5)

---

## Varga Pattern Summary

| Varga | Pattern | Formula Type |
|-------|---------|--------------|
| D24 | D10/D16 pattern | movable/fixed/dual + parity |
| D27 | Nakshatra-pada | (sign * 27 + amsa) % 12 |
| D30 | Odd/even directional | forward/reverse based on parity |
| D40 | D10/D16/D24 pattern | movable/fixed/dual + parity |
| D45 | D10/D16/D24/D40 pattern | movable/fixed/dual + parity |
| D60 | D10/D16/D24/D40/D45 pattern | movable/fixed/dual + parity |

---

## Next Steps

1. ⏳ **Visual Verification:** Compare results with ProKerala/JHora
2. ⏳ **Adjust if needed:** Fine-tune formulas based on verification
3. ⏳ **Lock formulas:** Finalize after exact match confirmed

**DO NOT mark complete until visual parity is achieved.**

