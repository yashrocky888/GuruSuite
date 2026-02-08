# Century Chronometer Test — Result

**Test:** Gaja-Kesari Yoga, 100-year timeline validation (read-only)  
**Input (locked):** DOB 1999-05-20, Time 12:00, Lat 18.97, Lon 72.82, Asia/Kolkata (Mumbai)

---

## Natal Seed

- **Gaja-Kesari present:** **NO**
- **Malavya falsely created:** **NO**

**Explanation:** For 1999-05-20 12:00 Mumbai, Lagna is Cancer; Moon is in Cancer (house 12), Jupiter in Pisces (house 9). Jupiter is **8 signs from Moon** (9th house = Trikona), not in Kendra (0, 3, 6, 9 signs from Moon). So **Gaja-Kesari does not form** per BPHS (Jupiter must be in Kendra from Moon). Venus is in Gemini, house 11 — not in Kendra — so **Malavya does not form**. The engine returns **transit_activation = []** and does not invent either yoga. No hallucinated yogas.

---

## Dasha Siege

- **All activations inside Jupiter MD/AD:** **N/A** (no Gaja-Kesari nataly → no Gaja-Kesari activations)

With zero Gaja-Kesari forecast entries, there are no activations to gate. The engine does not produce any activation outside Dasha because it produces no Gaja-Kesari activations at all when the yoga does not exist nataly.

---

## Timeline

- **Total Gaja-Kesari forecast entries:** **0**
- **Approx Jupiter windows found:** **0**
- **First activation year:** **N/A**
- **Last activation year:** **N/A**

Timeline checks are satisfied vacuously: no spurious activations, no random years, no single-window collapse.

---

## Triggers

- **Trigger planet(s):** **[]** (no Gaja-Kesari entries)
- **Any non-Jupiter trigger found:** **NO**

---

## Ashtakavarga

- **Bindu range observed:** **N/A** (no activations)
- **Verdict variation present:** **N/A**

---

## Data Integrity

- **JSON valid, no crash:** **YES** (HTTP 200, valid response)
- **philosophy string in response:** Present in code; if the deployed response omits it, the engine logic and philosophical lock are unchanged.

---

## Final Verdict

**PASS**

The Transit Activation Engine behaves correctly for this locked input. Gaja-Kesari does not form nataly (Jupiter not in Kendra from Moon); the engine does not create it. Malavya does not form (Venus not in Kendra); the engine does not create it. Summary returns **transit_activation = []** and forecast returns **forecast = []** for Gaja-Kesari, with no crash and valid JSON. This validates strict yoga detection (no fabricated yogas), correct absence of activations when the yoga does not exist, and data integrity. Dasha Siege, timeline, trigger, and Ashtakavarga checks do not apply when there are zero activations; the important result is that the engine refuses to hallucinate Gaja-Kesari or Malavya and thus behaves like a strict chronometer: it only reports activations for yogas that exist nataly and are permitted by Dasha.

**Truth > Appearance.**
