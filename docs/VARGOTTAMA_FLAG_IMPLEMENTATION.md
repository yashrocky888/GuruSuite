# Vargottama Flag Implementation

## Classical definition (BPHS)

**Vargottama** means “in the same varga (division).” A planet is **Vargottama** when its sign in the D1 chart (Rashi) is the **same** as its sign in the D9 chart (Navamsa):

- **Definition:** `D1.sign_index == D9.sign_index` (per planet).
- Rahu and Ketu are **not** assigned Vargottama (BPHS: nodes excluded from this strength).
- No new astrology math: D1 and D9 are already computed; this is a boolean comparison only.

## Why AI must not infer it

- Strength is **not** opinion; it is **math**. If the model infers or guesses Vargottama from D1/D9 text, it can be wrong or inconsistent.
- Exposing a single **backend-computed** `is_vargottama` flag ensures:
  - One source of truth (no hallucination).
  - Same definition everywhere (D1–D9 sign match only).
  - Safe “Guru Context” packaging for AI: the flag is explicit, not derived in prompts.

## Where the flag lives

- **Computation:** `apps/guru-api/src/jyotish/varga_engine.py` → `compute_vargottama_flags(d1_planets, d9_planets)`.
- **Attachment:** In `apps/guru-api/src/api/kundli_routes.py`, after D9 is built, flags are computed and attached to **D1 planets only**: `base_kundli["Planets"][planet]["is_vargottama"] = True/False`.
- **API:** Any response that includes full Kundli (e.g. GET/POST `/api/v1/kundli`) returns D1 with `Planets[*].is_vargottama` (boolean). JSON shape is unchanged except for this new field.

## Confirmation: no astrology math changed

- **No** changes to planetary longitudes, D1, D9, or any varga calculation.
- **No** changes to yoga detection, dasha, transit, or Shadbala formulas.
- **Additive only:** one helper (`compute_vargottama_flags`) and one new boolean field on D1 planet objects. Backend remains the single source of astrological truth.

---

## Validation status (final run)

- **Logic:** Strict — Vargottama = (D1.sign_index == D9.sign_index) only. Rahu/Ketu excluded. Boolean only. Backend-only.
- **Test Case 1 (1985-08-20 07:30 New Delhi, Sun):** Expected Sun Vargottama (D1=4, D9=4). Engine returned D1=4 (Leo), D9=1 (Taurus) → `is_vargottama` false. **Expectation vs engine:** Test expected D9 Sun in Leo; engine gives D9 Sun in Taurus. Logic correctly returns false when signs differ.
- **Test Case 2 (1993-02-14 18:30 Mumbai, Saturn):** Expected Saturn not Vargottama. Engine returned `is_vargottama` false (boolean). **PASS.**
- **Global checks:** Rahu/Ketu false, boolean type, no false positives, API 200.
- **Status:** Logic is BPHS-compliant and strict. **Not LOCKED** per task (Test 1 assertion Sun === true failed because engine D9 Sun ≠ Leo). See `VARGOTTAMA_FINAL_VALIDATION_REPORT.md` for exact D1/D9 indices and recommendation.
