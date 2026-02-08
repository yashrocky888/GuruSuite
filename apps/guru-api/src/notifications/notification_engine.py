"""
Phase 10: Notification Engine

Generates daily predictions for all users and stores them as notifications.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import swisseph as swe
import json

from src.db.database import SessionLocal
from src.db.models import User, BirthDetail, Notification
from src.ai.interpreter.daily_interpreter import interpret_daily, interpret_morning
from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.jyotish.panchang_engine import generate_panchang
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.jyotish.daily.daily_engine import compute_daily
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses, get_ayanamsa
from src.utils.converters import degrees_to_sign, normalize_degrees


def build_user_context(birth_detail: BirthDetail, current_jd: float) -> Dict:
    """
    Phase 10: Build complete astrological context for a user's birth data.
    
    Args:
        birth_detail: User's birth detail record
        current_jd: Current Julian Day for predictions
    
    Returns:
        Complete astrological context dictionary
    """
    # Parse birth date and time
    birth_dt = birth_detail.birth_date
    birth_time_str = birth_detail.birth_time  # HH:MM format
    hour, minute = map(int, birth_time_str.split(':'))
    
    # Create birth datetime
    birth_datetime = datetime.combine(birth_dt, datetime.min.time().replace(hour=hour, minute=minute))
    
    # Calculate birth Julian Day
    birth_jd = swe.julday(
        birth_datetime.year, birth_datetime.month, birth_datetime.day,
        birth_datetime.hour + birth_datetime.minute / 60.0,
        swe.GREG_CAL
    )
    
    # Generate Kundli
    kundli = generate_kundli(birth_jd, birth_detail.birth_latitude, birth_detail.birth_longitude)
    
    # Get planet positions for dasha
    birth_planets = get_planet_positions(birth_jd)
    moon_degree = birth_planets["Moon"]
    
    # Calculate Dasha
    dasha = calculate_vimshottari_dasha(birth_datetime, moon_degree)
    
    # Generate Panchang for current date
    current_datetime = datetime.now()
    panchang = generate_panchang(current_jd, current_datetime, birth_detail.birth_latitude, birth_detail.birth_longitude)
    
    # Prepare planets and houses for yoga detection
    planets = {}
    for p, d in kundli['Planets'].items():
        if p in ["Rahu", "Ketu"]:
            continue
        sign_num, _ = degrees_to_sign(d['degree'])
        asc_deg = kundli['Ascendant']['degree']
        rel_pos = (d['degree'] - asc_deg) % 360
        house_num = int(rel_pos / 30) + 1
        if house_num > 12:
            house_num = 1
        planets[p] = {'degree': d['degree'], 'sign': sign_num, 'house': house_num}
    
    houses = []
    asc_sign, _ = degrees_to_sign(kundli['Ascendant']['degree'])
    houses.append({'house': 1, 'degree': kundli['Ascendant']['degree'], 'sign': asc_sign})
    for h in kundli['Houses']:
        sign_num, _ = degrees_to_sign(h['degree'])
        houses.append({'house': h['house'], 'degree': h['degree'], 'sign': sign_num})
    
    # Detect Yogas
    yogas = detect_all_yogas(planets, houses)
    
    # Calculate Daily Impact
    daily = compute_daily(birth_jd, current_jd, birth_detail.birth_latitude, birth_detail.birth_longitude, birth_datetime)
    
    # Combine all data
    combined = {
        "kundli": {
            "ascendant": kundli["Ascendant"],
            "planets": kundli["Planets"],
            "houses": kundli["Houses"]
        },
        "dasha": {
            "current_mahadasha": dasha.get("mahadasha", [{}])[0] if dasha.get("mahadasha") else {},
            "nakshatra": dasha.get("nakshatra", ""),
            "nakshatra_lord": dasha.get("nakshatra_lord", "")
        },
        "panchang": panchang,
        "yogas": {
            "total": yogas.get("total_yogas", 0),
            "major": yogas.get("major_yogas", []),
            "summary": yogas.get("summary", {})
        },
        "daily": daily,
        "strength": {
            "shadbala": {},  # Simplified for notifications
            "ashtakavarga": {}
        }
    }
    
    return combined


def generate_notification_for_user(user: User, birth_detail: BirthDetail) -> Optional[Dict]:
    """
    Phase 10: Generate daily notification for a single user.
    
    Args:
        user: User object
        birth_detail: User's birth detail
    
    Returns:
        Notification data dictionary or None if error
    """
    try:
        # Current date/time (noon for calculations)
        current_dt = datetime.now()
        current_jd = swe.julday(
            current_dt.year, current_dt.month, current_dt.day,
            12.0,  # Noon
            swe.GREG_CAL
        )
        
        # Build context
        context = build_user_context(birth_detail, current_jd)
        
        # Check subscription level
        is_premium = user.subscription_level in ["premium", "lifetime"]
        
        if is_premium:
            # HARD CUTOVER: Daily predictions MUST come from POST /api/v1/predict only.
            raise RuntimeError("DEPRECATED: Use /api/v1/predict ONLY")
            # Premium users get full AI prediction
            ai_prediction = interpret_daily(context, use_local=False)
            
            # Build full message
            message = f"""
