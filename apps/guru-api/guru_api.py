"""
Phase 21: Guru API Wrapper

Main wrapper class for all Guru API functionality.
"""

from typing import Dict, Optional
from datetime import datetime

from src.interpretation.interpretation_engine import generate_full_interpretation
from src.transit_ai.daily_prediction_engine import generate_daily_transit_report
from src.transit_ai.transit_nlg import format_daily_transit_text
from src.muhurtha.muhurtha_engine import get_best_muhurtha
from src.nlg.nlg_muhurtha import format_muhurtha
from src.monthly.monthly_engine import generate_monthly_report
from src.nlg.nlg_monthly import format_monthly
from src.yearly.yearly_prediction_engine import generate_yearly_report
from src.nlg.nlg_yearly import format_yearly
from src.karma.life_path_engine import generate_karma_report
from src.nlg.nlg_karma import format_karma
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.transit_ai.transit_context_builder import build_transit_context
import swisseph as swe
from api.cache import cache_result


class GuruAPI:
    """
    Phase 21: Main Guru API wrapper class.
    
    Provides unified interface to all Guru API functionality.
    """
    
    def __init__(self):
        """Initialize Guru API."""
        pass
    
    @cache_result(ttl_seconds=3600)  # Cache for 1 hour
    def get_full_report(self, birth_details: Dict) -> Dict:
        """
        Phase 21: Get full kundali report with interpretation.
        
        Uses location-based precise calculations matching Drik Panchanga methodology.
        
        Args:
            birth_details: Birth details dictionary (can include birth_place for geocoding)
        
        Returns:
            Complete kundali report with interpretation
        """
        # Build birth chart with precise location-based calculations (Drik Panchanga methodology)
        birth_date = birth_details.get("birth_date")
        birth_time = birth_details.get("birth_time")
        birth_lat = birth_details.get("birth_latitude")
        birth_lon = birth_details.get("birth_longitude")
        birth_place = birth_details.get("birth_place")
        timezone = birth_details.get("timezone", "UTC")
        
        # Get precise coordinates (geocode if place name provided, like Drik Panchanga)
        if (birth_lat is None or birth_lon is None) and birth_place:
            from src.utils.location import geocode_place
            coords = geocode_place(birth_place)
            if coords:
                birth_lat, birth_lon = coords
        
        if isinstance(birth_date, str):
            birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
        else:
            birth_date_obj = birth_date if hasattr(birth_date, 'year') else datetime.strptime(str(birth_date), "%Y-%m-%d").date()
        
        # Parse time with seconds precision (Drik Panchanga uses exact time)
        time_parts = birth_time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        birth_dt_local = datetime.combine(birth_date_obj, datetime.min.time().replace(hour=hour, minute=minute, second=second, microsecond=0))
        
        # Convert local time to UTC (Swiss Ephemeris requires UTC)
        from src.utils.timezone import local_to_utc
        birth_dt_utc = local_to_utc(birth_dt_local, timezone)
        
        # Calculate Julian Day with maximum precision (matching Drik Panchanga)
        # Use full precision including seconds for accurate calculations
        birth_jd = swe.julday(
            birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
            birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0,
            swe.GREG_CAL
        )
        
        kundli = generate_kundli(birth_jd, birth_lat, birth_lon)
        
        # Generate interpretation (pass kundli, not birth_details)
        interpretation = generate_full_interpretation(kundli)
        
        return {
            "kundli": kundli,
            "interpretation": interpretation,
            "summary": "Complete birth chart analysis with detailed interpretation"
        }
    
    def get_today_transit_report(self, birth_details: Dict, on_date: Optional[str] = None) -> Dict:
        """
        Phase 21: Get today's transit prediction.
        
        Args:
            birth_details: Birth details dictionary
            on_date: Optional date (YYYY-MM-DD, defaults to today)
        
        Returns:
            Daily transit report
        """
        # Ensure birth_details is a dictionary
        if not isinstance(birth_details, dict):
            birth_details = {
                "birth_date": getattr(birth_details, "birth_date", None),
                "birth_time": getattr(birth_details, "birth_time", None),
                "birth_latitude": getattr(birth_details, "birth_latitude", None),
                "birth_longitude": getattr(birth_details, "birth_longitude", None),
                "timezone": getattr(birth_details, "timezone", "UTC")
            }
        
        # Parse date
        if on_date:
            calc_date = datetime.strptime(on_date, "%Y-%m-%d")
        else:
            calc_date = datetime.now()
        
        location = {
            "latitude": birth_details.get("birth_latitude"),
            "longitude": birth_details.get("birth_longitude"),
            "timezone": birth_details.get("timezone", "UTC")
        }
        
        # Generate report - pass dict directly
        report_json = generate_daily_transit_report(
            birth_details=birth_details,
            on_datetime=calc_date,
            location=location
        )
        report_text = format_daily_transit_text(report_json)
        
        return {
            "daily_transit_json": report_json,
            "daily_transit_text": report_text
        }
    
    def get_muhurtha(
        self,
        task: str,
        date: datetime,
        location: Dict,
        birth_details: Dict
    ) -> Dict:
        """
        Phase 21: Get best Muhurtha time windows.
        
        Args:
            task: Task type
            date: Date for Muhurtha
            location: Location dictionary
            birth_details: Birth details
        
        Returns:
            Muhurtha analysis
        """
        # Build birth chart
        birth_date = birth_details.get("birth_date")
        birth_time = birth_details.get("birth_time")
        birth_lat = birth_details.get("birth_latitude")
        birth_lon = birth_details.get("birth_longitude")
        timezone = birth_details.get("timezone", "UTC")
        
        if isinstance(birth_date, str):
            birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
        else:
            birth_date_obj = birth_date if hasattr(birth_date, 'year') else datetime.strptime(str(birth_date), "%Y-%m-%d").date()
        
        hour, minute = map(int, birth_time.split(':'))
        birth_dt_local = datetime.combine(birth_date_obj, datetime.min.time().replace(hour=hour, minute=minute, second=0, microsecond=0))
        
        # Convert local time to UTC (Swiss Ephemeris requires UTC)
        from src.utils.timezone import local_to_utc
        birth_dt_utc = local_to_utc(birth_dt_local, timezone)
        
        # Calculate Julian Day from UTC time
        birth_jd = swe.julday(
            birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
            birth_dt_utc.hour + birth_dt_utc.minute / 60.0,
            swe.GREG_CAL
        )
        
        natal_chart = generate_kundli(birth_jd, birth_lat, birth_lon)
        
        # Get Dasha
        moon_degree = natal_chart["Planets"]["Moon"]["degree"]
        dasha = calculate_vimshottari_dasha(birth_dt_utc, moon_degree)
        
        # Build transit context
        transit_context = build_transit_context(birth_details, date, location)
        
        # Get Muhurtha
        muhurtha_json = get_best_muhurtha(
            date=date,
            location=location,
            task=task,
            birth_chart=natal_chart,
            dasha=dasha,
            transit=transit_context
        )
        
        # Format text
        muhurtha_text = format_muhurtha(muhurtha_json)
        
        return {
            "muhurtha_json": muhurtha_json,
            "muhurtha_text": muhurtha_text
        }
    
    def get_monthly_prediction(self, birth_details: Dict, month: int, year: int) -> Dict:
        """
        Phase 21: Get monthly prediction.
        
        Args:
            birth_details: Birth details dictionary
            month: Month number (1-12)
            year: Year
        
        Returns:
            Monthly prediction report
        """
        monthly_json = generate_monthly_report(birth_details, month, year)
        monthly_text = format_monthly(monthly_json)
        
        return {
            "monthly_json": monthly_json,
            "monthly_text": monthly_text
        }
    
    def get_yearly_prediction(self, birth_details: Dict, year: int) -> Dict:
        """
        Phase 21: Get yearly prediction.
        
        Args:
            birth_details: Birth details dictionary
            year: Year
        
        Returns:
            Yearly prediction report
        """
        yearly_json = generate_yearly_report(birth_details, year)
        yearly_text = format_yearly(yearly_json)
        
        return {
            "yearly_json": yearly_json,
            "yearly_text": yearly_text
        }
    
    def get_karma_report(self, birth_details: Dict) -> Dict:
        """
        Phase 21: Get karma and soul path report.
        
        Args:
            birth_details: Birth details dictionary
        
        Returns:
            Karma report
        """
        karma_json = generate_karma_report(birth_details)
        karma_text = format_karma(karma_json)
        
        return {
            "karma_json": karma_json,
            "karma_text": karma_text
        }


# Global instance
guru_api = GuruAPI()

