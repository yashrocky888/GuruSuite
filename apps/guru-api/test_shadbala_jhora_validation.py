#!/usr/bin/env python3
"""
JHora Cross-Validation - Structural Shadbala Test
Birth Chart 3: 2001-04-07, 11:00 IST, Bangalore
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.jyotish.strength.shadbala import calculate_shadbala
from src.utils.timezone import get_julian_day, local_to_utc
from datetime import datetime
import pytz

# Test Chart 3
BIRTH_3 = {
    "date": "2001-04-07",
    "time": "11:00",
    "lat": 12.9716,
    "lon": 77.5946,
    "timezone": "Asia/Kolkata"
}

# JHora Reference Data (to be provided)
# Format: {planet: {"total": virupas, "rupas": rupas, "rank": rank}}
JHORA_REFERENCE = {
    "Sun": {"total": None, "rupas": None, "rank": None},
    "Moon": {"total": None, "rupas": None, "rank": None},
    "Mars": {"total": None, "rupas": None, "rank": None},
    "Mercury": {"total": None, "rupas": None, "rank": None},
    "Jupiter": {"total": None, "rupas": None, "rank": None},
    "Venus": {"total": None, "rupas": None, "rank": None},
    "Saturn": {"total": None, "rupas": None, "rank": None}
}

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def run_shadbala_birth3():
    """Run Shadbala calculation for Birth Chart 3"""
    print("=" * 100)
    print("JHORA CROSS-VALIDATION - BIRTH CHART 3")
    print("=" * 100)
    print(f"Date: {BIRTH_3['date']} {BIRTH_3['time']} {BIRTH_3['timezone']}")
    print(f"Location: {BIRTH_3['lat']}, {BIRTH_3['lon']} (Bangalore)")
    print(f"Ayanamsa: Lahiri (engine default)")
    print("=" * 100)
    print()
    
    # Parse date and time
    date_obj = datetime.strptime(BIRTH_3['date'], "%Y-%m-%d").date()
    time_parts = BIRTH_3['time'].split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    second = int(time_parts[2]) if len(time_parts) > 2 else 0
    
    # Create local datetime
    birth_dt_local = datetime.combine(
        date_obj,
        datetime.min.time().replace(hour=hour, minute=minute, second=second)
    )
    
    # Convert to UTC
    from src.utils.timezone import local_to_utc
    birth_dt_utc = local_to_utc(birth_dt_local, BIRTH_3['timezone'])
    
    # Get Julian Day
    jd = get_julian_day(birth_dt_utc)
    
    # Calculate Shadbala
    result = calculate_shadbala(
        jd=jd,
        lat=BIRTH_3['lat'],
        lon=BIRTH_3['lon'],
        timezone=BIRTH_3['timezone']
    )
    
    return result

def format_value(value, decimals=2):
    """Format numeric value"""
    if value is None:
        return "N/A"
    if isinstance(value, float) and (value != value or value == float('inf')):
        return "N/A"
    return f"{value:.{decimals}f}"

def print_comparison_table(our_results, jhora_ref):
    """Print comparison table"""
    print("=" * 100)
    print("COMPARISON TABLE")
    print("=" * 100)
    print()
    print(f"{'Planet':<12} | {'Our Total':<12} | {'Our Rupas':<12} | {'JHora Total':<12} | {'JHora Rupas':<12} | {'Rank (Our)':<12} | {'Rank (JHora)':<12}")
    print("-" * 100)
    
    for planet in PLANET_ORDER:
        if planet not in our_results:
            continue
        
        our_data = our_results[planet]
        jhora_data = jhora_ref.get(planet, {})
        
        our_total = our_data.get('total_shadbala', 0)
        our_rupas = our_data.get('shadbala_in_rupas', 0)
        our_rank = our_data.get('relative_rank', 'N/A')
        
        jhora_total = jhora_data.get('total', None)
        jhora_rupas = jhora_data.get('rupas', None)
        jhora_rank = jhora_data.get('rank', None)
        
        print(f"{planet:<12} | {format_value(our_total):<12} | {format_value(our_rupas):<12} | "
              f"{format_value(jhora_total):<12} | {format_value(jhora_rupas):<12} | "
              f"{our_rank:<12} | {jhora_rank if jhora_rank is not None else 'N/A':<12}")
    
    print()

def analyze_structural_correctness(our_results, jhora_ref):
    """Perform structural analysis"""
    print("=" * 100)
    print("ANALYSIS - STRUCTURAL CORRECTNESS")
    print("=" * 100)
    print()
    
    # Sort our results by total
    our_sorted = sorted(
        [(p, our_results[p]) for p in PLANET_ORDER if p in our_results],
        key=lambda x: x[1].get('total_shadbala', 0),
        reverse=True
    )
    
    # Sort JHora results by total (if available)
    jhora_sorted = []
    if any(jhora_ref.get(p, {}).get('total') is not None for p in PLANET_ORDER):
        jhora_sorted = sorted(
            [(p, jhora_ref.get(p, {})) for p in PLANET_ORDER if jhora_ref.get(p, {}).get('total') is not None],
            key=lambda x: x[1].get('total', 0),
            reverse=True
        )
    
    analysis_points = []
    
    # 1. Strongest planets match directionally?
    if jhora_sorted:
        our_top3 = [p for p, _ in our_sorted[:3]]
        jhora_top3 = [p for p, _ in jhora_sorted[:3]]
        overlap = len(set(our_top3) & set(jhora_top3))
        if overlap >= 2:
            analysis_points.append(f"✅ Strongest planets: {overlap}/3 match ({our_top3} vs {jhora_top3})")
        elif overlap == 1:
            analysis_points.append(f"⚠️  Strongest planets: {overlap}/3 match ({our_top3} vs {jhora_top3})")
        else:
            analysis_points.append(f"❌ Strongest planets: {overlap}/3 match ({our_top3} vs {jhora_top3})")
    else:
        our_top3 = [p for p, _ in our_sorted[:3]]
        analysis_points.append(f"ℹ️  Our strongest: {our_top3} (JHora data needed for comparison)")
    
    # 2. Weakest planets match directionally?
    if jhora_sorted:
        our_bottom3 = [p for p, _ in our_sorted[-3:]]
        jhora_bottom3 = [p for p, _ in jhora_sorted[-3:]]
        overlap = len(set(our_bottom3) & set(jhora_bottom3))
        if overlap >= 2:
            analysis_points.append(f"✅ Weakest planets: {overlap}/3 match ({our_bottom3} vs {jhora_bottom3})")
        elif overlap == 1:
            analysis_points.append(f"⚠️  Weakest planets: {overlap}/3 match ({our_bottom3} vs {jhora_bottom3})")
        else:
            analysis_points.append(f"❌ Weakest planets: {overlap}/3 match ({our_bottom3} vs {jhora_bottom3})")
    else:
        our_bottom3 = [p for p, _ in our_sorted[-3:]]
        analysis_points.append(f"ℹ️  Our weakest: {our_bottom3} (JHora data needed for comparison)")
    
    # 3. Rank inversion > 2 positions?
    if jhora_sorted:
        rank_inversions = []
        for planet in PLANET_ORDER:
            if planet not in our_results or jhora_ref.get(planet, {}).get('rank') is None:
                continue
            our_rank = our_results[planet].get('relative_rank', 999)
            jhora_rank = jhora_ref[planet].get('rank', 999)
            diff = abs(our_rank - jhora_rank)
            if diff > 2:
                rank_inversions.append((planet, our_rank, jhora_rank, diff))
        
        if rank_inversions:
            analysis_points.append(f"❌ Rank inversions > 2: {rank_inversions}")
        else:
            analysis_points.append("✅ No rank inversions > 2 positions")
    else:
        analysis_points.append("ℹ️  Rank inversion check requires JHora data")
    
    # 4. Bala component exploding (>600) or collapsing (<150)?
    component_issues = []
    for planet in PLANET_ORDER:
        if planet not in our_results:
            continue
        data = our_results[planet]
        
        sthana = data.get('sthana_bala', 0)
        dig = data.get('dig_bala', 0)
        kala = data.get('kala_bala', 0)
        total = data.get('total_shadbala', 0)
        
        if sthana > 600:
            component_issues.append(f"{planet} Sthana Bala: {sthana:.2f} (>600)")
        if dig > 600:
            component_issues.append(f"{planet} Dig Bala: {dig:.2f} (>600)")
        if kala > 600:
            component_issues.append(f"{planet} Kala Bala: {kala:.2f} (>600)")
        if total > 600:
            component_issues.append(f"{planet} Total: {total:.2f} (>600)")
        if total < 150:
            component_issues.append(f"{planet} Total: {total:.2f} (<150)")
    
    if component_issues:
        analysis_points.append(f"⚠️  Component anomalies: {component_issues}")
    else:
        analysis_points.append("✅ All components within normal range (150-600)")
    
    # 5. Dig Bala contradiction check
    dig_issues = []
    for planet in PLANET_ORDER:
        if planet not in our_results:
            continue
        dig = our_results[planet].get('dig_bala', 0)
        # Dig Bala should be 0-60, but check for extreme values
        if dig < 0:
            dig_issues.append(f"{planet} Dig Bala negative: {dig:.2f}")
        if dig > 60:
            dig_issues.append(f"{planet} Dig Bala > 60: {dig:.2f}")
    
    if dig_issues:
        analysis_points.append(f"❌ Dig Bala contradictions: {dig_issues}")
    else:
        analysis_points.append("✅ Dig Bala within valid range [0, 60]")
    
    # Print analysis
    for point in analysis_points:
        print(point)
    
    print()

def provide_verdict(our_results, jhora_ref):
    """Provide final verdict"""
    print("=" * 100)
    print("FINAL VERDICT")
    print("=" * 100)
    print()
    
    # Check if JHora data is available
    has_jhora_data = any(jhora_ref.get(p, {}).get('total') is not None for p in PLANET_ORDER)
    
    if not has_jhora_data:
        print("⚠️  WARN: JHora reference data not provided")
        print("   Cannot perform full structural validation.")
        print("   Please provide JHora Shadbala table (rupas & totals) for comparison.")
        print()
        print("   Our results are ready for comparison once JHora data is added.")
        return
    
    # Perform checks
    our_sorted = sorted(
        [(p, our_results[p]) for p in PLANET_ORDER if p in our_results],
        key=lambda x: x[1].get('total_shadbala', 0),
        reverse=True
    )
    
    jhora_sorted = sorted(
        [(p, jhora_ref.get(p, {})) for p in PLANET_ORDER if jhora_ref.get(p, {}).get('total') is not None],
        key=lambda x: x[1].get('total', 0),
        reverse=True
    )
    
    # Check top 3 overlap
    our_top3 = set(p for p, _ in our_sorted[:3])
    jhora_top3 = set(p for p, _ in jhora_sorted[:3])
    top3_overlap = len(our_top3 & jhora_top3)
    
    # Check bottom 3 overlap
    our_bottom3 = set(p for p, _ in our_sorted[-3:])
    jhora_bottom3 = set(p for p, _ in jhora_sorted[-3:])
    bottom3_overlap = len(our_bottom3 & jhora_bottom3)
    
    # Check rank inversions
    rank_inversions = 0
    for planet in PLANET_ORDER:
        if planet not in our_results or jhora_ref.get(planet, {}).get('rank') is None:
            continue
        our_rank = our_results[planet].get('relative_rank', 999)
        jhora_rank = jhora_ref[planet].get('rank', 999)
        if abs(our_rank - jhora_rank) > 2:
            rank_inversions += 1
    
    # Determine verdict
    if top3_overlap >= 2 and bottom3_overlap >= 2 and rank_inversions == 0:
        print("✅ PASS: Structurally consistent with JHora")
        print(f"   - Top 3 overlap: {top3_overlap}/3")
        print(f"   - Bottom 3 overlap: {bottom3_overlap}/3")
        print(f"   - Rank inversions > 2: {rank_inversions}")
    elif top3_overlap >= 1 and bottom3_overlap >= 1 and rank_inversions <= 1:
        print("⚠️  WARN: Minor variance but acceptable")
        print(f"   - Top 3 overlap: {top3_overlap}/3")
        print(f"   - Bottom 3 overlap: {bottom3_overlap}/3")
        print(f"   - Rank inversions > 2: {rank_inversions}")
    else:
        print("❌ FAIL: Major logical contradiction")
        print(f"   - Top 3 overlap: {top3_overlap}/3")
        print(f"   - Bottom 3 overlap: {bottom3_overlap}/3")
        print(f"   - Rank inversions > 2: {rank_inversions}")

def print_detailed_breakdown(our_results):
    """Print detailed component breakdown"""
    print("=" * 100)
    print("DETAILED COMPONENT BREAKDOWN (Our Engine)")
    print("=" * 100)
    print()
    
    for planet in PLANET_ORDER:
        if planet not in our_results:
            continue
        
        data = our_results[planet]
        print(f"{planet}:")
        print(f"  Sthana Bala:     {format_value(data.get('sthana_bala', 0))} Virupas")
        print(f"  Dig Bala:        {format_value(data.get('dig_bala', 0))} Virupas")
        print(f"  Kala Bala:       {format_value(data.get('kala_bala', 0))} Virupas")
        print(f"  Cheshta Bala:    {format_value(data.get('cheshta_bala', 0))} Virupas")
        print(f"  Naisargika Bala: {format_value(data.get('naisargika_bala', 0))} Virupas")
        print(f"  Drik Bala:       {format_value(data.get('drik_bala', 0))} Virupas")
        print(f"  TOTAL:           {format_value(data.get('total_shadbala', 0))} Virupas")
        print(f"  Rupas:          {format_value(data.get('shadbala_in_rupas', 0))} Rupas")
        print(f"  Rank:           {data.get('relative_rank', 'N/A')}")
        print()

if __name__ == "__main__":
    # Run Shadbala calculation
    our_results = run_shadbala_birth3()
    
    # Print detailed breakdown
    print_detailed_breakdown(our_results)
    
    # Print comparison table
    print_comparison_table(our_results, JHORA_REFERENCE)
    
    # Perform analysis
    analyze_structural_correctness(our_results, JHORA_REFERENCE)
    
    # Provide verdict
    provide_verdict(our_results, JHORA_REFERENCE)
    
    print()
    print("=" * 100)
    print("NOTE: To complete validation, add JHora reference data to JHORA_REFERENCE dictionary")
    print("=" * 100)
