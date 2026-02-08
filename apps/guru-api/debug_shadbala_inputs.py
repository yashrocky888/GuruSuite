#!/usr/bin/env python3
"""
Debug script to fetch and print raw Shadbala inputs.
FOUNDATION VERIFICATION MODE - NO Shadbala calculations.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.jyotish.strength.shadbala import debug_raw_shadbala_inputs

if __name__ == "__main__":
    # Test case: 2006-02-03 22:30 IST, Bengaluru
    date = "2006-02-03"
    time = "22:30"
    lat = 12.9716
    lon = 77.5946
    timezone = "Asia/Kolkata"
    
    debug_raw_shadbala_inputs(date, time, lat, lon, timezone)
