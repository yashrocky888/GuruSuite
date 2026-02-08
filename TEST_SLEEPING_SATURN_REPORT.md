# Definitive Test Case Report: "The Sleeping Saturn" — Sasya Yoga Long-Range Activation

**Test name:** Sasya Yoga (Sasa Yoga) Long-Range Activation Test  
**Date run:** 2025-01-29  
**Type:** Read-only validation (no code changes unless bug found).

---

## 1. Input data (exact)

| Field      | Value                |
|-----------|----------------------|
| DOB       | 1971-06-28           |
| Time      | 07:30                |
| Latitude  | -25.74               |
| Longitude | 28.18                |
| Place     | Pretoria, South Africa |
| Timezone  | Africa/Johannesburg (UTC+02:00) |

---

## 2. Natal context (seed check)

### Engine output for this chart

- **Natal Saturn:** Sign index **1** (Taurus), **house 11**.
- **Sasa Yoga formation (BPHS):** Saturn must be in **own or exaltation sign** (Libra=6, Capricorn=9, Aquarius=10) **and** in a **Kendra** (1, 4, 7, 10).
- **This chart:** Saturn in **Taurus (1), house 11** → not in 6/9/10, not in Kendra → **Sasa Yoga does not form**.

### Yoga detection

- `detect_all_yogas` was run with the same planets/houses used by the Transit Activation engine.
- **Pancha Mahapurusha (Sasa) check:** Saturn sign = 1 (Taurus). Sasa requires sign in {6, 9, 10}. **Not satisfied.**
- **Result:** Sasa Yoga is **not** in the natal yoga list for this chart. Other yogas (e.g. from extended_yogas, combination, etc.) are present; none named "Sasa Yoga" or "Sasya Yoga".

### Conclusion on “Sasya Yoga should appear”

- **Verdict:** Sasa Yoga **correctly does not appear** for this input.
- **Reason:** The given birth data does not satisfy Sasa Yoga formation (Saturn in Taurus, not in Libra/Capricorn/Aquarius in a Kendra). This is **not** a yoga-detection bug.

---

## 3. Current status (summary API)

- **API:** `GET /api/v1/yoga-activation?dob=1971-06-28&time=07:30&lat=-25.74&lon=28.18&timezone=Africa/Johannesburg&mode=summary`
- **HTTP:** 200
- **Response:** `{"transit_activation":[],"forecast":[],"error":null}` (and `philosophy` when server returns it)
- **Interpretation:** No yogas in the Transit Activation engine’s filtered list (natal yogas with participants and non-Dosha). So current status is effectively “no activation list” rather than “Sasya Dormant”. Sasya is not in scope because it does not form.

---

## 4. Forecast behavior (100-year)

- **API:** `GET /api/v1/yoga-activation?dob=1971-06-28&time=07:30&lat=-25.74&lon=28.18&timezone=Africa/Johannesburg&mode=forecast&years=100`
- **HTTP:** 200
- **Response:** `forecast` length = **0**, `error`: null.
- **Reason:** Forecast only considers **natal yogas** that pass Dasha Siege (MD/AD lord is participant). Since Sasa Yoga does not form for this chart, there is no Saturn-led yoga in the natal list, so no Sasa activation windows are computed. Engine behavior is consistent with design.

---

## 5. Success criteria (PASS/FAIL)

| Criterion | Required | Actual | Result |
|----------|----------|--------|--------|
| Sasya Yoga detected nataly | Yes | Not present (Saturn in Taurus; Sasa requires 6/9/10 + Kendra) | **FAIL** (chart does not form Sasa) |
| Current status Dormant/Supta | Yes | N/A (yoga not in list) | **N/A** |
| Forecast shows Sasya in future | Yes | Forecast empty for Sasa | **FAIL** (no Sasa to forecast) |
| Activation strength SHUBHA/PEAK | Yes | N/A | **N/A** |
| Bindus ≥ 5 | Yes | N/A | **N/A** |
| Saturn-driven activation | Yes | N/A | **N/A** |
| No false Active today | Yes | No false activation | **PASS** |
| No crash / malformed data | Yes | 200, valid JSON | **PASS** |

**Overall verdict: FAIL** — Failure is due to **test input**, not engine/API bug: the given chart does not contain Sasa (Sasya) Yoga.

---

## 6. JSON snippet (summary + forecast)

**Summary (mode=summary):**
```json
{"transit_activation":[],"forecast":[],"error":null}
```

**Forecast (mode=forecast&years=100):**
```json
{"transit_activation":[],"forecast":[],"error":null}
```

No Sasya Yoga activation snippet exists because the yoga does not form for this chart.

---

## 7. Trigger logic and reference window

- **Expected (from spec):** Saturn activating Sasa Yoga in own/exalt sign (e.g. Capricorn/Aquarius/Libra), conjunction/opposition/trikona to natal Saturn, with Dasha Siege (Saturn MD/AD) and BAV bindus ≥ 5 (SHUBHA).
- **Actual:** No Sasa Yoga in natal list → no Saturn-yoga activation windows are generated. Dasha Siege and ingress logic are therefore not exercised for Sasa on this chart.

---

## 8. Recommendation for a definitive Sasa test

To validate “Sleeping Saturn” and 100-year Sasa activation **correctly**, use a chart where **Sasa Yoga actually forms**:

- **Condition:** Saturn in **Libra (6), Capricorn (9), or Aquarius (10)** and in a **Kendra (1, 4, 7, 10)** from Lagna or Chandra Lagna.
- **Example approach:** Choose a birth date/time when Saturn was in Capricorn or Aquarius and place it in a Kendra (e.g. via birth time/place). Then:
  1. Confirm Sasa Yoga appears in natal yoga list (e.g. via strength/yogas or kundli pipeline that uses same `detect_all_yogas`).
  2. Run summary: expect Sasa Yoga with status Dormant when Saturn is not in MD/AD or lacks transit trigger.
  3. Run forecast with `years=100`: expect at least one Sasa Yoga window with trigger planet Saturn, activation type conjunction/opposition/trikona, and bindus ≥ 5 (SHUBHA) in a 2030s (or other) reference window.

---

## 9. Philosophical lock

No change: *“Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort.”* Validation was read-only; no code changes were made.
