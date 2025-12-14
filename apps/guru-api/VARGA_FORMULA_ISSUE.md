# Varga Formula Implementation Issue

## Problem
The user provided Parashara varga formulas for D7, D10, D12, but these formulas do not match the user's own reference data from their screenshot.

## User's Specified Formulas

### D7 (Saptamsa)
- If B is ODD: final_sign = B + N
- If B is EVEN: final_sign = B + (N * 7)

### D10 (Dasamsa)  
- If B is ODD: final_sign = Aries + N = 1 + N
- If B is EVEN: final_sign = Capricorn + N = 10 + N

### D12 (Dwadasamsa)
- final_sign = B + N

## Reference Data (from user's screenshot)
These are the expected results that must match 100%:

### D7
- Asc: 2 (Taurus), Ve: 2, Ke: 3, Ma: 4, Sa: 4, Ju: 5, Moon: 6, Sun: 7, Ra: 9, Me: 12

### D10
- Asc: 4 (Cancer), Ke: 4, Sun: 8, Ju: 8, Ra: 8, Moon: 9, Ve: 11, Me: 12, Ma: 12

### D12
- Me: 1, Sa: 1, Ra: 2, Ve: 6, Ju: 6, Sun: 7, Ma: 8, Ke: 8, Moon: 9

## Status
The formulas as specified do not produce the reference results. Further investigation needed to find the correct formula interpretation or implementation.

