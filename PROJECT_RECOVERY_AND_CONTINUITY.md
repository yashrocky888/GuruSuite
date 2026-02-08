# Project Recovery & Continuity Manual — GuruSuite

**Single source of truth for recovery and continuation. One page. No fluff.**

---

## 1. WHAT THIS PROJECT IS (HIGH-LEVEL)

- **Name:** GuruSuite
- **Architecture rule:** Backend (FastAPI) is the single source of astrological truth.
- **Frontend (Next.js)** is render-only; NEVER computes astrology.
- All astrology logic is **BPHS + Swiss Ephemeris (Drik)**.

---

## 2. BACKEND STRUCTURE (WHERE LOGIC LIVES)

- **apps/guru-api/src/main.py** → FastAPI entrypoint
- **src/api/** → All API routes
- **src/jyotish/** → ALL astrology math lives here
  - **kundli_engine.py** → D1 base
  - **varga_engine.py** + **varga_drik.py** → ALL vargas (D1–D60)
  - **strength/shadbala.py** → BPHS Shadbala (Sthana, Dig, Kaala, etc.)
  - **transits/yoga_activation_engine.py** → Transit Activation logic
- No astrology math is allowed in frontend.

---

## 3. TRANSIT ACTIVATION ENGINE (CRITICAL)

**Philosophy (exact):**

> Dasha grants permission.  
> Transit gives timing.  
> Ashtakavarga decides comfort.

- **Natal Yoga** must exist.
- **Dasha Siege:** MD/AD lord must be a yoga participant.
- **Transit trigger:** conjunction / opposition / trikona.
- **Ashtakavarga Bindus** qualify comfort (Kashta / Sama / Shubha).
- Forecast supports long-range (default 100 years).

**API:** `GET /api/v1/yoga-activation`  
- `mode=summary`  
- `mode=forecast&years=100`

---

## 4. SHADBALA ENGINE STATUS (IMPORTANT)

- Shadbala follows **BPHS Chapter 27**.
- **Uchcha Bala** formula was FIXED:  
  **Uchcha Bala = (angular distance from debilitation) / 3**
- **Dig Bala** uses angular distance from weakest point.
- **Rahu/Ketu** do NOT have Dig Bala (BPHS-faithful).
- All recent Shadbala tests PASS after fix.

---

## 5. FRONTEND RULES (DO NOT BREAK)

- **services/api.ts** is the ONLY place API calls are defined.
- Base URL comes from **NEXT_PUBLIC_API_BASE_URL** (Cloud Run).
- Frontend never uses relative `/api/v1` paths directly.
- **Zustand (useBirthStore)** is the single source of birth details.
- If transit logic appears outside its card/page → it is a BUG.

---

## 6. DEPLOYMENT TRUTH (VERY IMPORTANT)

- **Cloud Run service name:** guru-api  
- **Region:** asia-south1  
- Deployment is **revision-based** (new image → new revision).
- If **backend logic changes** → MUST deploy new revision.
- If **no backend change** → DO NOT deploy.
- **Health endpoint:** GET /health (root).
- **yoga-activation** exists under /api/v1.

---

## 7. HOW TO RECOVER IF PROJECT IS RE-UPLOADED

1. Verify backend runs locally: `uvicorn src.main:app` (from apps/guru-api).
2. Verify `/health`, `/api/v1/kundli`, `/api/v1/location/search`.
3. Check if `/api/v1/yoga-activation` exists.
4. If backend logic changed → deploy to Cloud Run.
5. Set 100% traffic to latest revision.
6. Frontend: `rm -rf .next`, `npm install`, `npm run dev`.
7. Confirm frontend calls Cloud Run URL, not localhost API.

---

## 8. FINAL NON-NEGOTIABLE RULE

**If this document is ignored, any future work is invalid.**
