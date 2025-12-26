# BPHS Parāśara Rules for D16-D60 Varga Charts

## Reference Standard
- **Bṛhat Parāśara Horā Śāstra (BPHS)**
- Prokerala & JHora as behavior reference (not data source)

## Implementation Pattern (Following D10/D12)

All vargas follow the same structural logic:
1. **Degree segmentation within sign**: `div_index = floor(degrees_in_sign / part_size)`
2. **Start sign determination**: Based on sign classification (nature, parity, element)
3. **Progression mapping**: Forward or reverse based on rules
4. **DMS preservation**: Varga charts preserve EXACT D1 DMS values

---

## D16 (Shodasamsa) - 16 divisions (1.875° each)

**BPHS Rule:**
- 16 equal divisions per sign
- Uses sign nature (movable/fixed/dual) + parity (odd/even)
- **Same pattern as D10**

**Formula:**
```
part = 30.0 / 16.0  # 1.875°
div_index = floor(degrees_in_sign / part)

IF sign is MOVABLE:
    start_offset = 0 if sign is ODD else 8
ELIF sign is FIXED:
    start_offset = 0 if sign is ODD else 8
ELIF sign is DUAL:
    start_offset = 4 if sign is ODD else 8

varga_sign_index = (sign_index + start_offset + div_index) % 12
```

**Sign Classification:**
- Movable (Chara): Aries(0), Cancer(3), Libra(6), Capricorn(9)
- Fixed (Sthira): Taurus(1), Leo(4), Scorpio(7), Aquarius(10)
- Dual (Dvisvabhava): Gemini(2), Virgo(5), Sagittarius(8), Pisces(11)

**Parity (0-indexed):**
- Odd: 0, 2, 4, 6, 8, 10 (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius)
- Even: 1, 3, 5, 7, 9, 11 (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces)

---

## D20 (Vimsamsa) - 20 divisions (1.5° each)

**BPHS Rule:**
- 20 equal divisions per sign
- **Simple forward progression** (like D12)
- NO odd/even reversal

**Formula:**
```
part = 1.5
div_index = floor(degrees_in_sign / part)
rasi_sign = sign_index + 1  # Convert to 1-based

varga_sign_1based = ((rasi_sign - 1 + div_index) % 12) + 1
varga_sign_index = varga_sign_1based - 1  # Convert back to 0-based
```

**Direction:** Always forward, no reversal

---

## D24 (Chaturvimsamsa) - 24 divisions (1.25° each)

**BPHS Rule:**
- 24 equal divisions per sign
- **Element-based starting signs**

**Formula:**
```
part = 30.0 / 24.0  # 1.25°
div_index = floor(degrees_in_sign / part)

IF sign is FIRE (Aries, Leo, Sagittarius):
    start_sign = 0  # Aries
ELIF sign is EARTH (Taurus, Virgo, Capricorn):
    start_sign = 1  # Taurus
ELIF sign is AIR (Gemini, Libra, Aquarius):
    start_sign = 2  # Gemini
ELSE (WATER: Cancer, Scorpio, Pisces):
    start_sign = 3  # Cancer

varga_sign_index = (start_sign + div_index) % 12
```

---

## D27 (Saptavimsamsa/Bhamsa) - 27 divisions (~1.111° each)

**BPHS Rule:**
- 27 equal divisions per sign (aligned with 27 nakshatras)
- **Nakshatra-pada aligned progression**

**Formula:**
```
part = 30.0 / 27.0  # ~1.111°
div_index = floor(degrees_in_sign / part)

varga_sign_index = (sign_index * 27 + div_index) % 12
```

**Purpose:** Each division corresponds to a nakshatra pada

---

## D30 (Trimsamsa) - 30 divisions (1° each)

**BPHS Rule:**
- 30 equal divisions per sign (1° each)
- **Odd signs forward, Even signs reverse**

