"""
Yoga Transit Activation API routes.

GET /api/v1/yoga-activation
- mode=summary: current activation list (Active / Dormant yogas, bindus, quality)
- mode=forecast: next N-year activation windows (default years=100)
Response: transit_activation, forecast, philosophy, error (strict shape).
"""

from fastapi import APIRouter, Query
from typing import Optional

from src.jyotish.transits.yoga_activation_engine import (
    evaluate_current_activation,
    evaluate_transit_activation_forecast,
)

router = APIRouter()

# Architectural principle (locked): UI tooltip and backend contract
PHILOSOPHY = "Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort."


@router.get("/yoga-activation")
def get_yoga_activation(
    dob: str = Query(..., description="Date of birth YYYY-MM-DD"),
    time: str = Query(..., description="Time of birth HH:MM"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    timezone: str = Query("Asia/Kolkata", description="Timezone"),
    mode: str = Query("summary", description="summary | forecast"),
    years: Optional[int] = Query(100, description="Forecast years (forecast only, default 100)"),
):
    """
    Yoga Transit Activation (BPHS-correct). Secondary information only.
    Transit never creates/alters natal yogas. Philosophy: Dasha grants permission;
    transit gives timing; Ashtakavarga decides comfort.
    """
    try:
        if mode == "forecast":
            forecast = evaluate_transit_activation_forecast(
                dob=dob, time=time, lat=lat, lon=lon, timezone=timezone, years=years or 100
            )
            return {
                "transit_activation": [],
                "forecast": forecast,
                "philosophy": PHILOSOPHY,
                "error": None,
            }
        # mode=summary (default)
        transit_activation = evaluate_current_activation(
            dob=dob, time=time, lat=lat, lon=lon, timezone=timezone
        )
        return {
            "transit_activation": transit_activation,
            "forecast": [],
            "philosophy": PHILOSOPHY,
            "error": None,
        }
    except Exception as e:
        return {
            "transit_activation": [],
            "forecast": [],
            "philosophy": PHILOSOPHY,
            "error": str(e),
        }
