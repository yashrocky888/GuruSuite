# D16-D60 Varga Charts - Prokerala/JHora Fix

## Current Status

**Test Birth Data:**
- DOB: 1995-05-16
- Time: 18:38 IST
- Place: Bangalore (12.9716°N, 77.5946°E)
- D1 Ascendant: Scorpio (212.2799°)

## Current Outputs (Need Verification Against Prokerala)

### D16 (Shodasamsa)
- **Current Ascendant:** Leo (index 4, house 1)
- **Current Formula:** Uses D10 pattern (movable/fixed/dual + parity)
- **Needs:** Prokerala verification

### D20 (Vimsamsa)
- **Current Ascendant:** Sagittarius (index 8, house 1)
- **Current Formula:** Simple forward progression (like D12)
- **Needs:** Prokerala verification

### D24 (Chaturvimsamsa)
- **Current Ascendant:** Leo (index 4, house 1)
- **Current Formula:** Element-based starting signs
- **Needs:** Prokerala verification

### D27 (Bhamsa)
- **Current Ascendant:** Pisces (index 11, house 1)
- **Current Formula:** Nakshatra-based progression
- **Needs:** Prokerala verification

### D30 (Trimsamsa)
- **Current Ascendant:** Virgo (index 5, house 1)
- **Current Formula:** Odd forward, Even reverse
- **Needs:** Prokerala verification

### D40 (Khavedamsa)
- **Current Ascendant:** Libra (index 6, house 1)
- **Current Formula:** Uses D10 pattern (movable/fixed/dual + parity)
- **Needs:** Prokerala verification

### D45 (Akshavedamsa)
- **Current Ascendant:** Libra (index 6, house 1)
- **Current Formula:** Element-based starting signs (like D24)
- **Needs:** Prokerala verification

### D60 (Shashtiamsa)
- **Current Ascendant:** Scorpio (index 7, house 1)
- **Current Formula:** Uses D10 pattern (movable/fixed/dual + parity)
- **Needs:** Prokerala verification

## Next Steps

1. **Get Prokerala Reference Data** for test birth chart
2. **Compare planet-by-planet** for each varga
3. **Fix formulas** to match Prokerala exactly
4. **Verify** against JHora as secondary validation

## Reference

- Prokerala: https://www.prokerala.com/astrology/divisional-charts.php
- Test against same birth data used for D10/D12 verification