🌅 Daily Horoscope - {current_dt.strftime('%B %d, %Y')}

{ai_prediction.get('summary', 'A day of balanced energies.')}

Lucky Color: {ai_prediction.get('lucky_color', 'White')}
Best Time: {ai_prediction.get('best_time', '10:00 - 14:00')}
Planet in Focus: {ai_prediction.get('planet_in_focus', 'Moon')}
Energy Rating: {ai_prediction.get('energy_rating', 70)}/100

What to Do:
{chr(10).join('• ' + item for item in ai_prediction.get('what_to_do', [])[:3])}

What to Avoid:
{chr(10).join('• ' + item for item in ai_prediction.get('what_to_avoid', [])[:2])}

Detailed Prediction:
{ai_prediction.get('detailed_prediction', 'Today brings balanced cosmic energies.')}

Morning Message:
{ai_prediction.get('morning_message', 'May this day bring you peace and prosperity.')}
"""
            
            summary = ai_prediction.get('summary', 'A day of balanced energies.')
            prediction_data = ai_prediction
        else:
            # Free users get summary only
            daily = context.get('daily', {})
            summary = f"Daily Score: {daily.get('score', 0):.1f} - {daily.get('rating', 'Good')}"
            
            message = f"""
🌅 Daily Horoscope - {current_dt.strftime('%B %d, %Y')}

{summary}

Your daily astrological reading is available. Upgrade to Premium for full AI-powered predictions with detailed guidance, lucky colors, best times, and personalized recommendations.

Current Dasha: {context.get('dasha', {}).get('nakshatra_lord', 'N/A')}
Yogas Detected: {context.get('yogas', {}).get('total', 0)}
"""
            
            prediction_data = {
                "summary": summary,
                "daily_score": daily.get('score', 0),
                "daily_rating": daily.get('rating', 'Good'),
                "subscription_required": True
            }
        
        return {
            "user_id": user.id,
            "notification_type": "daily",
            "title": f"Daily Horoscope - {current_dt.strftime('%B %d, %Y')}",
            "message": message.strip(),
            "summary": summary,
            "prediction_data": prediction_data,
            "delivery_status": "sent"
        }
    
    except Exception as e:
        print(f"Error generating notification for user {user.id}: {e}")
        return None


def run_daily_notifications():
    """
    Phase 10: Main function to run daily notifications for all users.
    
    This function:
    1. Fetches all users with birth data
    2. Generates daily predictions
    3. Saves notifications to database
    4. Respects user notification preferences
    """
    db = SessionLocal()
    try:
        # Get all users with birth data and notifications enabled
        users = db.query(User).filter(
            User.daily_notifications == "enabled"
        ).all()
        
        notifications_created = 0
        notifications_failed = 0
        
        for user in users:
            try:
                # Get user's birth data
                birth_detail = db.query(BirthDetail).filter(
                    BirthDetail.user_id == user.id
                ).first()
                
                if not birth_detail:
                    continue  # Skip users without birth data
                
                # Generate notification
                notification_data = generate_notification_for_user(user, birth_detail)
                
                if notification_data:
                    # Create notification record
                    notification = Notification(
                        user_id=notification_data["user_id"],
                        notification_type=notification_data["notification_type"],
                        title=notification_data["title"],
                        message=notification_data["message"],
                        summary=notification_data["summary"],
                        prediction_data=notification_data["prediction_data"],
                        delivery_status=notification_data["delivery_status"]
                    )
                    
                    db.add(notification)
                    notifications_created += 1
                else:
                    notifications_failed += 1
                    
            except Exception as e:
                print(f"Error processing user {user.id}: {e}")
                notifications_failed += 1
                continue
        
        db.commit()
        
        print(f"Daily notifications completed: {notifications_created} created, {notifications_failed} failed")
        return {
            "status": "success",
            "notifications_created": notifications_created,
            "notifications_failed": notifications_failed,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        db.rollback()
        print(f"Error in run_daily_notifications: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        db.close()

