#!/usr/bin/env python3
"""
BPHS Structural Verification Against UI Snapshot
Birth Detail 4: 2006-02-03, 22:30 IST, Bengaluru
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.jyotish.strength.shadbala import calculate_shadbala, SHADBALA_CONFIG
from src.utils.timezone import get_julian_day, local_to_utc
from datetime import datetime

# Birth Detail 4 (previously verified)
BIRTH_4 = {
    "date": "2006-02-03",
    "time": "22:30",
    "lat": 12.9716,
    "lon": 77.5946,
    "timezone": "Asia/Kolkata"
}

# UI Reference Ranking (from screenshot)
# Rank order: 1 = strongest, 7 = weakest
UI_REFERENCE_RANKING = {
    "Venus": 1,
    "Moon": 2,
    "Saturn": 3,
    "Mars": 4,
    "Sun": 5,
    "Mercury": 6,
    "Jupiter": 7
}

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def calculate_spearman_correlation(rank1, rank2):
    """Calculate Spearman rank correlation coefficient"""
    n = len(rank1)
    if n != len(rank2):
        return None
    
    # Calculate differences
    d_squared_sum = sum((rank1[p] - rank2[p]) ** 2 for p in rank1.keys() if p in rank2)
    
    # Spearman's formula: 1 - (6 * sum(d²)) / (n * (n² - 1))
    if n < 2:
        return 1.0
    
    correlation = 1.0 - (6.0 * d_squared_sum) / (n * (n * n - 1))
    return correlation

def analyze_ranking_differences(our_ranking, ui_ranking):
    """Analyze ranking differences"""
    differences = {}
    inversions = []
    
    for planet in PLANET_ORDER:
        if planet in our_ranking and planet in ui_ranking:
            our_rank = our_ranking[planet]
            ui_rank = ui_ranking[planet]
            diff = our_rank - ui_rank
            differences[planet] = diff
            
            if abs(diff) >= 3:
                inversions.append((planet, our_rank, ui_rank, diff))
    
    return differences, inversions

def categorize_match(our_rank, ui_rank):
    """Categorize match quality"""
    diff = abs(our_rank - ui_rank)
    if diff == 0:
        return "✅ Match"
    elif diff == 1:
        return "⚠️  Near (±1)"
    elif diff == 2:
        return "⚠️  Near (±2)"
    else:
        return "❌ Divergent (±3+)"

def check_dig_bala_sanity(shadbala_data):
    """Check Dig Bala directional sanity"""
    sanity_checks = []
    
    for planet in PLANET_ORDER:
        if planet not in shadbala_data:
            continue
        
        dig_bala = shadbala_data[planet].get('dig_bala', 0)
        
        # Dig Bala should be in [0, 60]
        if dig_bala < 0 or dig_bala > 60:
            sanity_checks.append(f"❌ {planet}: Dig Bala {dig_bala:.2f} outside [0, 60]")
        else:
            sanity_checks.append(f"✅ {planet}: Dig Bala {dig_bala:.2f} in range")
    
    return sanity_checks

def main():
    print("=" * 100)
    print("BPHS STRUCTURAL VERIFICATION - BIRTH DETAIL 4")
    print("=" * 100)
    print()
    
    # Verify SHADBALA_CONFIG
    print("SHADBALA_CONFIG Verification:")
    print(f"  KENDRADI_SCALE: {SHADBALA_CONFIG['KENDRADI_SCALE']} (Expected: 1.0)")
    print(f"  DIGBALA_SUN_MULTIPLIER: {SHADBALA_CONFIG['DIGBALA_SUN_MULTIPLIER']} (Expected: 1.0)")
    print(f"  SAPTAVARGAJA_DIVISOR: {SHADBALA_CONFIG['SAPTAVARGAJA_DIVISOR']} (Expected: 1.0)")
    print()
    
    if (SHADBALA_CONFIG['KENDRADI_SCALE'] != 1.0 or 
        SHADBALA_CONFIG['DIGBALA_SUN_MULTIPLIER'] != 1.0 or 
        SHADBALA_CONFIG['SAPTAVARGAJA_DIVISOR'] != 1.0):
        print("⚠️  WARNING: SHADBALA_CONFIG is not PURE BPHS!")
        print()
    
    # Parse date and time
    date_obj = datetime.strptime(BIRTH_4['date'], "%Y-%m-%d").date()
    time_parts = BIRTH_4['time'].split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    second = int(time_parts[2]) if len(time_parts) > 2 else 0
    
    # Create local datetime
    birth_dt_local = datetime.combine(
        date_obj,
        datetime.min.time().replace(hour=hour, minute=minute, second=second)
    )
    
    # Convert to UTC
    birth_dt_utc = local_to_utc(birth_dt_local, BIRTH_4['timezone'])
    
    # Get Julian Day
    jd = get_julian_day(birth_dt_utc)
    
    print(f"Birth Details:")
    print(f"  Date: {BIRTH_4['date']} {BIRTH_4['time']} {BIRTH_4['timezone']}")
    print(f"  Location: {BIRTH_4['lat']}, {BIRTH_4['lon']} (Bengaluru)")
    print(f"  Julian Day: {jd:.6f}")
    print()
    
    # Calculate Shadbala
    print("Calculating Shadbala (PURE BPHS STANDARD)...")
    try:
        result = calculate_shadbala(
            jd=jd,
            lat=BIRTH_4['lat'],
            lon=BIRTH_4['lon'],
            timezone=BIRTH_4['timezone']
        )
        print("✅ Calculation complete")
        print()
    except Exception as e:
        error_msg = str(e)
        if "seplm" in error_msg.lower() or "ephemeris" in error_msg.lower() or "file" in error_msg.lower():
            print("❌ ERROR: Swiss Ephemeris data files not found")
            print()
            print("To fix this, please:")
            print("1. Download Swiss Ephemeris data files from:")
            print("   https://www.astro.com/swisseph/swephinfo_e.htm")
            print("2. Extract to: apps/guru-api/ephe/")
            print("3. Required files: seplm*.se1 (planetary ephemeris)")
            print()
            print("Or install via package manager:")
            print("  macOS: brew install swisseph")
            print("  Linux: apt-get install swisseph-data")
            print()
            sys.exit(1)
        else:
            raise
    
    # Extract our ranking
    our_ranking = {}
    our_totals = {}
    for planet in PLANET_ORDER:
        if planet in result:
            our_ranking[planet] = result[planet].get('relative_rank', 999)
            our_totals[planet] = result[planet].get('total_shadbala', 0)
    
    # Sort by rank for display
    our_sorted = sorted(our_ranking.items(), key=lambda x: x[1])
    
    print("=" * 100)
    print("RANKING COMPARISON TABLE")
    print("=" * 100)
    print()
    print(f"{'Planet':<12} | {'Our Rank':<10} | {'Our Total':<12} | {'UI Rank':<10} | {'Status':<20}")
    print("-" * 100)
    
    for planet, our_rank in our_sorted:
        ui_rank = UI_REFERENCE_RANKING.get(planet, 'N/A')
        total = our_totals.get(planet, 0)
        status = categorize_match(our_rank, ui_rank) if ui_rank != 'N/A' else 'N/A'
        print(f"{planet:<12} | {our_rank:<10} | {total:>11.2f} | {ui_rank:<10} | {status:<20}")
    
    print()
    
    # Calculate rank correlation
    correlation = calculate_spearman_correlation(our_ranking, UI_REFERENCE_RANKING)
    
    # Analyze differences
    differences, inversions = analyze_ranking_differences(our_ranking, UI_REFERENCE_RANKING)
    
    print("=" * 100)
    print("ANALYSIS SUMMARY")
    print("=" * 100)
    print()
    
    print("Rank Correlation (Spearman):")
    if correlation is not None:
        print(f"  Coefficient: {correlation:.4f}")
        if correlation >= 0.9:
            print("  Interpretation: ✅ Strong positive correlation")
        elif correlation >= 0.7:
            print("  Interpretation: ⚠️  Moderate positive correlation")
        elif correlation >= 0.5:
            print("  Interpretation: ⚠️  Weak positive correlation")
        else:
            print("  Interpretation: ❌ Poor correlation")
    print()
    
    print("Rank Differences:")
    for planet in PLANET_ORDER:
        if planet in differences:
            diff = differences[planet]
            if diff == 0:
                print(f"  ✅ {planet}: Exact match")
            elif abs(diff) == 1:
                print(f"  ⚠️  {planet}: ±1 position (Our: {our_ranking[planet]}, UI: {UI_REFERENCE_RANKING[planet]})")
            elif abs(diff) == 2:
                print(f"  ⚠️  {planet}: ±2 positions (Our: {our_ranking[planet]}, UI: {UI_REFERENCE_RANKING[planet]})")
            else:
                print(f"  ❌ {planet}: ±{abs(diff)} positions (Our: {our_ranking[planet]}, UI: {UI_REFERENCE_RANKING[planet]})")
    print()
    
    if inversions:
        print("Major Inversions (±3+ positions):")
        for planet, our_rank, ui_rank, diff in inversions:
            print(f"  ❌ {planet}: Our Rank {our_rank} vs UI Rank {ui_rank} (diff: {diff:+d})")
        print()
    else:
        print("✅ No major inversions (±3+ positions)")
        print()
    
    # Top/Bottom group analysis
    our_top3 = [p for p, r in sorted(our_ranking.items(), key=lambda x: x[1])[:3]]
    our_bottom3 = [p for p, r in sorted(our_ranking.items(), key=lambda x: x[1], reverse=True)[:3]]
    ui_top3 = [p for p, r in sorted(UI_REFERENCE_RANKING.items(), key=lambda x: x[1])[:3]]
    ui_bottom3 = [p for p, r in sorted(UI_REFERENCE_RANKING.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    print("Top 3 (Strongest) Comparison:")
    top3_overlap = len(set(our_top3) & set(ui_top3))
    print(f"  Our Top 3: {our_top3}")
    print(f"  UI Top 3:  {ui_top3}")
    print(f"  Overlap: {top3_overlap}/3")
    if top3_overlap >= 2:
        print("  ✅ Strong alignment")
    elif top3_overlap == 1:
        print("  ⚠️  Partial alignment")
    else:
        print("  ❌ No alignment")
    print()
    
    print("Bottom 3 (Weakest) Comparison:")
    bottom3_overlap = len(set(our_bottom3) & set(ui_bottom3))
    print(f"  Our Bottom 3: {our_bottom3}")
    print(f"  UI Bottom 3:  {ui_bottom3}")
    print(f"  Overlap: {bottom3_overlap}/3")
    if bottom3_overlap >= 2:
        print("  ✅ Strong alignment")
    elif bottom3_overlap == 1:
        print("  ⚠️  Partial alignment")
    else:
        print("  ❌ No alignment")
    print()
    
    # Dig Bala sanity check
    print("Dig Bala Sanity Check:")
    dig_checks = check_dig_bala_sanity(result)
    for check in dig_checks:
        print(f"  {check}")
    print()
    
    # Final verdict
    print("=" * 100)
    print("FINAL VERDICT")
    print("=" * 100)
    print()
    
    # Determine verdict
    exact_matches = sum(1 for p in PLANET_ORDER if p in differences and differences[p] == 0)
    near_matches = sum(1 for p in PLANET_ORDER if p in differences and abs(differences[p]) <= 1)
    major_inversions_count = len(inversions)
    
    # Check for polarity reversal (strongest ↔ weakest)
    our_strongest = min(our_ranking.items(), key=lambda x: x[1])[0]
    our_weakest = max(our_ranking.items(), key=lambda x: x[1])[0]
    ui_strongest = min(UI_REFERENCE_RANKING.items(), key=lambda x: x[1])[0]
    ui_weakest = max(UI_REFERENCE_RANKING.items(), key=lambda x: x[1])[0]
    
    polarity_reversed = (our_strongest == ui_weakest and our_weakest == ui_strongest)
    
    if polarity_reversed:
        print("❌ FAIL: Polarity reversed (strongest ↔ weakest)")
        print(f"   Our strongest: {our_strongest} (rank {our_ranking[our_strongest]})")
        print(f"   UI strongest: {ui_strongest} (rank {UI_REFERENCE_RANKING[ui_strongest]})")
        print(f"   Our weakest: {our_weakest} (rank {our_ranking[our_weakest]})")
        print(f"   UI weakest: {ui_weakest} (rank {UI_REFERENCE_RANKING[ui_weakest]})")
    elif major_inversions_count == 0 and correlation and correlation >= 0.7:
        print("✅ PASS: Structure aligns well")
        print(f"   Exact matches: {exact_matches}/7")
        print(f"   Near matches (±1): {near_matches}/7")
        print(f"   Rank correlation: {correlation:.4f}")
    elif major_inversions_count <= 2 and correlation and correlation >= 0.5:
        print("⚠️  WARN: Minor variance but acceptable")
        print(f"   Exact matches: {exact_matches}/7")
        print(f"   Near matches (±1): {near_matches}/7")
        print(f"   Major inversions: {major_inversions_count}")
        print(f"   Rank correlation: {correlation:.4f}")
    else:
        print("❌ FAIL: Major structural divergence")
        print(f"   Exact matches: {exact_matches}/7")
        print(f"   Near matches (±1): {near_matches}/7")
        print(f"   Major inversions: {major_inversions_count}")
        if correlation:
            print(f"   Rank correlation: {correlation:.4f}")
    
    print()
    print("=" * 100)

if __name__ == "__main__":
    main()
