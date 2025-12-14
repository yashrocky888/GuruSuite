"""
Phase 20: Yearly Prediction Engine

Generates 12-month blueprint and predictions.
"""

from typing import Dict, List
from datetime import datetime
import calendar

from src.yearly.yearly_transit_map import build_yearly_matrix
from src.yearly.solar_return_engine import compute_solar_return_chart
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.transit_ai.transit_context_builder import build_transit_context
import swisseph as swe


def generate_yearly_report(birth_details: Dict, year: int) -> Dict:
    """
    Phase 20: Generate complete yearly prediction report.
    
    Args:
        birth_details: Birth details
        year: Year for prediction
    
    Returns:
        Complete yearly report
    """
    # Build yearly transit matrix
    yearly_matrix = build_yearly_matrix(year)
    
    # Compute solar return (optional)
    solar_return = compute_solar_return_chart(birth_details, year)
    
    # Build birth chart
    birth_date = birth_details.get("birth_date")
    birth_time = birth_details.get("birth_time")
    birth_lat = birth_details.get("birth_latitude")
    birth_lon = birth_details.get("birth_longitude")
    timezone = birth_details.get("timezone", "UTC")
    
    if isinstance(birth_date, str):
        from datetime import datetime as dt
        birth_date_obj = dt.strptime(birth_date, "%Y-%m-%d").date()
    else:
        birth_date_obj = birth_date if hasattr(birth_date, 'year') else dt.strptime(str(birth_date), "%Y-%m-%d").date()
    
    hour, minute = map(int, birth_time.split(':'))
    birth_dt_local = dt.combine(birth_date_obj, dt.min.time().replace(hour=hour, minute=minute, second=0, microsecond=0))
    
    # Convert local time to UTC (Swiss Ephemeris requires UTC)
    from src.utils.timezone import local_to_utc
    birth_dt_utc = local_to_utc(birth_dt_local, timezone)
    
    birth_jd = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0,
        swe.GREG_CAL
    )
    
    natal_chart = generate_kundli(birth_jd, birth_lat, birth_lon)
    
    # Get Dasha
    moon_degree = natal_chart["Planets"]["Moon"]["degree"]
    dasha = calculate_vimshottari_dasha(birth_dt_utc, moon_degree)
    
    # Analyze themes
    themes = analyze_yearly_themes(yearly_matrix, natal_chart, dasha, year)
    
    # Identify major events
    major_events = identify_yearly_major_events(yearly_matrix, natal_chart, dasha)
    
    # Identify good and bad periods
    good_periods = identify_good_periods(yearly_matrix, natal_chart, dasha, year)
    bad_periods = identify_bad_periods(yearly_matrix, natal_chart, dasha, year)
    
    # Generate summary
    summary = generate_yearly_summary(themes, major_events, dasha)
    
    # Final advice
    final_advice = generate_yearly_advice(themes, good_periods, bad_periods, dasha)
    
    return {
        "year": year,
        "summary": summary,
        "themes": themes,
        "major_events": major_events,
        "good_periods": good_periods,
        "bad_periods": bad_periods,
        "final_advice": final_advice,
        "solar_return": solar_return.get("interpretation", "") if solar_return else ""
    }


def analyze_yearly_themes(yearly_matrix: Dict, natal_chart: Dict, dasha: Dict, year: int) -> Dict:
    """
    Phase 20: Analyze yearly themes for different life areas.
    
    Args:
        yearly_matrix: Yearly transit matrix
        natal_chart: Birth chart
        dasha: Dasha data
        year: Year
    
    Returns:
        Themes dictionary
    """
    themes = {}
    
    # Get mid-year transits (June)
    monthly_positions = yearly_matrix.get("monthly_positions", {})
    mid_year_transits = monthly_positions.get(6, {})  # June
    
    # Career theme
    if "Jupiter" in mid_year_transits:
        jup_sign = mid_year_transits["Jupiter"].get("sign", "")
        themes["career"] = f"Expansion in career due to Jupiter's favorable position in {jup_sign}. Focus on growth and recognition."
    elif "Saturn" in mid_year_transits:
        themes["career"] = "Career requires discipline and hard work. Saturn's influence brings long-term growth through patience."
    else:
        themes["career"] = "Stable career period with moderate growth opportunities."
    
    # Money theme
    if "Jupiter" in mid_year_transits:
        themes["money"] = "Financial stability and growth. Jupiter's blessings support wealth accumulation."
    elif "Saturn" in mid_year_transits:
        themes["money"] = "Financial discipline required. Saturn teaches lessons about money management and savings."
    else:
        themes["money"] = "Stable financial period. Maintain current approach."
    
    # Love theme
    if "Venus" in mid_year_transits:
        venus_sign = mid_year_transits["Venus"].get("sign", "")
        themes["love"] = f"Improvement in relationships as Venus transits favorable positions. Love and harmony increase."
    else:
        themes["love"] = "Moderate relationship period. Focus on communication and understanding."
    
    # Health theme
    if "Mars" in mid_year_transits:
        mars_sign = mid_year_transits["Mars"].get("sign", "")
        themes["health"] = f"Watch immunity during Mars transits. Take care of health, especially in April-June period."
    else:
        themes["health"] = "Generally good health. Regular checkups recommended."
    
    # Spirituality theme
    if "Jupiter" in mid_year_transits:
        themes["spirituality"] = "Very strong spiritual period during Jupiter transits. Excellent for meditation, learning, and growth."
    else:
        themes["spirituality"] = "Moderate spiritual growth. Continue regular practices."
    
    return themes


