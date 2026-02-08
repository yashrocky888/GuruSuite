# API Change Audit and Deploy — Final Integrity Check

## STEP 1 — Backend Change Audit (MANDATORY)

**Answer: (B) BACKEND LOGIC CHANGES WERE MADE**

### File and exact change

| File | Change type | Exact change |
|------|-------------|--------------|
| `apps/guru-api/src/jyotish/strength/shadbala.py` | Formula (math) | In `calculate_uchcha_bala` (lines ~300–315): **Before:** `uchcha = (180.0 - angular_distance) / 3.0` **After:** `uchcha = angular_distance / 3.0` (BPHS Ch 27: Uchcha Bala = one-third of angular distance from debilitation point; comment updated accordingly). |

No other backend logic changes (no changes to yoga_activation_engine, yoga_activation_routes, transit_routes, main.py, or helpers for the purpose of making tests pass). Cosmetic refactors, comments, and formatting were not counted.

---

## STEP 2 — Deployment Rule

Because the answer in STEP 1 is (B), a new Cloud Run revision for the **same** service (`guru-api`), **same** region, with **100%** traffic to the new revision is required. No new service; no traffic split.

---

## STEP 3 — Post-Deploy Verification

- **Cloud Run service name:** `guru-api`
- **Revision ID:** `guru-api-00132-5wf`
- **Traffic percentage:** 100% (new revision)
- **Region:** `asia-south1`
- **Service URL:** https://guru-api-660206747784.asia-south1.run.app

**Verification calls (HTTP status only):**

| Endpoint | HTTP status |
|----------|-------------|
| GET /health | 200 |
| GET /api/v1/kundli (with dob, time, lat, lon, timezone) | 200 |
| GET /api/v1/location/search?q=bangalore | 200 |
| GET /api/v1/yoga-activation (summary; with dob, time, lat, lon) | 200 |
| GET /api/v1/yoga-activation?mode=forecast&years=100 (with dob, time, lat, lon) | 200 |

All required verification endpoints return **200**.

---

## STEP 4 — Final Declaration

✔ **API UPDATED — CLOUD DEPLOY COMPLETED AND VERIFIED**

