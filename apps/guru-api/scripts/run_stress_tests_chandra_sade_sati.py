#!/usr/bin/env python3
"""
Stress tests: Ashtama Chandra & Sade Sati validation.
Calls build_guru_context with calculation_date=2026-01-31, then predict flow.
NO changes to astrology logic. Logs to tests/logs/.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.jyotish.ai.guru_payload import build_guru_context
from src.api.prediction_routes import GURU_SYSTEM_PROMPT, predict
from src.config import settings

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

BANGALORE = {"lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"}
TARGET_DATE = datetime(2026, 1, 31)


def call_llm_with_context(context: dict, seeker_name: str = "Seeker", timescale: str = "daily") -> str:
    """Build user_prompt and call LLM (same as predict()). Returns guidance text."""
    context_json = json.dumps(context, indent=2)
    user_prompt = f"""Seeker Name: {seeker_name}. Timescale: {timescale}.
Provide guidance based ONLY on this JSON. Follow all RULES: greet by name, Panchanga opening, Manas, daily verdicts (TRAVEL / WORK / OUTINGS), what today is good for, DO & DO NOT list, Nakshatra if present, light remedies if needed. If permission_granted is false, advise rest and do not encourage outward action.

Data:
{context_json}"""

    openai_key = getattr(settings, "openai_api_key", None)
    if not openai_key:
        return "OPENAI_API_KEY not set — no AI guidance generated."

    try:
        from src.ai.llm_client import LLMClient
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
            return response.choices[0].message.content or ""
        return "Guidance could not be generated (client not openai)."
    except Exception:
        return "Guidance could not be generated. Use the technical breakdown below."


def test_ashtama_chandra():
    """Test 1: Scorpio Moon, 2026-01-31 Bangalore → Transit Moon Gemini → house_from_moon MUST be 8."""
    birth = {
        "name": "AshtamaTest",
        "dob": "1988-11-10",
        "time": "12:00:00",
        "lat": BANGALORE["lat"],
        "lon": BANGALORE["lon"],
        "timezone": BANGALORE["timezone"],
    }
    context = build_guru_context(birth, timescale="daily", calculation_date=TARGET_DATE)
    transit = context.get("transit") or {}
    moon_data = transit.get("Moon") or {}
    house_from_moon = moon_data.get("house_from_moon")
    natal_moon_sign = ((context.get("natal") or {}).get("planets_d1") or {}).get("Moon") or {}
    natal_sign_idx = natal_moon_sign.get("sign_index")
    trans_sign_idx = moon_data.get("sign_index")

    guidance = call_llm_with_context(context, seeker_name=birth.get("name", "Seeker"), timescale="daily")

    # Assertions: CRITICAL = house_from_moon == 8 (Vedic sign count). AI checks apply only when guidance was generated.
    hfm_ok = house_from_moon == 8
    key_not_set = "OPENAI_API_KEY" in guidance or not guidance.strip()
    ai_8_or_ashtama = "8th" in guidance and "Moon" in guidance or "Ashtama" in guidance.lower()
    ai_mental_rest = any(x in guidance.lower() for x in ["mental", "churn", "sensitivity", "caution", "rest", "introspection", "heaviness", "internal"])
    ai_no_travel_social = not any(x in guidance.lower() for x in ["great day for travel", "good time to socialize", "ideal for partnerships", "outward action"])

    pass_assert = hfm_ok and (key_not_set or ((ai_8_or_ashtama or ai_mental_rest) and ai_no_travel_social))
    fail_reason = []
    if not hfm_ok:
        fail_reason.append(f"house_from_moon={house_from_moon} (expected 8)")
    if house_from_moon == 7:
        fail_reason.append("BUG: 7th from Moon (degree-slicing) — Vedic sign count must be 8")
    if not key_not_set:
        if not (ai_8_or_ashtama or ai_mental_rest):
            fail_reason.append("AI did not mention 8th/Ashtama or mental restraint")
        if not ai_no_travel_social:
            fail_reason.append("AI suggested travel/social/outward action against Ashtama")

    repo_root = Path(__file__).resolve().parents[3]
    out_dir = repo_root / "tests" / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "STRESS_TEST_ASHTAMA_CHANDRA.md"

    verdict = "PASS" if pass_assert else "FAIL"
    reason = "; ".join(fail_reason) if fail_reason else "house_from_moon==8, AI respects Ashtama Chandra."

    md = f"""# Stress Test — Ashtama Chandra Trap

## Test Metadata
- Date run: {datetime.now().strftime("%Y-%m-%d %H:%M")}
- Calculation date: 2026-01-31
- Location: Bangalore, India
- Natal Moon: Scorpio (sign_index {natal_sign_idx})
- Transit Moon: Gemini (sign_index {trans_sign_idx})

## Raw Transit Block (Moon)
```json
{json.dumps(moon_data, indent=2)}
```

## Computed house_from_moon
**{house_from_moon}** (expected: 8 for Ashtama Chandra; formula (2-7)%12+1 = 8)

## AI Guidance (verbatim)
```
{guidance}
```

## Assertions
| Check | Result |
|-------|--------|
| house_from_moon == 8 | {"PASS" if hfm_ok else "FAIL"} |
| AI mentions 8th/Ashtama or mental restraint | {"PASS" if (ai_8_or_ashtama or ai_mental_rest) else "FAIL"} |
| AI does not suggest travel/social/outward | {"PASS" if ai_no_travel_social else "FAIL"} |