def identify_yearly_major_events(yearly_matrix: Dict, natal_chart: Dict, dasha: Dict) -> List[Dict]:
    """
    Phase 20: Identify major events for the year.
    
    Args:
        yearly_matrix: Yearly transit matrix
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        List of major events
    """
    events = []
    
    # Add events from yearly matrix
    matrix_events = yearly_matrix.get("major_events", [])
    events.extend(matrix_events)
    
    # Add retrogrades
    retrogrades = yearly_matrix.get("retrogrades", [])
    for retro in retrogrades[:3]:  # Top 3
        events.append({
            "date": retro.get("start", ""),
            "description": retro.get("description", ""),
            "impact": "moderate"
        })
    
    # Add eclipses
    eclipses = yearly_matrix.get("eclipses", [])
    for eclipse in eclipses:
        events.append({
            "date": eclipse.get("date", ""),
            "description": eclipse.get("description", ""),
            "impact": "high"
        })
    
    return events


def identify_good_periods(yearly_matrix: Dict, natal_chart: Dict, dasha: Dict, year: int) -> List[Dict]:
    """
    Phase 20: Identify good periods in the year.
    
    Args:
        yearly_matrix: Yearly transit matrix
        natal_chart: Birth chart
        dasha: Dasha data
        year: Year
    
    Returns:
        List of good periods
    """
    good_periods = []
    
    # Check for Jupiter in favorable positions
    monthly_positions = yearly_matrix.get("monthly_positions", {})
    
    for month in range(1, 13):
        if month in monthly_positions:
            planets = monthly_positions[month]
            if "Jupiter" in planets:
                jup_sign = planets["Jupiter"].get("sign", "")
                good_periods.append({
                    "start": f"{year}-{month:02d}-01",
                    "end": f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}",
                    "description": f"Jupiter in {jup_sign} - favorable period for growth and blessings",
                    "areas": ["career", "finances", "spirituality"]
                })
    
    return good_periods[:6]  # Top 6


def identify_bad_periods(yearly_matrix: Dict, natal_chart: Dict, dasha: Dict, year: int) -> List[Dict]:
    """
    Phase 20: Identify challenging periods in the year.
    
    Args:
        yearly_matrix: Yearly transit matrix
        natal_chart: Birth chart
        dasha: Dasha data
        year: Year
    
    Returns:
        List of bad periods
    """
    bad_periods = []
    
    # Check for Saturn in challenging positions
    monthly_positions = yearly_matrix.get("monthly_positions", {})
    
    for month in range(1, 13):
        if month in monthly_positions:
            planets = monthly_positions[month]
            if "Saturn" in planets:
                sat_sign = planets["Saturn"].get("sign", "")
                bad_periods.append({
                    "start": f"{year}-{month:02d}-01",
                    "end": f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}",
                    "description": f"Saturn in {sat_sign} - challenging period requiring patience",
                    "areas": ["career", "health"],
                    "advice": "Be patient, practice discipline, avoid hasty decisions"
                })
    
    # Add retrograde periods
    retrogrades = yearly_matrix.get("retrogrades", [])
    for retro in retrogrades:
        if retro.get("planet") in ["Saturn", "Mars"]:
            bad_periods.append({
                "start": retro.get("start", ""),
                "end": retro.get("end", ""),
                "description": retro.get("description", ""),
                "advice": "Review and reflect, avoid new beginnings"
            })
    
    return bad_periods[:6]  # Top 6


def generate_yearly_summary(themes: Dict, major_events: List[Dict], dasha: Dict) -> str:
    """
    Phase 20: Generate yearly summary.
    
    Args:
        themes: Yearly themes
        major_events: Major events
        dasha: Dasha data
    
    Returns:
        Summary string
    """
    summary = f"This year focuses on "
    
    # Identify primary theme
    primary_themes = []
    if themes.get("career", "").startswith("Expansion"):
        primary_themes.append("career consolidation")
    if themes.get("spirituality", "").startswith("Very strong"):
        primary_themes.append("spiritual growth")
    
    if primary_themes:
        summary += " and ".join(primary_themes)
    else:
        summary += "balanced growth across all areas"
    
    summary += ". "
    
    if major_events:
        summary += f"Major planetary shifts include {len(major_events)} significant events. "
    
    current_dasha = dasha.get("current_dasha", {})
    dasha_lord = current_dasha.get("dasha_lord", "Unknown")
    summary += f"Your {dasha_lord} Dasha period shapes the overall direction of the year."
    
    return summary


def generate_yearly_advice(themes: Dict, good_periods: List[Dict], bad_periods: List[Dict], dasha: Dict) -> str:
    """
    Phase 20: Generate final yearly advice.
    
    Args:
        themes: Yearly themes
        good_periods: Good periods
        bad_periods: Bad periods
        dasha: Dasha data
    
    Returns:
        Advice string
    """
    advice = "Yearly Guidance:\n\n"
    
    advice += "Focus Areas:\n"
    for area, theme_text in themes.items():
        advice += f"• {area.title()}: {theme_text}\n"
    
    if good_periods:
        advice += f"\nFavorable Periods: {len(good_periods)} periods identified for important activities.\n"
    
    if bad_periods:
        advice += f"\nChallenging Periods: {len(bad_periods)} periods requiring extra caution and patience.\n"
    
    advice += "\nOverall: This year brings opportunities for growth. Use favorable periods wisely and be patient during challenges."
    
    return advice

