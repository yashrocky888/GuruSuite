# D24-D60 Drik Siddhānta Mapping (ProKerala/JHora Match)

## Status: ⚠️ IN PROGRESS

**Objective:** Match ProKerala/JHora EXACTLY for D24-D60

**Test Chart:** 1995-05-16 18:38 IST, Bangalore

---

## D24 (Chaturvimsamsa) ✅ FIXED

**Formula:** Uses D10/D16 pattern (movable/fixed/dual + parity)

**Verification:**
- D1 Ascendant: Scorpio (7), deg_in_sign=2.279858, amsa_index=1
- D24 Ascendant: Leo (4) ✅ (matches ProKerala)

**Implementation:**
```python
# Sign nature + parity logic (same as D10/D16)
if sign_index in (0, 3, 6, 9):  # Movable
    start_offset = 0 if is_odd else 8
elif sign_index in (1, 4, 7, 10):  # Fixed
    start_offset = 0 if is_odd else 8
else:  # Dual
    start_offset = 4 if is_odd else 8

varga_sign = (sign_index + start_offset + amsa_index) % 12
```

---

## D27, D30, D40, D45, D60 ⚠️ NEED PROKERALA REFERENCE DATA

**Required for reverse-engineering:**
- D27 Ascendant, Sun, Moon signs
- D30 Ascendant, Sun, Moon signs
- D40 Ascendant, Sun, Moon signs
- D45 Ascendant, Sun, Moon signs
- D60 Ascendant, Sun, Moon signs

**Current Status:**
- Using universal formula (INCORRECT)
- Need ProKerala outputs to reverse-engineer correct Drik mappings

---

## Next Steps

1. ✅ D24: Fixed using D10/D16 pattern
2. ⏳ D27-D60: Need ProKerala reference data to reverse-engineer
3. ⏳ Verify all vargas match ProKerala exactly
4. ⏳ Lock formulas after verification

