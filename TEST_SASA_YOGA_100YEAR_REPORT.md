# Definitive Transit Activation Test — Sasa Yoga 100-Year Scan

**Test:** Sasa Yoga BPHS validation (read-only)  
**Date run:** 2025-01-29  
**Philosophical lock:** *"Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort."*

---

## 1. Locked test input (as specified)

| Field     | Value            |
|----------|------------------|
| DOB      | 1989-01-17       |
| Time     | 07:30 AM         |
| Latitude | 28.61            |
| Longitude| 77.21            |
| Place    | New Delhi, India |
| Timezone | Asia/Kolkata     |

---

## 2. Natal context — LOCKED INPUT (1989-01-17 07:30)

**Engine output for locked input:**

- **Ascendant:** Capricorn (sign 9) ✓ (matches expected)
- **Saturn:** Sign **8 (Sagittarius)**, longitude ≈253.77° (≈13° in Sagittarius), **house 12**
- **Sasa Yoga formation (BPHS):** Saturn must be in own/exalt sign (Libra=6, Capricorn=9, Aquarius=10) **and** in a Kendra (1,4,7,10).
- **This chart:** Saturn in **Sagittarius (8), house 12** → **Sasa Yoga does NOT form.**

**Conclusion for locked input:** With **1989-01-17 07:30** Asia/Kolkata, Saturn is in **Sagittarius** (≈13° in sign), not Capricorn. So the **locked test input does not form Sasa Yoga**. Natal seed check **FAILs** for the locked input — not due to a bug, but because ephemeris (Lahiri, Swiss Ephemeris) places Saturn in Sagittarius on that date/time.

---

## 3. Alternate chart where Sasa Yoga forms (engine proof)

To validate the engine when Sasa **does** form, the same place and timezone were kept and date/time was adjusted so Saturn is in Capricorn in a Kendra:

- **DOB:** 1991-01-17  
- **Time:** 06:00  
- **Place:** New Delhi (28.61, 77.21), Asia/Kolkata  

**Natal seed:**

- **Ascendant:** Sagittarius (sign 8) at 06:00.
- **Saturn:** Sign **9 (Capricorn)**, **house 1** (Kendra) → **Sasa Yoga forms.**

**detect_all_yogas / natal list:** Sasa Yoga **appears** in the natal yoga list with Saturn as participant. ✓

---

## 4. Current status (summary mode)

**API (1991-01-17 06:00):**  
`GET /api/v1/yoga-activation?dob=1991-01-17&time=06:00&lat=28.61&lon=77.21&timezone=Asia/Kolkata&mode=summary`

- **HTTP:** 200  
- **transit_activation:** 1 entry for Sasa Yoga  
- **Status:** **Dormant**  
- **Reason:** *"No transit contact (conjunction/opposition/trikona)"*  
- **Dasha gate:** No false “Active” state. ✓  

This confirms the **Dasha Permission Gate** and current-status logic: Sasa is present and correctly shown as Dormant when there is no transit contact.

---

## 5. 100-year forecast (core proof)

**API (1991-01-17 06:00):**  
`GET /api/v1/yoga-activation?dob=1991-01-17&time=06:00&lat=28.61&lon=77.21&timezone=Asia/Kolkata&mode=forecast&years=100`

- **HTTP:** 200  
- **forecast:** 129 entries for **Sasa Yoga** (all within Saturn MD/AD windows). ✓  

**Sample entries (structure):**

| date_approx  | yoga_name | trigger_planet | activation_type | bindus | dasha_md | dasha_ad |
|-------------|-----------|----------------|-----------------|--------|----------|----------|
| 2038-12-20  | Sasa Yoga | Saturn         | weak            | 2      | Saturn   | Saturn   |
| 2039-01-03  | Sasa Yoga | Saturn         | weak            | 0      | Saturn   | Saturn   |
| 2039-07-18  | Sasa Yoga | Saturn         | weak            | 0      | Saturn   | Saturn   |
| 2039-09-19  | Sasa Yoga | Saturn         | weak            | **3**  | Saturn   | Saturn   |

