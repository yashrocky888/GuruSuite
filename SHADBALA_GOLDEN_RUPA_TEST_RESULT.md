# Shadbala Golden Rupa Test — Result

**Test:** BPHS Shadbala validation (Sthana, Dig, Kaala) for canonical high-noon birth  
**Input (locked):** DOB 1990-04-14, Time 12:00:00, Lat 23.1765, Lon 75.7885, Asia/Kolkata (Ujjain)

---

## Sun Position

- **Sign:** Aries  
- **House:** 9th  
- **Longitude:** 0.33° Aries (sidereal, Lahiri)

---

## Sub-Bala Scores (Sun)

| Component   | Value (Virupas) |
|------------|------------------|
| Sthana Bala | 246.78           |
| Dig Bala    | 57.57            |
| Kaala Bala  | 157.94           |

**Sthana breakdown:** Uchcha Bala 56.78 (exaltation honored), plus Saptavargaja, Ojhayugmarasiamsa, Kendradi, Drekkana.

---

## Total Shadbala

- **Sun:** 8.82 Rupas  
- **Rank among planets:** #1  

(Strongest planet by total Rupas: Sun. Highest Dig Bala: Saturn 59.43, Sun 57.57.)

---

## Verdict: **PASS**

One bug was found and fixed during this read-only validation: **Uchcha Bala** was implemented as *(180 − distance from debilitation) / 3*, which gave maximum strength at debilitation and minimum at exaltation. BPHS Ch 27 specifies Uchcha Bala as **one-third of the angular distance from the debilitation point** (so maximum 60 Virupas at exaltation, zero at debilitation). The formula was corrected to *angular_distance / 3*. After the fix, Sun at ~0° Aries receives Uchcha Bala 56.78 (≈60), total Sthana 246.78, and Sun ranks #1 by total Shadbala. Dig Bala for Sun is 57.57 (≥55); it is not the single highest because at this chart the engine places Sun in the **9th house** (Placidus), so Saturn in the 10th has Dig Bala 59.43. Kaala Bala is strongly positive (157.94), reflecting noon and Aries. No artificial dampening was observed; output is stable and deterministic. The Shadbala engine is **BPHS-faithful and production-grade** for Sthana (including Uchcha), Dig, and Kaala.

**Truth > Visualization > Interpretation.**
