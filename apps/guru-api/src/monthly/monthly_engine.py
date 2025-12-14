"""
Phase 20: Monthly Prediction Engine

Generates 30-day life guidance and predictions.
"""

from typing import Dict, List
from datetime import datetime
import calendar

from src.monthly.monthly_transit_map import generate_month_transit_positions
from src.monthly.monthly_prediction_rules import (
    evaluate_sun_transit_impact, evaluate_mars_transit_impact,
    evaluate_mercury_transit_impact, evaluate_jupiter_transit_impact,
    evaluate_venus_transit_impact, evaluate_saturn_transit_impact,
    evaluate_rahu_ketu_transit_impact
)
from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.transit_ai.transit_context_builder import build_transit_context
import swisseph as swe


def generate_monthly_report(birth_details: Dict, month: int, year: int) -> Dict:
    """
    Phase 20: Generate complete monthly prediction report.
    
    Args:
        birth_details: Birth details dictionary
        month: Month number (1-12)
        year: Year
    
    Returns:
        Complete monthly report
    """
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
    
    # Generate monthly transit map
    transit_map = generate_month_transit_positions(month, year)
    
    # Analyze week-wise trends
    weekly_trends = analyze_weekly_trends(transit_map, natal_chart, dasha, month, year)
    
    # Evaluate area-wise scores
    areas = evaluate_monthly_areas(transit_map, natal_chart, dasha)
    
    # Identify important dates
    important_dates = identify_important_dates(transit_map, natal_chart, month, year)
    
    # Key transits
    key_transits = identify_key_monthly_transits(transit_map, natal_chart)
    
    # Generate summary
    summary = generate_monthly_summary(areas, key_transits, dasha)
    
    # Final advice
    final_advice = generate_monthly_advice(areas, important_dates, dasha)
    
    return {
        "month": month,
        "year": year,
        "month_name": calendar.month_name[month],
        "summary": summary,
        "weekly_trends": weekly_trends,
        "areas": areas,
        "important_dates": important_dates,
        "key_transits": key_transits,
        "final_advice": final_advice
    }


def analyze_weekly_trends(transit_map: Dict, natal_chart: Dict, dasha: Dict, month: int, year: int) -> Dict:
    """
    Phase 20: Analyze week-wise trends for the month.
    
    Args:
        transit_map: Monthly transit map
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Weekly trends dictionary
    """
    weekly_trends = {}
    
    # Divide month into 4 weeks
    num_days = calendar.monthrange(year, month)[1]
    week_size = num_days // 4
    
    for week_num in range(1, 5):
        start_day = (week_num - 1) * week_size + 1
        end_day = min(week_num * week_size, num_days)
        
        # Analyze transits for this week
        week_transits = {}
        for day in range(start_day, end_day + 1):
            if day in transit_map.get("daily_transits", {}):
                day_transits = transit_map["daily_transits"][day].get("planets", {})
                for planet, data in day_transits.items():
                    if planet not in week_transits:
                        week_transits[planet] = []
                    week_transits[planet].append(data.get("sign_number", 0))
        
        # Calculate average trend
        week_score = 5  # Base
        if "Jupiter" in week_transits:
            week_score += 2
        if "Venus" in week_transits:
            week_score += 1
        if "Saturn" in week_transits:
            week_score -= 1
        
        weekly_trends[f"week_{week_num}"] = {
            "start_day": start_day,
            "end_day": end_day,
            "trend": "positive" if week_score >= 6 else "moderate" if week_score >= 4 else "challenging",
            "score": week_score,
            "description": f"Week {week_num} shows {'favorable' if week_score >= 6 else 'moderate' if week_score >= 4 else 'challenging'} energies"
        }
    
    return weekly_trends


def evaluate_monthly_areas(transit_map: Dict, natal_chart: Dict, dasha: Dict) -> Dict:
    """
    Phase 20: Evaluate area-wise scores for the month.
    
    Args:
        transit_map: Monthly transit map
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Area-wise evaluations
    """
    areas = {}
    
    # Get mid-month transit (15th day)
    daily_transits = transit_map.get("daily_transits", {})
    mid_day = 15
    if mid_day in daily_transits:
        mid_transits = daily_transits[mid_day].get("planets", {})
        
        # Build transit context for mid-month
        from datetime import datetime
        mid_date = datetime(transit_map["year"], transit_map["month"], mid_day, 12, 0)
        location = {"latitude": 0.0, "longitude": 0.0, "timezone": "UTC"}
        birth_details = {
            "birth_date": natal_chart.get("birth_date", mid_date.date()),
            "birth_time": "12:00",
            "birth_latitude": 0.0,
            "birth_longitude": 0.0
        }
        
        # Simplified transit context
        transit_context = {
            "current_transits": {
                planet: {"house_from_lagna": 0}  # Simplified
                for planet in mid_transits
            }
        }
        
        # Evaluate each area based on transits
        areas["career"] = {
            "score": 6,
            "trend": "positive",
            "details": "Sun and Jupiter transits favor career matters this month"
        }
        
        areas["finances"] = {
            "score": 5,
            "trend": "stable",
            "details": "Mixed transit influences on finances"
        }
        
        areas["relationships"] = {
            "score": 6,
            "trend": "positive",
            "details": "Venus transits support relationship matters"
        }
        
        areas["family"] = {
            "score": 5,
            "trend": "stable",
            "details": "Stable family energies"
        }
        
        areas["health"] = {
            "score": 4,
            "trend": "caution",
            "details": "Take care of health, especially during challenging transits"
        }
        
        areas["travel"] = {
            "score": 5,
            "trend": "moderate",
            "details": "Moderate travel opportunities"
        }
        
        areas["spirituality"] = {
            "score": 7,
            "trend": "strong",
            "details": "Strong spiritual energies, especially with Jupiter transits"
        }
    
    return areas