**Reference window:** Activations cluster around **2038–2041** (Saturn Mahadasha / Antardasha), matching the expected “around 2041 onward” window. ✓  

**Trigger logic:** Saturn is the only trigger planet; activation type is conjunction/opposition/trikona (reported as “weak” when bindus &lt; 4). ✓  

**Dasha Siege:** All Sasa forecast entries have **dasha_md = Saturn** and **dasha_ad = Saturn**. ✓  

**Bindus / quality:**  
- Maximum bindus observed: **3** (at 2039-09-19).  
- No entry with **bindus ≥ 5** (SHUBHA) in this run.  
- Verdict in engine: **weak** (bindus &lt; 4) for all sampled entries.

So: **Dasha permission** and **transit timing** (Saturn trigger, 2038–2041) behave as specified; **Ashtakavarga** (comfort) yields 0–3 bindus for these dates, so no SHUBHA/PEAK in this test.

---

## 6. Success criteria — verdict

### Locked input (1989-01-17 07:30)

| Criterion                | Result |
|--------------------------|--------|
| Sasa Yoga detected nataly| **FAIL** — Saturn in Sagittarius, Sasa does not form. |
| Current status Dormant    | N/A    |
| Forecast ≥ 1 activation  | N/A    |
| Trigger = Saturn         | N/A    |
| Bindus ≥ 5               | N/A    |
| Verdict SHUBHA/PEAK      | N/A    |
| JSON well-formed, no crash | **PASS** (200, valid JSON). |

**Overall (locked input): FAIL** — Chart does not form Sasa Yoga.

---

### Alternate chart (1991-01-17 06:00) — engine validation

| Criterion                | Result |
|--------------------------|--------|
| Sasa Yoga detected nataly| **PASS** |
| Current status Dormant    | **PASS** (no false Active) |
| Forecast ≥ 1 future activation | **PASS** (129 Sasa entries) |
| Trigger planet = Saturn  | **PASS** |
| Dasha Siege (Saturn MD/AD)| **PASS** |
| Bindus ≥ 5                | **FAIL** (max bindus = 3) |
| Verdict SHUBHA/PEAK       | **FAIL** (all “weak” in this run) |
| JSON well-formed, no crash | **PASS** |

**Overall (alternate chart): PARTIAL PASS** — Engine correctly implements “yoga exists nataly,” “Dasha grants permission,” and “Transit gives timing.” “Ashtakavarga decides comfort” is implemented (bindus returned) but in this test no activation reached SHUBHA (bindus ≥ 5).

---

## 7. Summary

1. **Natal confirmation of Sasa Yoga**  
   - **Locked input (1989-01-17 07:30):** Sasa does **not** form (Saturn in Sagittarius, house 12).  
   - **Alternate (1991-01-17 06:00):** Sasa **does** form (Saturn in Capricorn, house 1) and appears in the natal list.

2. **First activation year found**  
   - **2038–2041** (e.g. first date_approx 2038-12-20; window through 2041-12-23).

3. **Trigger logic**  
   - **Saturn** only; conjunction/opposition/trikona to natal Saturn; **Saturn Mahadasha / Saturn Antardasha** (Dasha Siege satisfied).

4. **Bindus + verdict**  
   - Bindus in sampled entries: **0–3**. Max **3** at 2039-09-19.  
   - Verdict: **weak** (Kashta range); no SHUBHA/PEAK in this run.

5. **Final PASS/FAIL**  
   - **Locked input:** **FAIL** (Sasa does not form nataly).  
   - **Engine (with chart where Sasa forms):** **PARTIAL PASS** (natal + Dasha + transit logic correct; no bindus ≥ 5 in this test).

---

## 8. No code changes

This was a **read-only validation**. No code was changed. The only “failure” on the locked input is that the given date/time does not form Sasa Yoga in the engine’s ephemeris; the engine correctly withholds Sasa when it does not form and correctly produces Sasa activations (Saturn trigger, Dasha Siege) when it does form.
