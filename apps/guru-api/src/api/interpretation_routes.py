"""
Phase 18: Interpretation API Routes

API endpoints for complete Jyotish interpretation reports.
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from datetime import datetime
import swisseph as swe

from src.auth.jwt_handler import decode_token
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.jyotish.transits.gochar import get_transits
from src.jyotish.kundli_engine import get_planet_positions
from src.interpretation.interpretation_engine import generate_full_interpretation
from src.interpretation.nlg_formatter import generate_final_text_report
from src.db.database import SessionLocal
from src.db.models import BirthDetail, User

router = APIRouter()


def get_user_from_token(token: str) -> User:
    """Get user from JWT token."""
    try:
        token_data = decode_token(token)
        user_id = token_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


@router.get("/full-report")
async def get_full_interpretation_report(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
):
    """
    Phase 18: Get complete Jyotish interpretation report.
    
    Returns:
        Complete interpretation with JSON data and natural language report
    """
    # Extract token
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        token = authorization.replace("Bearer ", "").strip()
    elif token:
        token = token.strip()
    else:
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    # Get user
    user = get_user_from_token(token)
    
    # Get birth data
    db = SessionLocal()
    try:
        birth_data = db.query(BirthDetail).filter(BirthDetail.user_id == user.id).first()
        
        if not birth_data:
            raise HTTPException(
                status_code=400,
                detail="Birth data not found. Please save your birth details first."
            )
        
        # Build birth datetime
        birth_date = birth_data.birth_date
        hour, minute = map(int, birth_data.birth_time.split(':'))
        dt = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Calculate Julian Day
        jd = swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        lat = birth_data.birth_latitude
        lon = birth_data.birth_longitude
        
        # Generate Kundli
        kundli = generate_kundli(jd, lat, lon)
        
        # Calculate Dasha
        moon_degree = kundli["Planets"]["Moon"]["degree"]
        dasha = calculate_vimshottari_dasha(dt, moon_degree)
        kundli["dasha"] = dasha
        
        # Detect Yogas
        planets_for_yogas = {
            p: {
                'degree': kundli['Planets'][p]['degree'],
                'sign': kundli['Planets'][p]['sign'],
                'house': kundli['Planets'][p]['house']
            }
            for p in kundli['Planets'] if p not in ["Rahu", "Ketu"]
        }
        houses_for_yogas = [
            {'house': h['house'], 'degree': h['degree'], 'sign': h['sign']}
            for h in kundli['Houses']
        ]
        yogas = detect_all_yogas(planets_for_yogas, houses_for_yogas)
        kundli["yogas"] = {"detected_yogas": yogas}
        
        # Calculate Transits
        today = datetime.now()
        today_jd = swe.julday(
            today.year, today.month, today.day,
            today.hour + today.minute / 60.0,
            swe.GREG_CAL
        )
        current_planets = get_planet_positions(today_jd)
        birth_planets_dict = {p: kundli["Planets"][p]["degree"] for p in kundli["Planets"]}
        transits = get_transits(birth_planets_dict, current_planets, jd, today_jd)
        kundli["transits"] = transits
        
        # Generate full interpretation
        interpretation = generate_full_interpretation(kundli)
        
        # Generate natural language report
        report_text = generate_final_text_report(interpretation)
        
        return {
            "success": True,
            "user_id": user.id,
            "kundli": {
                "planets": {p: {"house": kundli["Planets"][p].get("house"), "sign": kundli["Planets"][p].get("sign")} for p in kundli["Planets"]},
                "houses": len(kundli.get("Houses", [])),
                "yogas_count": len(yogas)
            },
            "interpretation": interpretation,
            "report_text": report_text,
            "generated_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating interpretation: {str(e)}")
    
    finally:
        db.close()