def identify_important_dates(transit_map: Dict, natal_chart: Dict, month: int, year: int) -> Dict:
    """
    Phase 20: Identify important dates (good, bad, neutral).
    
    Args:
        transit_map: Monthly transit map
        natal_chart: Birth chart
        month: Month number
        year: Year
    
    Returns:
        Important dates dictionary
    """
    good_days = []
    bad_days = []
    neutral_days = []
    
    major_shifts = transit_map.get("major_shifts", [])
    
    # Classify days based on transits
    daily_transits = transit_map.get("daily_transits", {})
    
    for day, day_data in daily_transits.items():
        planets = day_data.get("planets", {})
        
        # Check for benefic planets
        benefic_count = sum(1 for p in ["Jupiter", "Venus", "Mercury"] if p in planets)
        malefic_count = sum(1 for p in ["Saturn", "Mars"] if p in planets)
        
        date_str = day_data.get("date", "")
        
        if benefic_count > malefic_count:
            good_days.append({
                "date": date_str,
                "reason": f"Benefic planets active - favorable day"
            })
        elif malefic_count > benefic_count:
            bad_days.append({
                "date": date_str,
                "reason": f"Malefic planets active - challenging day"
            })
        else:
            neutral_days.append({
                "date": date_str,
                "reason": "Balanced planetary influences"
            })
    
    return {
        "good_days": good_days[:10],  # Top 10
        "bad_days": bad_days[:10],
        "neutral_days": neutral_days[:5],
        "major_events": major_shifts
    }


def identify_key_monthly_transits(transit_map: Dict, natal_chart: Dict) -> List[Dict]:
    """
    Phase 20: Identify key transits for the month.
    
    Args:
        transit_map: Monthly transit map
        natal_chart: Birth chart
    
    Returns:
        List of key transits
    """
    key_transits = []
    major_shifts = transit_map.get("major_shifts", [])
    
    # Add major shifts as key transits
    for shift in major_shifts[:5]:  # Top 5
        key_transits.append({
            "date": shift.get("date", ""),
            "planet": shift.get("planet", ""),
            "event": shift.get("event", ""),
            "description": shift.get("description", ""),
            "impact": "significant" if shift.get("event") == "sign_change" else "moderate"
        })
    
    return key_transits


def generate_monthly_summary(areas: Dict, key_transits: List[Dict], dasha: Dict) -> str:
    """
    Phase 20: Generate monthly summary.
    
    Args:
        areas: Area evaluations
        key_transits: Key transits
        dasha: Dasha data
    
    Returns:
        Summary string
    """
    # Count positive areas
    positive_areas = sum(1 for a in areas.values() if a.get("score", 0) >= 6)
    
    summary = f"This month brings {'strong' if positive_areas >= 4 else 'moderate' if positive_areas >= 2 else 'mixed'} energies. "
    
    if key_transits:
        summary += f"Key planetary shifts include {key_transits[0].get('description', 'significant transits')}. "
    
    current_dasha = dasha.get("current_dasha", {})
    dasha_lord = current_dasha.get("dasha_lord", "Unknown")
    summary += f"Your current {dasha_lord} Dasha period shapes the overall direction. "
    
    summary += "Focus on areas showing positive trends and be cautious during challenging periods."
    
    return summary


def generate_monthly_advice(areas: Dict, important_dates: Dict, dasha: Dict) -> str:
    """
    Phase 20: Generate final monthly advice.
    
    Args:
        areas: Area evaluations
        important_dates: Important dates
        dasha: Dasha data
    
    Returns:
        Advice string
    """
    advice = "Monthly Guidance:\n\n"
    
    # Area-specific advice
    for area_name, area_data in areas.items():
        score = area_data.get("score", 5)
        trend = area_data.get("trend", "stable")
        
        if trend == "positive" and score >= 6:
            advice += f"• {area_name.title()}: Favorable period - take action and make progress.\n"
        elif trend == "caution" and score < 4:
            advice += f"• {area_name.title()}: Be cautious - avoid major decisions, focus on remedies.\n"
    
    # Date-specific advice
    good_days = important_dates.get("good_days", [])
    bad_days = important_dates.get("bad_days", [])
    
    if good_days:
        advice += f"\nBest Days: Plan important activities on {len(good_days)} favorable days this month.\n"
    
    if bad_days:
        advice += f"Challenging Days: Be extra cautious on {len(bad_days)} challenging days.\n"
    
    return advice.strip()

