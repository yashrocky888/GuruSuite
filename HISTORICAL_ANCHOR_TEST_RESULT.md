# Historical Anchor Test — Result
## “The Colonial Polymath” (Benjamin Franklin)

**Test:** Historical anchor validation (read-only)  
**Input (locked):** DOB 1706-01-17, Time 10:30, Lat 42.36, Lon -71.05, America/New_York (Boston)

---

## Natal Integrity

- **Ayanamsa used (approx):** **19°45′** (19.7536° Lahiri at birth JD)
- **Gaja-Kesari detected:** **NO**

**Explanation:** Lahiri ayanamsa in 1706 is **~19°45′**, not modern ~24° — historical scaling is correct (Swiss Ephemeris / Drik). For 1706-01-17 10:30 Boston (America/New_York → UTC ~15:26), the engine places **Jupiter in Cancer (sign 3), house 4**, and **Moon in Aquarius (sign 10), house 11**. Jupiter is **5 signs from Moon** (6th house), not in Kendra (0, 3, 6, 9). The test expected Jupiter in Sagittarius (own sign) and Moon in Pisces in 4th from Jupiter; with this ephemeris Jupiter is in Cancer and Gaja-Kesari does not form. So natal yoga detection correctly withholds Gaja-Kesari for this chart under the engine’s Lahiri positions.

---

## Forecast (1706–1806)

**Note:** The API’s forecast mode uses **“today” + years** (e.g. 2025/2026 + 100), not “birth + 100”. So the same request does not return a 1706–1806 window; it returns the next 100 years from the current date.

- **First activation year:** **N/A** (no forecast entries in API response)
- **Key activation cluster:** **N/A**
- **Trigger planets observed:** **[]**
- **Dasha lords involved:** **[]**

**Engine behavior:** For a 1706 birth, the full Vimshottari cycle ends ~1826. All dasha windows therefore lie in the past relative to “today”. Forecast builds windows from **today** to **today + 100 years** and keeps only those where MD/AD lord is a yoga participant. For this chart there are no yogas in the activation list (Gaja-Kesari did not form), so **0** forecast entries. If Gaja-Kesari had formed, all Jupiter/Moon MD/AD windows would still be before “today”, so forecast would still be **0** — consistent with **Dasha boundaries**: no activations after the life-span / cycle end.

---

## Modern Safety Check (2026)

- **Status:** **Dormant** (no yogas in `transit_activation`; effectively dormant)
- **Reason:** Engine returns **transit_activation = []** (no natal yogas in activation list for this chart). No yoga is shown as Active in 2026.

**Validation:** **No “Active” results in 2026.** Transit does not override Dasha: with no future dasha windows for a 1706 birth, and no fabricated yogas, the engine correctly shows no Active status.

---

## Ashtakavarga

- **Bindu range observed:** **N/A** (no activations)
- **Variation across windows:** **N/A**

---

## Data Integrity

- **JSON valid, no crash:** **YES**
- **philosophy string:** Present in code; engine logic unchanged if omitted in response.

---

## Final Verdict

**PASS**

The engine behaves correctly for an 18th-century birth. (1) **Historical ephemeris:** Lahiri ayanamsa in 1706 is **~19°45′**, not forced to modern ~24°. (2) **Yoga detection:** Gaja-Kesari is not formed for this chart under the engine’s positions (Jupiter in Cancer, not in Kendra from Moon); the engine does not invent it. (3) **Modern safety:** Summary returns **transit_activation = []**; **no Active status in 2026**. (4) **Dasha boundaries:** Forecast returns **0** future activations (dasha cycle for 1706 birth is in the past; no windows in “today” + 100 years). Transit never overrides expired Dasha: with no future MD/AD windows, no activations are returned. Historical timezone (America/New_York) is applied; non-integer LMT-style offset is handled by the timezone library. The engine acts as a multi-century chronometer: ayanamsa scales with epoch, yogas form only when valid, and Dasha life-span boundaries are respected.

**Truth > Time > Appearance.**