**Formula:**
```
part = 1.0
div_index = floor(degrees_in_sign / part)

IF sign_index % 2 == 0:  # Odd sign (0-indexed)
    varga_sign_index = (sign_index + div_index) % 12
ELSE:  # Even sign
    varga_sign_index = (sign_index - div_index) % 12
```

**Direction:**
- Odd signs (0, 2, 4, 6, 8, 10): Forward progression
- Even signs (1, 3, 5, 7, 9, 11): Reverse progression

---

## D40 (Chatvarimsamsa/Khavedamsa) - 40 divisions (0.75° each)

**BPHS Rule:**
- 40 equal divisions per sign
- Uses sign nature (movable/fixed/dual) + parity (odd/even)
- **Same pattern as D10/D16**

**Formula:**
```
part = 30.0 / 40.0  # 0.75°
div_index = floor(degrees_in_sign / part)

IF sign is MOVABLE:
    start_offset = 0 if sign is ODD else 8
ELIF sign is FIXED:
    start_offset = 0 if sign is ODD else 8
ELIF sign is DUAL:
    start_offset = 4 if sign is ODD else 8

varga_sign_index = (sign_index + start_offset + div_index) % 12
```

**Sign Classification:** Same as D10/D16

---

## D45 (Akshavedamsa) - 45 divisions (~0.667° each)

**BPHS Rule:**
- 45 equal divisions per sign
- **Element-based starting signs** (same as D24)

**Formula:**
```
part = 30.0 / 45.0  # ~0.667°
div_index = floor(degrees_in_sign / part)

IF sign is FIRE:
    start_sign = 0  # Aries
ELIF sign is EARTH:
    start_sign = 1  # Taurus
ELIF sign is AIR:
    start_sign = 2  # Gemini
ELSE (WATER):
    start_sign = 3  # Cancer

varga_sign_index = (start_sign + div_index) % 12
```

---

## D60 (Shashtiamsa) - 60 divisions (0.5° each)

**BPHS Rule:**
- 60 equal divisions per sign (MOST PRECISE VARGA)
- Uses sign nature (movable/fixed/dual) + parity (odd/even)
- **Same pattern as D10/D16/D40**
- **NO ROUNDING ALLOWED** - single degree error invalidates chart

**Formula:**
```
part = 30.0 / 60.0  # 0.5°
div_index = floor(degrees_in_sign / part)

IF sign is MOVABLE:
    start_offset = 0 if sign is ODD else 8
ELIF sign is FIXED:
    start_offset = 0 if sign is ODD else 8
ELIF sign is DUAL:
    start_offset = 4 if sign is ODD else 8

varga_sign_index = (sign_index + start_offset + div_index) % 12
```

**Sign Classification:** Same as D10/D16/D40

---

## Common Rules (All Vargas)

1. **DMS Preservation:**
   - Varga charts preserve EXACT D1 degrees/minutes/seconds
   - Only sign changes, never DMS values
   - Formula: `varga_longitude = varga_sign_index * 30 + degrees_in_sign`

2. **Ascendant Handling:**
   - Ascendant uses SAME formula as planets
   - No special treatment

3. **House Calculation:**
   - Whole Sign system: `house = ((planet_sign_index - ascendant_sign_index + 12) % 12) + 1`
   - Ascendant always in house 1

4. **Boundary Checks:**
   - `div_index` must be clamped to [0, divisions-1]
   - `varga_sign_index` must be in [0, 11]

---

## Validation Tests

For each varga:
1. **Division Count:** Verify correct number of divisions
2. **Sign Range:** All signs must be 0-11
3. **House Range:** All houses must be 1-12
4. **Ascendant House:** Must always be 1
5. **DMS Preservation:** DMS values must match D1 exactly
6. **Boundary Degrees:** Test 0°, mid-sign, 29°59′59″

---

## Lock Status

Once all tests pass and Prokerala/JHora parity is achieved:
- ✅ Lock varga engine
- ✅ Document rules per varga
- ✅ Mark D1-D60 as GOLD STANDARD