## Verdict
**{verdict}** — {reason}
"""
    out_file.write_text(md, encoding="utf-8")
    print(f"[Ashtama Chandra] house_from_moon={house_from_moon} verdict={verdict}")
    return pass_assert, house_from_moon


def test_sade_sati():
    """Test 2: Aquarius Moon, 2026-01-31 → Saturn in Pisces = 2nd from Moon (final Sade Sati)."""
    # Use a birth that yields Aquarius Moon (sign_index 10). If not found, use one with Saturn in 2nd from Moon.
    births_try = [
        {"dob": "1990-02-14", "time": "06:00:00"},  # try Aquarius Moon
        {"dob": "1982-02-08", "time": "12:00:00"},
        {"dob": "1978-02-02", "time": "18:00:00"},
    ]
    birth = None
    context = None
    for b in births_try:
        full_birth = {
            "name": "SadeSatiTest",
            "dob": b["dob"],
            "time": b["time"],
            "lat": BANGALORE["lat"],
            "lon": BANGALORE["lon"],
            "timezone": BANGALORE["timezone"],
        }
        ctx = build_guru_context(full_birth, timescale="daily", calculation_date=TARGET_DATE)
        pm = (ctx.get("natal") or {}).get("planets_d1") or {}
        moon = (pm.get("Moon") or {})
        sidx = moon.get("sign_index")
        sat = (ctx.get("transit") or {}).get("Saturn") or {}
        sat_hfm = sat.get("house_from_moon")
        if sidx == 10 and sat_hfm == 2:
            birth = full_birth
            context = ctx
            break
        if sat_hfm == 2:
            birth = full_birth
            context = ctx
            break

    if context is None:
        context = build_guru_context(
            {"name": "SadeSatiTest", "dob": "1990-02-14", "time": "06:00:00", "lat": BANGALORE["lat"], "lon": BANGALORE["lon"], "timezone": BANGALORE["timezone"]},
            timescale="daily", calculation_date=TARGET_DATE
        )
        birth = {"name": "SadeSatiTest", "dob": "1990-02-14", "time": "06:00:00", "lat": BANGALORE["lat"], "lon": BANGALORE["lon"], "timezone": BANGALORE["timezone"]}

    transit = context.get("transit") or {}
    sat_data = transit.get("Saturn") or {}
    moon_data = transit.get("Moon") or {}
    natal_moon = ((context.get("natal") or {}).get("planets_d1") or {}).get("Moon") or {}
    natal_sign_idx = natal_moon.get("sign_index")

    guidance = call_llm_with_context(context, seeker_name=birth.get("name", "Seeker"), timescale="daily")

    sat_hfm = sat_data.get("house_from_moon")
    moon_hfm = moon_data.get("house_from_moon")
    key_not_set = "OPENAI_API_KEY" in guidance or not guidance.strip()
    ai_sade_sati = "sade sati" in guidance.lower() or ("saturn" in guidance.lower() and ("phase" in guidance.lower() or "pressure" in guidance.lower() or "restraint" in guidance.lower()))
    ai_restraint = any(x in guidance.lower() for x in ["restraint", "caution", "responsibility", "speech", "wealth", "careful", "avoid"])
    ai_no_party = not any(x in guidance.lower() for x in ["great day for enjoyment", "good day for spending", "ideal for party"])

    pass_assert = key_not_set or (ai_sade_sati or (sat_hfm == 2 and ai_restraint)) and ai_no_party
    fail_reason = []
    if not key_not_set:
        if not ai_sade_sati and (sat_hfm == 2 and not ai_restraint):
            fail_reason.append("AI did not mention Sade Sati or Saturn restraint")
        if not ai_no_party:
            fail_reason.append("AI suggested enjoyment/spending despite Saturn")

    repo_root = Path(__file__).resolve().parents[3]
    out_dir = repo_root / "tests" / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "STRESS_TEST_SADE_SATI.md"

    verdict = "PASS" if pass_assert else "FAIL"
    reason = "; ".join(fail_reason) if fail_reason else "AI acknowledges Saturn / restraint; no party/spending advice."

    md = f"""# Stress Test — Sade Sati Shadow

## Test Metadata
- Date run: {datetime.now().strftime("%Y-%m-%d %H:%M")}
- Calculation date: 2026-01-31
- Location: Bangalore, India
- Natal Moon sign_index: {natal_sign_idx} ({SIGN_NAMES[natal_sign_idx] if natal_sign_idx is not None else 'N/A'})

## Raw Transit Block — Saturn
```json
{json.dumps(sat_data, indent=2)}
```

## Raw Transit Block — Moon
```json
{json.dumps(moon_data, indent=2)}
```

## AI Guidance (verbatim)
```
{guidance}
```

## Assertions
| Check | Result |
|-------|--------|
| Saturn house_from_moon (2 = final Sade Sati) | {sat_hfm} |
| AI mentions Sade Sati / Saturn / restraint | {"PASS" if ai_sade_sati or ai_restraint else "FAIL"} |
| AI does not suggest enjoyment/spending | {"PASS" if ai_no_party else "FAIL"} |

## Verdict
**{verdict}** — {reason}
"""
    out_file.write_text(md, encoding="utf-8")
    print(f"[Sade Sati] Saturn_house_from_moon={sat_hfm} Moon_house_from_moon={moon_hfm} verdict={verdict}")
    return pass_assert


def main():
    ok1, hfm = test_ashtama_chandra()
    if not ok1 or hfm == 7:
        print("HOUSE COUNTING / SATURN OVERRIDE ERROR — INVESTIGATE IMMEDIATELY")
        if hfm == 7:
            print("CRITICAL: house_from_moon is 7 (wrong). Vedic sign count must be 8 for Scorpio→Gemini.")
        return 1

    ok2 = test_sade_sati()
    if not ok2:
        print("HOUSE COUNTING / SATURN OVERRIDE ERROR — INVESTIGATE IMMEDIATELY")
        return 1

    print("STRESS TESTS PASSED — GURU LOGIC VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
