#!/usr/bin/env python3
"""
Read-only Daily Prediction Audit for 2026-01-30 (Lunar Pulse).
Calls build_guru_context with calculation_date and same LLM flow as predict().
NO changes to astrology logic, prompt, or API.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Run from apps/guru-api
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.jyotish.ai.guru_payload import build_guru_context
from src.api.prediction_routes import GURU_SYSTEM_PROMPT
from src.config import settings
from src.ai.llm_client import LLMClient
from src.jyotish.dasha.vimshottari_engine import get_nakshatra_from_longitude

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

def main():
    birth_details = {
        "dob": "1981-05-20",
        "time": "06:30:00",
        "lat": 18.97,
        "lon": 72.82,
        "timezone": "Asia/Kolkata",
    }
    calculation_date = datetime(2026, 1, 30)
    timescale = "daily"

    # Build context for 2026-01-30 (read-only use of existing function)
    context = build_guru_context(
        birth_details,
        timescale=timescale,
        calculation_date=calculation_date,
    )

    # Same LLM flow as predict() — no logic change
    context_json = json.dumps(context, indent=2)
    user_prompt = f"""Timescale: {timescale}.
Provide concise guidance based ONLY on this JSON. If permission_granted is false, advise rest or restraint.
Mention current Dasha lords, Shadbala strength, and Ashtakavarga comfort where relevant.

Data:
{context_json}"""

    guidance = ""
    openai_key = getattr(settings, "openai_api_key", None)
    if openai_key:
        try:
            client = LLMClient()
            if client.mode == "openai" and client.openai_client:
                response = client.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": GURU_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=800,
                    temperature=0.5,
                )
                guidance = response.choices[0].message.content or ""
            else:
                guidance = "Guidance could not be generated (client not openai)."
        except Exception:
            guidance = "Guidance could not be generated. Use the technical breakdown below."
    else:
        guidance = "OPENAI_API_KEY not set — no AI guidance generated."

    # Derive transit Moon nakshatra from context (read-only)
    transit_moon_deg = (context.get("transit") or {}).get("Moon", {}).get("degree", 0)
    nak_info = get_nakshatra_from_longitude(transit_moon_deg)
    transit_moon_nakshatra = nak_info.get("name", "N/A")
    transit_moon_nak_lord = nak_info.get("lord", "N/A")

    natal_moon = (context.get("natal") or {}).get("planets_d1") or {}
    natal_moon = natal_moon.get("Moon") or {}
    natal_moon_sign = natal_moon.get("sign") or SIGN_NAMES[natal_moon.get("sign_index", 0)]

    transit_moon_data = (context.get("transit") or {}).get("Moon") or {}
    transit_moon_sign_idx = transit_moon_data.get("sign_index", 0)
    transit_moon_sign = SIGN_NAMES[transit_moon_sign_idx]
    house_from_moon = transit_moon_data.get("house_from_moon", "N/A")

    time_block = context.get("time") or {}
    mahadasha = time_block.get("mahadasha_lord", "N/A")
    antardasha = time_block.get("antardasha_lord", "N/A")
    permission = time_block.get("permission_granted", False)
    permission_str = "granted" if permission else "dormant_or_closed"

    # Quality: bindus per planet; Gemini = sign_index 2. Which house is Gemini? We report quality block as-is.
    quality = context.get("quality") or {}
    # Bindus for Gemini: in our context quality is per planet (transit_house, bindu). For "bindus for Gemini" we report planets transiting sign 2 (Gemini) or house 3 if Aries lagna. Task asks "Ashtakavarga bindus for Gemini" — report quality block and note Gemini.
    gemini_bindus_note = "Quality block is per-planet (transit_house, bindu). See quality in context for each planet."

    # Output path: repo root tests/logs (scripts -> guru-api -> apps -> GuruSuite)
    repo_root = Path(__file__).resolve().parents[3]
    out_dir = repo_root / "tests" / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "DAILY_PREDICTION_AUDIT_JAN30.md"

    # Cloud Run revision: not available at script run time; use placeholder
    revision = os.environ.get("K_REVISION", "local")

    md = f"""# Daily Prediction Test Audit (Lunar Pulse)

## 1️⃣ Test Metadata

| Field | Value |
|-------|--------|
| Date run | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |
| Backend revision | {revision} |
| Model used | gpt-4o |
| Timescale | Daily |
| Calculation date | 2026-01-30 |
| Birth | 1981-05-20 06:30, Mumbai (18.97, 72.82), Asia/Kolkata |

---

## 2️⃣ Raw Logic Snapshot (FROM CONTEXT)

| Item | Value |
|------|--------|
| Natal Moon sign | {natal_moon_sign} |
| Transit Moon sign (2026-01-30) | {transit_moon_sign} |
| House from Moon (Chandra Lagna) | {house_from_moon} |
| Nakshatra of transit Moon | {transit_moon_nakshatra} |
| Nakshatra lord | {transit_moon_nak_lord} |
| Current Mahadasha | {mahadasha} |
| Current Antardasha | {antardasha} |
| Dasha permission | {permission_str} |
| Ashtakavarga (quality) | {gemini_bindus_note} |

Quality block (bindus per planet): `{json.dumps(quality, indent=2)[:500]}...`

---

## 3️⃣ Guru's Exact Words

```
{guidance}
```

---

## 4️⃣ Logic Audit (PASS / FAIL / PARTIAL)

| Check | Result | Notes |
|-------|--------|--------|
| Moon House Logic | _AUDIT_ | Is Gemini (transit Moon sign) correctly treated as 8th from Moon? Does Guru advise caution/introspection? |
| Nakshatra Logic | _AUDIT_ | Is Ardra (or current nakshatra) referenced (storm, intensity)? Is Rahu-like intensity acknowledged? |
| Dasha Gate | _AUDIT_ | Is current Dasha named? Does advice respect permission status? |
| Ashtakavarga Reality | _AUDIT_ | Are bindus mentioned or implied? If bindus >5, is support acknowledged despite 8th house? |

---

## 5️⃣ Final Verdict

_One of: ✅ Guru-Grade Accurate | ⚠️ Partially Accurate | ❌ Logic Violation Detected_

Conclusion: _One-paragraph technical conclusion._

---

_Full guru_context (reference):_
```json
{context_json[:8000]}
```
"""

    out_file.write_text(md, encoding="utf-8")
    print(f"Written: {out_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
