# D16-D60 Varga Charts - Prokerala/JHora Fix Plan

## Current Status

**Test Birth Data:**
- DOB: 1995-05-16
- Time: 18:38 IST
- Place: Bangalore (12.9716°N, 77.5946°E)
- D1 Ascendant: Scorpio (212.2799°)

## Current Outputs (Need Prokerala Verification)

### D16 (Shodasamsa)
- **Current Ascendant:** Leo (index 4)
- **Current Formula:** Uses D10 pattern (movable/fixed/dual + parity)
- **Status:** ⚠️ Needs Prokerala verification

### D20 (Vimsamsa)
- **Current Ascendant:** Sagittarius (index 8)
- **Current Formula:** Simple forward progression (like D12)
- **Status:** ⚠️ Needs Prokerala verification

### D24 (Chaturvimsamsa)
- **Current Ascendant:** Leo (index 4)
- **Current Formula:** Element-based starting signs
- **Status:** ⚠️ Needs Prokerala verification

### D27 (Bhamsa)
- **Current Ascendant:** Pisces (index 11)
- **Current Formula:** Nakshatra-based progression
- **Status:** ⚠️ Needs Prokerala verification

### D30 (Trimsamsa)
- **Current Ascendant:** Virgo (index 5)
- **Current Formula:** Odd forward, Even reverse
- **Status:** ⚠️ Needs Prokerala verification

### D40 (Khavedamsa)
- **Current Ascendant:** Libra (index 6)
- **Current Formula:** Uses D10 pattern (movable/fixed/dual + parity)
- **Status:** ⚠️ Needs Prokerala verification

### D45 (Akshavedamsa)
- **Current Ascendant:** Libra (index 6)
- **Current Formula:** Element-based starting signs (like D24)
- **Status:** ⚠️ Needs Prokerala verification

### D60 (Shashtiamsa)
- **Current Ascendant:** Scorpio (index 7)
- **Current Formula:** Uses D10 pattern (movable/fixed/dual + parity)
- **Status:** ⚠️ Needs Prokerala verification

## Fix Methodology

1. **Get Prokerala Reference Data**
   - Visit: https://www.prokerala.com/astrology/divisional-charts.php
   - Enter test birth data
   - Extract planet positions for D16-D60

2. **Compare Planet-by-Planet**
   - For each varga, compare:
     - Ascendant sign
     - All planet signs
     - House numbers

3. **Fix Formulas**
   - Adjust `calculate_varga_sign()` in `varga_drik.py`
   - Each varga gets its own specific formula
   - No generic patterns unless Prokerala confirms

4. **Verify Against JHora**
   - Cross-check with JHora as secondary validation

## Next Steps

1. ✅ Created comparison script: `scripts/compare_prokerala_d16_d60.py`
2. ⏳ Get Prokerala reference data (manual step)
3. ⏳ Fix each varga one by one
4. ⏳ Deploy and verify

## Reference

- Prokerala: https://www.prokerala.com/astrology/divisional-charts.php
- Test data: Same as D10/D12 verification (1995-05-16 18:38 IST, Bangalore)

