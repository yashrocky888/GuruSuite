"""
Phase 12: Multi-Channel Delivery Engine

Orchestrates notification delivery across all channels based on user preferences.
"""

from datetime import datetime
from typing import Dict, Optional
import swisseph as swe

from src.db.database import SessionLocal
from src.db.models import User, BirthDetail, Notification, DeliveryLog, NotificationPreferences
from src.notifications.preferences.user_prefs import get_prefs
from src.notifications.channels.whatsapp import send_whatsapp
from src.notifications.channels.emailer import send_email
from src.notifications.channels.push import send_push
from src.notifications.templates.daily import daily_short, daily_full
from src.ai.interpreter.daily_interpreter import interpret_daily
from src.jyotish.daily.daily_engine import compute_daily
from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.jyotish.panchang_engine import generate_panchang
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.utils.converters import degrees_to_sign


def build_daily_data(birth_detail: BirthDetail) -> Dict:
    """
    Phase 12: Build complete daily data for user.
    
    Args:
        birth_detail: User's birth detail
    
    Returns:
        Complete daily data dictionary
    """
    # Parse birth date and time
    birth_dt = birth_detail.birth_date
    birth_time_str = birth_detail.birth_time
    hour, minute = map(int, birth_time_str.split(':'))
    birth_datetime = datetime.combine(birth_dt, datetime.min.time().replace(hour=hour, minute=minute))
    
    # Calculate Julian Days
    birth_jd = swe.julday(
        birth_datetime.year, birth_datetime.month, birth_datetime.day,
        birth_datetime.hour + birth_datetime.minute / 60.0,
        swe.GREG_CAL
    )
    
    current_dt = datetime.now()
    current_jd = swe.julday(
        current_dt.year, current_dt.month, current_dt.day,
        12.0,
        swe.GREG_CAL
    )
    
    # Generate all data
    kundli = generate_kundli(birth_jd, birth_detail.birth_latitude, birth_detail.birth_longitude)
    birth_planets = get_planet_positions(birth_jd)
    moon_degree = birth_planets["Moon"]
    dasha = calculate_vimshottari_dasha(birth_datetime, moon_degree)
    panchang = generate_panchang(current_jd, current_dt, birth_detail.birth_latitude, birth_detail.birth_longitude)
    
    # Prepare for yogas
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
    
    yogas = detect_all_yogas(planets, houses)
    daily = compute_daily(birth_jd, current_jd, birth_detail.birth_latitude, birth_detail.birth_longitude, birth_datetime)
    
    # Get moon data for lucky color
    moon_data = daily.get("moon", {})
    
    return {
        "kundli": {
            "ascendant": kundli["Ascendant"],
            "planets": kundli["Planets"]
        },
        "dasha": dasha,
        "panchang": panchang,
        "yogas": yogas,
        "daily": daily,
        "moon": moon_data,
        "daily_strength": {
            "summary": daily.get("summary", "A day of balanced energies"),
            "score": daily.get("score", 70),
            "rating": daily.get("rating", "Good"),
            "moon": moon_data
        }
    }


