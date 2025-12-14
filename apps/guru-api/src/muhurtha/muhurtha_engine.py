"""
Phase 20: Muhurtha Engine (Main Orchestrator)

Orchestrates all Muhurtha calculations to find best time windows.
"""

from typing import Dict, List
from datetime import datetime, timedelta
import swisseph as swe

from src.muhurtha.panchanga_engine import compute_panchanga
from src.muhurtha.choghadiya_engine import compute_choghadiya
from src.muhurtha.muhurtha_rules import (
    evaluate_travel_muhurtha, evaluate_job_application_muhurtha,
    evaluate_marriage_talk_muhurtha, evaluate_investment_muhurtha,
    evaluate_property_purchase_muhurtha, evaluate_business_start_muhurtha,
    evaluate_medical_treatment_muhurtha, evaluate_spiritual_initiation_muhurtha,
    evaluate_naming_ceremony_muhurtha
)
from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.transit_ai.transit_context_builder import build_transit_context


TASK_EVALUATORS = {
    "travel": evaluate_travel_muhurtha,
    "job_application": evaluate_job_application_muhurtha,
    "marriage_talk": evaluate_marriage_talk_muhurtha,
    "investment": evaluate_investment_muhurtha,
    "property_purchase": evaluate_property_purchase_muhurtha,
    "business_start": evaluate_business_start_muhurtha,
    "medical_treatment": evaluate_medical_treatment_muhurtha,
    "spiritual_initiation": evaluate_spiritual_initiation_muhurtha,
    "naming_ceremony": evaluate_naming_ceremony_muhurtha,
    "buy_vehicle": evaluate_travel_muhurtha,  # Similar to travel
    "general": evaluate_job_application_muhurtha  # Default
}


def get_best_muhurtha(date: datetime, location: Dict, task: str, birth_chart: Dict, dasha: Dict, transit: Dict) -> Dict:
    """
    Phase 20: Get best Muhurtha time windows for a task.
    
    Args:
        date: Date for Muhurtha calculation
        location: Location dictionary
        task: Task type (travel, job_application, etc.)
        birth_chart: Birth chart
        dasha: Dasha data
        transit: Transit context
    
    Returns:
        Complete Muhurtha analysis with best windows
    """
    # Compute Panchanga
    panchanga = compute_panchanga(date, location)
    
    # Compute Choghadiya
    choghadiya = compute_choghadiya(date, location)
    
    # Get task evaluator
    evaluator = TASK_EVALUATORS.get(task, TASK_EVALUATORS["general"])
    
    # Evaluate task-specific Muhurtha
    task_evaluation = evaluator(panchanga, choghadiya, transit)
    
    # Analyze hour-by-hour windows
    best_windows = analyze_hourly_windows(date, panchanga, choghadiya, transit, task, task_evaluation)
    
    # Identify avoid windows
    avoid_windows = identify_avoid_windows(date, panchanga, choghadiya, transit)
    
    # Generate final advice
    final_advice = generate_final_advice(best_windows, avoid_windows, task_evaluation, task)
    
    return {
        "task": task,
        "date": date.strftime("%Y-%m-%d"),
        "overall_score": task_evaluation.get("score", 0),
        "overall_recommendation": task_evaluation.get("recommendation", ""),
        "best_windows": best_windows,
        "avoid_windows": avoid_windows,
        "panchanga": {
            "tithi": panchanga.get("tithi", {}).get("name", ""),
            "nakshatra": panchanga.get("nakshatra", {}).get("name", ""),
            "yoga": panchanga.get("yoga", {}).get("name", ""),
            "karana": panchanga.get("karana", {}).get("name", "")
        },
        "choghadiya_summary": {
            "best_segments": len(choghadiya.get("best_segments", [])),
            "avoid_segments": len(choghadiya.get("avoid_segments", []))
        },
        "final_advice": final_advice,
        "warnings": task_evaluation.get("warnings", [])
    }


def analyze_hourly_windows(date: datetime, panchanga: Dict, choghadiya: Dict, transit: Dict, task: str, task_eval: Dict) -> List[Dict]:
    """
    Phase 20: Analyze hour-by-hour windows to find best times.
    
    Args:
        date: Date
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit: Transit context
        task: Task type
        task_eval: Task evaluation
    
    Returns:
        List of best time windows
    """
    windows = []
    
    # Get best Choghadiya segments
    best_segments = choghadiya.get("best_segments", [])
    
    # Analyze each good Choghadiya segment
    for segment in best_segments[:3]:  # Top 3
        if segment.get("type") in ["excellent", "good"]:
            start_time = segment.get("start", "")
            end_time = segment.get("end", "")
            
            # Calculate score for this window
            window_score = calculate_window_score(start_time, end_time, panchanga, transit, task)
            
            if window_score >= 6:  # Only include high-scoring windows
                windows.append({
                    "start": start_time,
                    "end": end_time,
                    "score": window_score,
                    "reason": generate_window_reason(start_time, end_time, segment, panchanga, transit),
                    "choghadiya": segment.get("name", ""),
                    "type": segment.get("type", "")
                })
    
    # Sort by score (highest first)
    windows.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return windows[:3]  # Return top 3


