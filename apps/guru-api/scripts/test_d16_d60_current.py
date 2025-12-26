#!/usr/bin/env python3
"""
Test script to output current D16-D60 varga results
for comparison with Prokerala/JHora reference data.

Test data: 1995-05-16, 18:38 IST, Bangalore (Lahiri)
"""

import sys
import os

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

import swisseph as swe
from datetime import datetime
from utils.timezone import local_to_utc
from jyotish.kundli_engine import generate_kundli
from jyotish.varga_engine import build_varga_chart

# Test data: 1995-05-16, 18:38 IST, Bangalore
birth_dt = datetime(1995, 5, 16, 18, 38, 0)
birth_dt_utc = local_to_utc(birth_dt, 'Asia/Kolkata')
jd = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
                birth_dt_utc.hour + birth_dt_utc.minute/60.0, swe.GREG_CAL)
lat, lon = 12.9716, 77.5946

# Get D1 data
d1 = generate_kundli(jd, lat, lon)
d1_asc = d1['Ascendant']['degree']
d1_asc_sign = d1['Ascendant']['sign_sanskrit']
d1_planets = {p: d1['Planets'][p]['degree'] for p in 
              ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']}

print("=" * 80)
print("D16-D60 VARGA TEST RESULTS (Current Implementation)")
print("=" * 80)
print(f"\nD1 Ascendant: {d1_asc_sign} ({d1_asc:.4f}°)")
print(f"D1 Moon: {d1['Planets']['Moon']['sign_sanskrit']} ({d1_planets['Moon']:.4f}°)")
print(f"D1 Rahu: {d1['Planets']['Rahu']['sign_sanskrit']} ({d1_planets['Rahu']:.4f}°)")
print("\n" + "=" * 80)

# Test all vargas D16-D60
vargas_to_test = [16, 20, 24, 27, 30, 40, 45, 60]

for varga in vargas_to_test:
    try:
        chart = build_varga_chart(d1_planets, d1_asc, varga)
        asc = chart['ascendant']
        moon = chart['planets']['Moon']
        rahu = chart['planets']['Rahu']
        
        print(f"\nD{varga}:")
        print(f"  Ascendant: {asc['sign']} (sign_index: {asc['sign_index']}, degree: {asc['degree']:.4f}°)")
        print(f"  Moon:      {moon['sign']} (sign_index: {moon['sign_index']}, degree: {moon['degree']:.4f}°)")
        print(f"  Rahu:      {rahu['sign']} (sign_index: {rahu['sign_index']}, degree: {rahu['degree']:.4f}°)")
    except Exception as e:
        print(f"\nD{varga}: ERROR - {e}")

print("\n" + "=" * 80)
print("END OF TEST RESULTS")
print("=" * 80)

