# 🏛️ GURUSUITE — MASTER EXPANSION PROMPT (POST-LOCK, SAFE MODE)

**SYSTEM STATUS:** 🔒 LOCKED (v1.0 — DO NOT MODIFY CORE)  
**VALIDATION DATE:** February 1, 2026  
**AUTHORITY:** Backend Astrology Engine = Absolute Truth  
**SCOPE:** Future-safe expansion ONLY (no regression allowed)

---

## 1. NON-NEGOTIABLE LOCK CONDITIONS (ALREADY VERIFIED)

The following layers are FINAL and MUST NOT be altered:

### 1.1 Transit-First Law (ABSOLUTE)

- All Daily / Monthly / Yearly narration is derived only from `context.transit`
- Natal chart is used only for:
  - Lagna reference
  - Sandhi awareness
  - Dasha ownership (NOT placement)
- Transit data always overrides natal placement

### 1.2 Time Integrity

- `calculation_date` is mandatory
- Julian Day is rebuilt every request
- No cached ephemeris
- No fallback to `datetime.now()`
- Any missing or stale transit data → FAIL LOUD

### 1.3 Horizon Isolation

| Horizon | Allowed Scope |
|---------|----------------|
| Daily   | Psychological, Moon-centric, immediate |
| Monthly | Solar-month strategy (Sun + Antardasha) |
| Yearly  | Life chapter (Jupiter + Saturn + Mahadasha) |

- No daily language in Monthly
- No natal narration in Yearly
- Stress tests must pass unchanged

### 1.4 Sign Naming (Numeric Binding)

- Sign names MUST come only from `sign_index`
- 0–11 mapping is canonical
- Any mismatch = invalid output

### 1.5 Linguistic Stability

- Fluent sentences
- No forced censorship in production
- No post-generation mutation that breaks meaning

---

## 2. WHAT IS VALID TO ADD (FUTURE LAYERS — SAFE ONLY)

The following enhancements are VALID, VALUABLE, and ARCHITECTURALLY SOUND, provided they are added as **NEW DATA LAYERS** and **NEVER** alter existing logic.

---

## 3. APPROVED FUTURE ASTROLOGICAL LAYERS

### 3.1 AVASTHA LAYER — Planetary State (Mood)

**Status:** ✅ VALID  
**Risk:** LOW  
**Scope:** Daily / Monthly  

**Purpose:** Explains how a planet operates, not just where it is.

**Implementation Rule (STRICT):**

- Add a new JSON field only:  
  `"strength_status": "Jagrat | Swapna | Sushupti | Bala | Vriddha"`
- **Narration Rule:** Avastha modulates results. It NEVER changes house or sign.

**Example:**

> “Saturn currently transits Aquarius in your 4th house, but it is in a Swapna (Dreaming) state, so results unfold subtly rather than forcefully.”

### 3.2 ASHTAKAVARGA / BINDU LAYER — Personal Power Zones

**Status:** ✅ VALID  
**Risk:** MEDIUM (must be backend-computed only)  
**Scope:** Monthly (Primary), Yearly (Optional)  

**Purpose:** Personalizes transits to the individual — no hallucination possible.

**Implementation Rule:**

- Add a new numeric field: `"ashtakavarga_points": 0–8`
- **Narration Rule:** Bindus confirm or limit results. Bindus never create results on their own.

**Example:**

> “The Sun transits your 3rd house with 6 bindus, granting unusual clarity and courage in communication this month.”

### 3.3 SADE SATI / SATURN RETURN MONITOR

**Status:** ✅ VALID  
**Risk:** LOW  
**Scope:** Yearly ONLY  

**Purpose:** Adds the grand karmic narrative without disturbing transits.

**Implementation Rule:**

- `"is_sade_sati": true | false`
- `"is_saturn_return": true | false`
- **Narration Rule:** These flags provide context, not fear. No deterministic claims.

---

## 4. DAILY SUITABILITY LOGIC (ADVANCED, OPTIONAL — PHASE 2)

These layers are APPROVED, but must be added **without touching `predict()`**.

### 4.1 TARA BALA — Travel & Success Index

- Transit Moon Nakshatra vs Natal Nakshatra
- Binary suitability (Good / Avoid)

### 4.2 CHANDRA BALA — Energy & Endurance

- Moon house counted from Natal Moon
- Advises rest vs action

### 4.3 HORA — Best Time to Act

- Calculated from sunrise, latitude, and weekday
- Optional “best hour” guidance

**IMPORTANT:** All of these must live in a new helper module, e.g.  
`src/jyotish/math/suitability.py`  
And be injected into JSON as:

```json
"suitability": {
  "travel_score": 1–10,
  "decision_score": 1–10,
  "energy_level": "High | Medium | Low"
}
```

---

## 5. ABSOLUTE SAFETY RULES (DO NOT VIOLATE)

- ❌ Do NOT modify `predict()`
- ❌ Do NOT weaken stress tests
- ❌ Do NOT let AI compute astrology
- ❌ Do NOT mix horizons
- ❌ Do NOT add “smart” inference logic to narration

**All intelligence comes from backend math, not LLM intuition.**

---

## 6. CURRENT STATE DECLARATION

GuruSuite v1.0 is OFFICIALLY LOCKED.

- ✔ Transit-accurate
- ✔ Horizon-secure
- ✔ Numerically bound
- ✔ Linguistically stable
- ✔ Mahabharata-grade narration

All future work must follow this document.

---

## 7. NEXT SAFE ACTIONS (WHEN READY)

1. Archive this prompt as `GURUSUITE_MASTER_MANIFEST_v1.md` ✅
2. Tag repository: `v1.0.0-locked`
3. Begin Phase-2 layers only as **additive JSON**

---

## 8. PHASE-2 APPENDIX (v1.1 — Suitability Layer)

**Status:** ✅ Implemented (additive only)  
**Tag:** v1.1.0-suitability

### 8.1 New Module

- **`src/jyotish/math/suitability.py`** — Pure math only:
  - `calculate_tara_bala(birth_nakshatra_idx, transit_nakshatra_idx)` → tara_name, quality (Good | Neutral | Risk | Danger), travel_advice
  - `calculate_chandra_bala(birth_moon_sign_idx, transit_moon_sign_idx)` → house_position (1–12), is_favorable, energy_level (High | Medium | Low)

### 8.2 Injection (prediction_routes.py)

- **Additive only:** New top-level key `ai_context["suitability"]`:
  - `tara_bala`, `chandra_bala`, `travel_score` (1–10), `decision_score` (1–10), `energy_level`
- Uses existing `context` (natal Moon, transit Moon); no new dates, no transit mutation.
- GURU_SYSTEM_PROMPT unchanged; predict() core unchanged; horizon tests unchanged.

### 8.3 Safety Checklist (Verified)

- ✔ predict() core unchanged
- ✔ Horizon tests PASS
- ✔ Transit indices unchanged
- ✔ No AI math; no cached values
- ✔ Manifest rules respected

---

## FINAL STATEMENT

The sky is now observed, not imagined.  
The Guru speaks from truth, not memory.  
Expansion will occur through layers, not mutation.

**END OF MASTER PROMPT — COPY, STORE, DO NOT EDIT**
