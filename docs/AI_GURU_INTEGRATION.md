# AI Guru Integration — Guru Context JSON & Prediction

## Overview

The Guru Context is a **single JSON payload** built from verified backend math (Shadbala, Dasha, Transit Activation, Vargottama). It is sent to an AI (OpenAI/Gemini) with a fixed **Guru Persona** prompt so predictions respect Dasha permission, Shadbala strength, and Ashtakavarga comfort.

**Rule:** Truth > Appearance. If the Dasha is closed, the Guru must say the period is for rest, not action.

---

## How the JSON is Mapped to the AI Prompt

### 1. Natal Block

- **Source:** Kundli (D1) + D9 vargottama flags + yoga detection.
- **Content:** All yogas (name, planet/planets), D1 planet positions (sign_index, sign, house, degree, **is_vargottama**), ascendant.
- **Prompt use:** "Only predict what the Dasha permits" — yogas and dignities (e.g. Vargottama) describe natal potential; the AI must not overstate when Time Block says permission is dormant.

### 2. Strength Block

- **Source:** Shadbala at birth (verified BPHS).
- **Content:** Per-planet **rupas** (shadbala_in_rupas), total_virupas, status.
- **Prompt use:** RULE 2 — "Use Shadbala to determine the 'power' of the advice." Strong planets support bold action; weak ones suggest caution.

### 3. Time Block

- **Source:** Vimshottari Dasha + Transit Activation summary.
- **Content:** mahadasha_lord, antardasha_lord, **permission** (granted | dormant_or_closed), active_yogas_count, dasha_end.
- **Prompt use:** RULE 1 — "Only predict what the Dasha permits." If permission is dormant_or_closed, the Guru must emphasise rest and reflection, not major action.

### 4. Transit Block

- **Source:** Current planetary positions; houses computed from **Chandra Lagna** (Natal Moon) and from Lagna.
- **Content:** Per planet: sign_index, house_lagna, **house_chandra_lagna**, degree.
- **Prompt use:** Context for "key transits" — the AI names planets and reasons; Chandra Lagna house shows Moon-relative transit impact.

### 5. Quality Block

- **Source:** Ashtakavarga (Bhinnashtakavarga) — bindus in the house each planet is currently transiting.
- **Content:** Per planet: transit_house, **bindu** (0–8).
- **Prompt use:** RULE 3 — "Use Ashtakavarga bindus to determine 'comfort' or 'stress'." Kashta (low bindus) = difficulty; Sama = neutral; Shubha (high bindus) = favourable.

---

## Enabling Guru AI (Secure)

- **Secrets:** Never hardcode, log, or commit API keys. Use `.env` only; `.env` is in `.gitignore`.
- **Local:** `cd apps/guru-api` then `export OPENAI_API_KEY="your_key"` and `uvicorn src.main:app --reload`.
- **Cloud Run:** `gcloud run services update guru-api --region=asia-south1 --set-env-vars OPENAI_API_KEY=your_key` (same service, new revision, 100% traffic).
- **When key missing:** API returns HTTP 200 with `"message": "OPENAI_API_KEY not set"` plus `context` and `technical_breakdown` (no 500).
- **Model lock:** Predictions use **gpt-4o** only (best available API model; strict rule-following; low hallucination; no env override).

## API

- **Endpoint:** `POST /api/v1/predict`
- **Body:** `{ "birth_details": { "dob", "time", "lat", "lon", "timezone" }, "timescale": "daily" | "monthly" | "yearly" }`
- **Response (key set):** `{ "guidance": string, "context": GuruContextJSON, "technical_breakdown": { strength, time, quality } }`
- **Response (key missing):** `{ "message": "OPENAI_API_KEY not set", "context": ..., "technical_breakdown": ... }`

If `OPENAI_API_KEY` is not set, the API still returns **context** and **technical_breakdown**; the response includes **message** (`"OPENAI_API_KEY not set"`); the frontend shows that as the guidance text.

---

## Guru Persona (Prompt)

- **System:** "Act as an ancient Vedic Rishi. Use the provided JSON data only. RULE 1: Only predict what the Dasha permits. RULE 2: Use Shadbala to determine the 'power' of the advice. RULE 3: Use Ashtakavarga to determine 'comfort' or 'stress'. Speak technically but practically. Name the planets and the reasons. Truth over appearance."
- **User:** Timescale + full Guru Context JSON.

---

## Automation (Future)

The **predict** function in `src.api.prediction_routes` is standalone: it accepts `birth_details` and `timescale`, builds context, and calls the AI. It can be invoked from a Celery task or cron job for email subscription (e.g. daily/monthly digest) without duplicating logic.

---

## Files (Additive Only)

- **Backend:** `src/jyotish/ai/guru_payload.py` (build_guru_context), `src/api/prediction_routes.py` (POST /predict).
- **Frontend:** `app/dashboard/predictions/page.tsx` (tabs Daily | Monthly | Yearly, Guru Guidance Card, Technical Breakdown accordion).
- **Docs:** This file. No changes were made to varga_engine, shadbala, or yoga_activation_engine.