def calculate_window_score(start_time: str, end_time: str, panchanga: Dict, transit: Dict, task: str) -> int:
    """
    Phase 20: Calculate score for a time window.
    
    Args:
        start_time: Start time string
        end_time: End time string
        panchanga: Panchanga data
        transit: Transit context
        task: Task type
    
    Returns:
        Score (0-10)
    """
    score = 5  # Base score
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    good_nakshatras = ["Rohini", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana"]
    if nakshatra_name in good_nakshatras:
        score += 2
    
    # Check Tithi
    tithi = panchanga.get("tithi", {})
    tithi_num = tithi.get("number", 0)
    if tithi_num in [1, 6, 11]:
        score += 1
    elif tithi_num in [4, 9, 14]:
        score -= 2
    
    # Check transit - Jupiter or Venus in favorable houses
    current_transits = transit.get("current_transits", {})
    if "Jupiter" in current_transits:
        jup_house = current_transits["Jupiter"].get("house_from_lagna", 0)
        if jup_house in [1, 5, 9, 10]:
            score += 2
    
    if "Venus" in current_transits:
        venus_house = current_transits["Venus"].get("house_from_lagna", 0)
        if venus_house in [1, 4, 5, 7, 9]:
            score += 1
    
    return max(0, min(10, score))


def generate_window_reason(start_time: str, end_time: str, segment: Dict, panchanga: Dict, transit: Dict) -> str:
    """
    Phase 20: Generate reason for a time window.
    
    Args:
        start_time: Start time
        end_time: End time
        segment: Choghadiya segment
        panchanga: Panchanga data
        transit: Transit context
    
    Returns:
        Reason string
    """
    reasons = []
    
    # Choghadiya reason
    chog_name = segment.get("name", "")
    if chog_name == "Amrit":
        reasons.append("Amrit Choghadiya - highly auspicious")
    elif chog_name in ["Labh", "Shubh"]:
        reasons.append(f"{chog_name} Choghadiya - favorable")
    
    # Nakshatra reason
    nakshatra = panchanga.get("nakshatra", {}).get("name", "")
    if nakshatra in ["Pushya", "Hasta", "Swati", "Anuradha"]:
        reasons.append(f"{nakshatra} Nakshatra - auspicious")
    
    # Transit reason
    current_transits = transit.get("current_transits", {})
    if "Jupiter" in current_transits:
        jup_house = current_transits["Jupiter"].get("house_from_lagna", 0)
        if jup_house in [1, 5, 9, 10]:
            reasons.append(f"Jupiter in {jup_house}th house - favorable")
    
    return "; ".join(reasons) if reasons else "Favorable planetary conditions"


def identify_avoid_windows(date: datetime, panchanga: Dict, choghadiya: Dict, transit: Dict) -> List[Dict]:
    """
    Phase 20: Identify windows to avoid.
    
    Args:
        date: Date
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit: Transit context
    
    Returns:
        List of avoid windows
    """
    avoid_windows = []
    
    # Rahu Kalam
    rahu_kalam = panchanga.get("rahu_kalam", {})
    if rahu_kalam:
        avoid_windows.append({
            "start": rahu_kalam.get("start", ""),
            "end": rahu_kalam.get("end", ""),
            "reason": "Rahu Kalam - inauspicious period",
            "severity": "high"
        })
    
    # Yama Gandam
    yama_gandam = panchanga.get("yama_gandam", {})
    if yama_gandam:
        avoid_windows.append({
            "start": yama_gandam.get("start", ""),
            "end": yama_gandam.get("end", ""),
            "reason": "Yama Gandam - inauspicious period",
            "severity": "high"
        })
    
    # Bad Choghadiya segments
    avoid_segments = choghadiya.get("avoid_segments", [])
    for segment in avoid_segments:
        avoid_windows.append({
            "start": segment.get("start", ""),
            "end": segment.get("end", ""),
            "reason": f"{segment.get('name', '')} Choghadiya - {segment.get('meaning', '')}",
            "severity": "medium"
        })
    
    return avoid_windows


def generate_final_advice(best_windows: List[Dict], avoid_windows: List[Dict], task_eval: Dict, task: str) -> str:
    """
    Phase 20: Generate final advice.
    
    Args:
        best_windows: Best time windows
        avoid_windows: Windows to avoid
        task_eval: Task evaluation
        task: Task type
    
    Returns:
        Final advice string
    """
    if not best_windows:
        return f"Today is not ideal for {task}. Consider postponing to a more favorable date."
    
    best_window = best_windows[0]
    start_time = best_window.get("start", "")
    end_time = best_window.get("end", "")
    
    advice = f"Proceed during {start_time} to {end_time} for maximum success. "
    advice += f"This window has a score of {best_window.get('score', 0)}/10. "
    advice += best_window.get("reason", "")
    
    if avoid_windows:
        advice += f" Avoid the following periods: "
        avoid_times = [f"{w.get('start')}-{w.get('end')}" for w in avoid_windows[:3]]
        advice += ", ".join(avoid_times)
    
    return advice