def send_to_user(user: User, data: Dict, prefs: NotificationPreferences, db: SessionLocal) -> Dict:
    """
    Phase 12: Send notifications to user via all enabled channels.
    
    Args:
        user: User object
        data: Daily prediction data
        prefs: User notification preferences
        db: Database session
    
    Returns:
        Dictionary with delivery results
    """
    results = {
        "user_id": user.id,
        "channels": {}
    }
    
    # Generate messages
    short_msg = daily_short(data, prefs.language)
    summary = data.get("daily_strength", {}).get("summary", "Daily guidance")
    
    # Check subscription for full AI message
    is_premium = user.subscription_level in ["premium", "lifetime"]
    
    if is_premium:
        # Get full AI prediction
        try:
            ai_prediction = interpret_daily(data, use_local=False)
            full_msg = daily_full(ai_prediction, prefs.language)
        except:
            full_msg = short_msg
    else:
        full_msg = short_msg  # Free users get short message
    
    # WhatsApp delivery
    if prefs.channel_whatsapp == "enabled":
        whatsapp_number = prefs.whatsapp_number or user.phone
        if whatsapp_number:
            result = send_whatsapp(whatsapp_number, short_msg)
            status = "success" if result.get("success") else "failed"
            error_msg = result.get("error") if not result.get("success") else None
            
            log = DeliveryLog(
                user_id=user.id,
                channel="whatsapp",
                status=status,
                message_preview=summary[:200],
                error_message=error_msg,
                gateway_response=result
            )
            db.add(log)
            results["channels"]["whatsapp"] = result
    
    # Email delivery
    if prefs.channel_email == "enabled" and user.email:
        result = send_email(user.email, "Your Daily Guru Guidance", full_msg)
        status = "success" if result.get("success") else "failed"
        error_msg = result.get("error") if not result.get("success") else None
        
        log = DeliveryLog(
            user_id=user.id,
            channel="email",
            status=status,
            message_preview=summary[:200],
            error_message=error_msg,
            gateway_response=result
        )
        db.add(log)
        results["channels"]["email"] = result
    
    # Push notification delivery
    if prefs.channel_push == "enabled" and prefs.push_token:
        result = send_push(prefs.push_token, "Guru's Daily Guidance", summary)
        status = "success" if result.get("success") else "failed"
        error_msg = result.get("error") if not result.get("success") else None
        
        log = DeliveryLog(
            user_id=user.id,
            channel="push",
            status=status,
            message_preview=summary[:200],
            error_message=error_msg,
            gateway_response=result
        )
        db.add(log)
        results["channels"]["push"] = result
    
    # In-app notification (always create if enabled)
    if prefs.channel_inapp == "enabled":
        try:
            # Create in-app notification
            notification = Notification(
                user_id=user.id,
                notification_type="daily",
                title=f"Daily Horoscope - {datetime.now().strftime('%B %d, %Y')}",
                message=full_msg,
                summary=summary,
                prediction_data=data if is_premium else {"summary": summary},
                delivery_status="sent"
            )
            db.add(notification)
            
            log = DeliveryLog(
                user_id=user.id,
                channel="in_app",
                status="success",
                message_preview=summary[:200]
            )
            db.add(log)
            results["channels"]["in_app"] = {"success": True}
        except Exception as e:
            log = DeliveryLog(
                user_id=user.id,
                channel="in_app",
                status="failed",
                message_preview=summary[:200],
                error_message=str(e)
            )
            db.add(log)
            results["channels"]["in_app"] = {"success": False, "error": str(e)}
    
    return results


def process_due_users() -> Dict:
    """
    Phase 12: Process all users who need notifications at current time.
    
    Runs every 5 minutes, checks which users have delivery_time matching current time.
    
    Returns:
        Dictionary with processing results
    """
    db = SessionLocal()
    try:
        now = datetime.now().strftime("%H:%M")
        
        # Get all users with notifications enabled
        users = db.query(User).filter(
            User.daily_notifications == "enabled"
        ).all()
        
        processed = 0
        successful = 0
        failed = 0
        
        for user in users:
            try:
                # Get user preferences
                prefs = get_prefs(user.id, db)
                
                # Check if it's time to deliver
                if prefs.delivery_time != now:
                    continue
                
                # Get birth data
                birth_detail = db.query(BirthDetail).filter(
                    BirthDetail.user_id == user.id
                ).first()
                
                if not birth_detail:
                    continue
                
                # Build daily data
                data = build_daily_data(birth_detail)
                
                # Send to user
                result = send_to_user(user, data, prefs, db)
                
                processed += 1
                if any(ch.get("success") for ch in result.get("channels", {}).values()):
                    successful += 1
                else:
                    failed += 1
                
            except Exception as e:
                print(f"Error processing user {user.id}: {e}")
                failed += 1
                continue
        
        db.commit()
        
        return {
            "status": "success",
            "processed": processed,
            "successful": successful,
            "failed": failed,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        db.rollback()
        print(f"Error in process_due_users: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        db.close()

