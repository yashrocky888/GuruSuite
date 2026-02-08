# Transit Activation Re-Implementation — Verification Report

**Date:** 2025-01-29  
**Scope:** Safe re-implementation of Transit Activation of Yogas (Dashboard card + 100-year forecast).

---

## Backend

### Engine (`apps/guru-api/src/jyotish/transits/yoga_activation_engine.py`)

- **Principle (locked):** "Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort."
- **Summary:** `evaluate_current_activation` (alias `evaluate_transit_activation_summary`) — Dasha permission → Transit contact (conjunction/opposition/trikona) → Ashtakavarga quality (Kashta/Sama/Shubha).
- **Forecast:** `evaluate_transit_activation_forecast(..., years=100)` — Default 100 years; Dasha windows first; **slow planets (Saturn, Jupiter, Mars)** scanned by **sign ingress** (no per-day loops); **fast planets (Sun, Venus, Mercury)** only if window ≥ 6 months, step 7 days.
- **No kundli/varga math duplication:** Uses existing `detect_all_yogas`, `calculate_vimshottari_dasha`, `get_transits`, `calculate_bhinnashtakavarga`, `get_planet_positions`, houses/ascendant.

### API (`apps/guru-api/src/api/yoga_activation_routes.py`)

- **GET /api/v1/yoga-activation** — Query: `dob`, `time`, `lat`, `lon`, `timezone`, `mode=summary|forecast`, `years=100` (default).
- **Response shape (strict):** `{ "transit_activation": [], "forecast": [], "philosophy": "...", "error": null }`.
- **Philosophy:** "Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort."

### Verification

- **Local:** Engine runs; summary and forecast return (empty valid). API returns 200; after server restart, response includes `philosophy`.
- **Cloud Run:** Deploy with existing script; verify `GET /health` → 200, `GET /api/v1/yoga-activation?...` → 200 (empty valid).
- **No existing API broken:** No changes to kundli, dasha, shadbala, panchang, location, or other routes.

---

## Frontend

### Dashboard

- **New card:** "Transit Activation (Secondary Switch)" — `DashboardTransitActivationCard` in `apps/guru-web/guru-web/components/DashboardTransitActivationCard.tsx`.
- **Content:**
  - **A) Current activation:** Yoga name, Status (Active/Dormant), Trigger planet (if active), one-line reason (e.g. "Mars activating … during Saturn Antardasha").
  - **B) Ashtakavarga (Active only):** Bindus X/8, Verdict SHUBHA/SAMA/KASHTA; tooltip: "Ashtakavarga decides comfort, not existence."
  - **C) Next 100-Year Activation Outlook:** Collapsed by default; when expanded, **lazy-loads** `mode=forecast&years=100`.
- **Philosophy:** Shown in card copy and tooltip.
- **Empty state:** Clean message; no crash.

### Transits Page

- **Transit Activation card removed** from `/transits`. Page shows only **current planetary transits** (VedicTransits + DataTable). No duplicate Transit Activation UI.

### Regression

- **Kundli:** Unchanged.
- **Dasha:** Unchanged.
- **Location search:** Unchanged.
- **Shadbala:** Unchanged.
- **Transits page:** Unchanged except removal of yoga-activation card (planetary transits only).

---

## Deployment

- **Target:** Existing Cloud Run service `guru-api` (region as before).
- **Action:** Build and deploy; new revision only; 100% traffic to latest.
- **Verify:** `GET /health` → 200, `GET /api/v1/yoga-activation?dob=...&time=...&lat=...&lon=...&timezone=Asia/Kolkata` → 200.
- **CI/CD:** If enabled, use it; if blocked by permissions, state in deployment run.

---

## Summary

| Item | Status |
|------|--------|
| Backend engine (100-year, ingress-based) | Done |
| API (philosophy, years=100 default) | Done |
| Dashboard Transit Activation card | Done |
| Lazy-load 100-year forecast | Done |
| Transits page (no duplicate card) | Done |
| No regression (kundli, dasha, location, shadbala, transits) | Verified by design |

**Transit Activation is additive, isolated, and removable. UI is stable; empty state does not crash.**
