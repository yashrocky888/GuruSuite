"""
Varga Calibration Loader

Loads lookup tables for D24-D60 varga charts from calibration JSON files.
These tables are manually verified against ProKerala/JHora outputs.

Architecture:
- D1-D20: Formula-based (verified correct)
- D24-D60: Lookup-table based (calibrated from ProKerala/JHora)
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path

# Cache for loaded calibration tables
_calibration_cache: Dict[str, Dict[int, List[int]]] = {}


def load_calibration_table(varga: str) -> Optional[Dict[int, List[int]]]:
    """
    Load calibration table for a specific varga.
    
    Args:
        varga: Varga name (e.g., "D24", "D27", "D30", "D40", "D45", "D60")
    
    Returns:
        Dictionary mapping base_sign_index (0-11) to list of final_sign_index (0-11)
        for each amsa_index (0 to N-1), or None if file not found
    """
    if varga in _calibration_cache:
        return _calibration_cache[varga]
    
    # Get calibration file path
    calibration_dir = Path(__file__).parent.parent.parent / "calibration"
    calibration_file = calibration_dir / f"{varga.lower()}.json"
    
    if not calibration_file.exists():
        return None
    
    try:
        with open(calibration_file, 'r') as f:
            data = json.load(f)
        
        # Extract table and convert to proper format
        table_data = data.get("table", {})
        calibration_table = {}
        
        for base_sign_str, amsa_list in table_data.items():
            base_sign = int(base_sign_str)
            calibration_table[base_sign] = [int(sign) for sign in amsa_list]
        
        # Cache the result
        _calibration_cache[varga] = calibration_table
        
        return calibration_table
    
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"⚠️  Error loading calibration for {varga}: {e}")
        return None


def get_varga_sign_from_calibration(
    base_sign_index: int,
    amsa_index: int,
    varga: str
) -> Optional[int]:
    """
    Get varga sign from calibration table.
    
    Args:
        base_sign_index: Base sign index (0-11) from D1
        amsa_index: Amsa index (0 to N-1) within the sign
        varga: Varga name (e.g., "D24", "D27", "D30", "D40", "D45", "D60")
    
    Returns:
        Final sign index (0-11) in varga chart, or None if calibration not available
    """
    calibration_table = load_calibration_table(varga)
    
    if calibration_table is None:
        return None
    
    if base_sign_index not in calibration_table:
        return None
    
    amsa_list = calibration_table[base_sign_index]
    
    if amsa_index < 0 or amsa_index >= len(amsa_list):
        return None
    
    return amsa_list[amsa_index]


def is_calibration_available(varga: str) -> bool:
    """
    Check if calibration table is available for a varga.
    
    Args:
        varga: Varga name (e.g., "D24", "D27", "D30", "D40", "D45", "D60")
    
    Returns:
        True if calibration table exists and is loaded
    """
    return load_calibration_table(varga) is not None

