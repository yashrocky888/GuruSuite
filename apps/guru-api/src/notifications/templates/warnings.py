"""
Phase 12: Warning/Alert Notification Templates

Templates for transit warnings and important alerts.
"""

from typing import Dict


def transit_warning(warning_data: Dict, language: str = "english") -> str:
    """
    Phase 12: Generate transit warning message template.
    
    Args:
        warning_data: Warning/alert data
        language: Language code
    
    Returns:
        Warning message string
    """
    planet = warning_data.get("planet", "Unknown")
    warning_type = warning_data.get("type", "general")
    message = warning_data.get("message", "Be cautious today")
    severity = warning_data.get("severity", "moderate")
    
    if language == "hindi":
        severity_map = {
            "high": "उच्च",
            "moderate": "मध्यम",
            "low": "निम्न"
        }
        return f"""
⚠️ ग्रह संक्रमण चेतावनी ⚠️

ग्रह: {planet}
प्रकार: {warning_type}
गंभीरता: {severity_map.get(severity, severity)}

संदेश:
{message}

कृपया सावधान रहें और महत्वपूर्ण निर्णय लेने से पहले सोचें।
"""
    elif language == "kannada":
        severity_map = {
            "high": "ಉನ್ನತ",
            "moderate": "ಮಧ್ಯಮ",
            "low": "ಕಡಿಮೆ"
        }
        return f"""
⚠️ ಗ್ರಹ ಸಂಕ್ರಮಣ ಎಚ್ಚರಿಕೆ ⚠️

ಗ್ರಹ: {planet}
ವಿಧ: {warning_type}
ತೀವ್ರತೆ: {severity_map.get(severity, severity)}

ಸಂದೇಶ:
{message}

ದಯವಿಟ್ಟು ಎಚ್ಚರಿಕೆಯಿಂದಿರಿ ಮತ್ತು ಪ್ರಮುಖ ನಿರ್ಧಾರಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳುವ ಮೊದಲು ಯೋಚಿಸಿ.
"""
    else:  # english
        return f"""
⚠️ Transit Warning ⚠️

Planet: {planet}
Type: {warning_type}
Severity: {severity.title()}

Message:
{message}

Please be cautious and think carefully before making important decisions.
"""

