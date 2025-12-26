# D16-D60 Varga Fix - Ready for Prokerala Data

## Current Implementation Status

All D16-D60 varga calculations are implemented in `varga_drik.py` using formulas that may not match Prokerala exactly. 

**Current formulas are based on:**
- D16, D40, D60: D10 pattern (movable/fixed/dual + parity)
- D20: D12 pattern (simple forward)
- D24, D45: Element-based starting signs
- D27: Nakshatra-based progression
- D30: Odd forward, Even reverse

## Fix Process (Once Prokerala Data Available)

### Step 1: Get Prokerala Reference
1. Visit: https://www.prokerala.com/astrology/divisional-charts.php
2. Enter: 1995-05-16, 18:38 IST, Bangalore
3. Extract planet positions for each varga

### Step 2: Compare & Identify Mismatches
Run comparison script:
```bash
python scripts/compare_prokerala_d16_d60.py --verify
```

### Step 3: Fix Each Varga Individually
For each varga with mismatches:
1. Identify which planets are wrong
2. Analyze the pattern (starting sign, progression, reversal rules)
3. Update `calculate_varga_sign()` in `varga_drik.py`
4. Test against Prokerala reference
5. Verify against JHora

### Step 4: Lock the Code
Add lock comments:
```python
# 🔒 PROKERALA + JHORA VERIFIED
# 🔒 DO NOT MODIFY WITHOUT GOLDEN TEST UPDATE
```

## Files to Modify

- `src/jyotish/varga_drik.py` - `calculate_varga_sign()` function
- `tests/test_varga_prokerala_d16_d60.py` - Add golden tests
- `scripts/compare_prokerala_d16_d60.py` - Update reference data

## Current Outputs

See: `/tmp/current_d16_d60_outputs.txt`

## Next Action

**REQUIRED:** Prokerala reference data for test birth chart (1995-05-16 18:38 IST, Bangalore)

Once data is available, fix formulas one by one to match Prokerala exactly.

