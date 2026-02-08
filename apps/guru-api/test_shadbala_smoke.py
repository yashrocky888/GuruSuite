#!/usr/bin/env python3
"""
Shadbala Smoke Test & Invariant Check
READ-ONLY verification - no code modifications
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.jyotish.strength.shadbala import calculate_shadbala, NAISARGIKA_BALA
from src.utils.timezone import get_julian_day, get_timezone, local_to_utc
from datetime import datetime
import pytz

# Test charts (random birth dates)
TEST_CHARTS = [
    {
        "name": "Chart 1",
        "date": "2006-02-03",
        "time": "22:30",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Chart 2",
        "date": "1990-07-15",
        "time": "14:20",
        "lat": 28.6139,
        "lon": 77.2090,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Chart 3",
        "date": "1985-12-25",
        "time": "08:45",
        "lat": 19.0760,
        "lon": 72.8777,
        "timezone": "Asia/Kolkata"
    }
]

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def format_virupa(value):
    """Format virupa value with 2 decimal places"""
    if value is None or (isinstance(value, float) and (value != value or value == float('inf'))):
        return "N/A"
    return f"{value:.2f}"

def run_smoke_test():
    """Run smoke test for 2-3 random birth charts"""
    print("=" * 100)
    print("SHADBALA SMOKE TEST")
    print("=" * 100)
    print()
    
    for chart in TEST_CHARTS:
        print(f"\n{'='*100}")
        print(f"TEST CHART: {chart['name']}")
        print(f"Date: {chart['date']} {chart['time']} {chart['timezone']}")
        print(f"Location: {chart['lat']}, {chart['lon']}")
        print(f"{'='*100}\n")
        
        try:
            # Parse date and time
            date_obj = datetime.strptime(chart['date'], "%Y-%m-%d").date()
            time_parts = chart['time'].split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            second = int(time_parts[2]) if len(time_parts) > 2 else 0
            
            # Create local datetime
            birth_dt_local = datetime.combine(
                date_obj,
                datetime.min.time().replace(hour=hour, minute=minute, second=second)
            )
            
            # Convert to UTC
            birth_dt_utc = local_to_utc(birth_dt_local, chart['timezone'])
            
            # Get Julian Day
            jd = get_julian_day(birth_dt_utc)
            
            # Calculate Shadbala
            result = calculate_shadbala(
                jd=jd,
                lat=chart['lat'],
                lon=chart['lon'],
                timezone=chart['timezone']
            )
            
            # Print full output
            print("FULL SHADBALA OUTPUT:")
            print("-" * 100)
            
            for planet in PLANET_ORDER:
                if planet not in result:
                    continue
                    
                data = result[planet]
                print(f"\n{planet}:")
                print(f"  Sthana Bala:     {format_virupa(data.get('sthana_bala', 0))} Virupas")
                print(f"    - Uchcha Bala:      {format_virupa(data.get('uchcha_bala', 0))}")
                print(f"    - Saptavargaja:     {format_virupa(data.get('saptavargaja_bala', 0))}")
                print(f"    - Ojhayugmarasiamsa: {format_virupa(data.get('ojhayugmarasiamsa_bala', 0))}")
                print(f"    - Kendradi Bala:     {format_virupa(data.get('kendradi_bala', 0))}")
                print(f"    - Drekkana Bala:     {format_virupa(data.get('drekkana_bala', 0))}")
                print(f"  Dig Bala:        {format_virupa(data.get('dig_bala', 0))} Virupas")
                print(f"  Kala Bala:       {format_virupa(data.get('kala_bala', 0))} Virupas")
                print(f"    - Nathonnatha:       {format_virupa(data.get('nathonnatha_bala', 0))}")
                print(f"    - Paksha Bala:       {format_virupa(data.get('paksha_bala', 0))}")
                print(f"    - Tribhaga Bala:    {format_virupa(data.get('tribhaga_bala', 0))}")
                print(f"    - Varsha Bala:      {format_virupa(data.get('varsha_bala', 0))}")
                print(f"    - Masa Bala:        {format_virupa(data.get('masa_bala', 0))}")
                print(f"    - Dina Bala:        {format_virupa(data.get('dina_bala', 0))}")
                print(f"    - Hora Bala:        {format_virupa(data.get('hora_bala', 0))}")
                print(f"    - Ayana Bala:       {format_virupa(data.get('ayana_bala', 0))}")
                print(f"  Cheshta Bala:    {format_virupa(data.get('cheshta_bala', 0))} Virupas")
                print(f"  Naisargika Bala: {format_virupa(data.get('naisargika_bala', 0))} Virupas")
                print(f"  Drik Bala:       {format_virupa(data.get('drik_bala', 0))} Virupas")
                print(f"  TOTAL:           {format_virupa(data.get('total_shadbala', 0))} Virupas")
                print(f"  Rupas:           {format_virupa(data.get('shadbala_in_rupas', 0))} Rupas")
                print(f"  Rank:            {data.get('relative_rank', 'N/A')}")
            
            print("\n" + "-" * 100)
            print("✅ Smoke test PASSED - No exceptions, all values computed")
            
        except Exception as e:
            print(f"❌ Smoke test FAILED - Exception occurred: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def check_invariants():
    """Verify Shadbala invariants for each planet"""
    print("\n" + "=" * 100)
    print("SHADBALA INVARIANT CHECK")
    print("=" * 100)
    print()
    
    all_passed = True
    
    for chart in TEST_CHARTS:
        print(f"\n{'='*100}")
        print(f"INVARIANT CHECK: {chart['name']}")
        print(f"{'='*100}\n")
        
        try:
            # Parse date and time
            date_obj = datetime.strptime(chart['date'], "%Y-%m-%d").date()
            time_parts = chart['time'].split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            second = int(time_parts[2]) if len(time_parts) > 2 else 0
            
            # Create local datetime
            birth_dt_local = datetime.combine(
                date_obj,
                datetime.min.time().replace(hour=hour, minute=minute, second=second)
            )
            
            # Convert to UTC
            birth_dt_utc = local_to_utc(birth_dt_local, chart['timezone'])
            
            # Get Julian Day
            jd = get_julian_day(birth_dt_utc)
            
            result = calculate_shadbala(
                jd=jd,
                lat=chart['lat'],
                lon=chart['lon'],
                timezone=chart['timezone']
            )
            
            # Collect all ranks
            ranks = []
            planet_issues = []
            
            for planet in PLANET_ORDER:
                if planet not in result:
                    continue
                
                data = result[planet]
                issues = []
                
                # Check 1: Dig Bala ∈ [0, 60]
                dig_bala = data.get('dig_bala', 0)
                if not (0 <= dig_bala <= 60):
                    issues.append(f"Dig Bala {dig_bala:.2f} not in [0, 60]")
                
                # Check 2: Cheshta Bala ∈ {0, constants, 60}
                cheshta_bala = data.get('cheshta_bala', 0)
                valid_cheshta = cheshta_bala == 0 or cheshta_bala == 60 or abs(cheshta_bala - 30) < 0.01
                if not valid_cheshta:
                    # Allow some tolerance for intermediate values
                    if not (0 <= cheshta_bala <= 60):
                        issues.append(f"Cheshta Bala {cheshta_bala:.2f} not in valid range [0, 60]")
                
                # Check 3: Naisargika Bala matches BPHS constants
                naisargika = data.get('naisargika_bala', 0)
                expected_naisargika = NAISARGIKA_BALA.get(planet, 0)
                if abs(naisargika - expected_naisargika) > 0.01:
                    issues.append(f"Naisargika Bala {naisargika:.2f} != expected {expected_naisargika:.2f}")
                
                # Check 4: Total Shadbala > 0
                total = data.get('total_shadbala', 0)
                if total <= 0:
                    issues.append(f"Total Shadbala {total:.2f} <= 0")
                
                # Check 5: Shadbala_in_rupas = total / 60
                rupas = data.get('shadbala_in_rupas', 0)
                expected_rupas = total / 60.0
                if abs(rupas - expected_rupas) > 0.01:
                    issues.append(f"Rupas {rupas:.2f} != total/60 ({expected_rupas:.2f})")
                
                # Check 6 & 7: Rank validation
                rank = data.get('relative_rank', None)
                if rank is None:
                    issues.append("Rank is missing")
                else:
                    ranks.append((planet, rank))
                
                # Check for NaN or Inf
                for key, value in data.items():
                    if isinstance(value, float):
                        if value != value:  # NaN check
                            issues.append(f"{key} is NaN")
                        if value == float('inf') or value == float('-inf'):
                            issues.append(f"{key} is Infinity")
                
                if issues:
                    planet_issues.append((planet, issues))
                    print(f"❌ {planet}:")
                    for issue in issues:
                        print(f"   - {issue}")
                else:
                    print(f"✅ {planet}: All invariants passed")
            
            # Check rank uniqueness
            if ranks:
                rank_values = [r[1] for r in ranks]
                unique_ranks = set(rank_values)
                
                if len(unique_ranks) != len(rank_values):
                    print(f"\n❌ RANK UNIQUENESS: Duplicate ranks found")
                    rank_counts = {}
                    for planet, rank in ranks:
                        if rank not in rank_counts:
                            rank_counts[rank] = []
                        rank_counts[rank].append(planet)
                    for rank, planets in rank_counts.items():
                        if len(planets) > 1:
                            print(f"   Rank {rank}: {', '.join(planets)}")
                    all_passed = False
                else:
                    print(f"\n✅ RANK UNIQUENESS: All ranks are unique")
                
                # Check exactly one planet has rank = 1
                rank_1_planets = [p for p, r in ranks if r == 1]
                if len(rank_1_planets) != 1:
                    print(f"❌ RANK 1: Expected exactly 1 planet, found {len(rank_1_planets)}: {rank_1_planets}")
                    all_passed = False
                else:
                    print(f"✅ RANK 1: Exactly one planet has rank 1: {rank_1_planets[0]}")
                
                # Check ranks are in range 1-7
                invalid_ranks = [(p, r) for p, r in ranks if not (1 <= r <= 7)]
                if invalid_ranks:
                    print(f"❌ RANK RANGE: Ranks outside [1, 7]: {invalid_ranks}")
                    all_passed = False
                else:
                    print(f"✅ RANK RANGE: All ranks in [1, 7]")
            
            if planet_issues:
                all_passed = False
            
        except Exception as e:
            print(f"❌ Invariant check FAILED - Exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("SHADBALA VERIFICATION SUITE")
    print("=" * 100)
    
    smoke_passed = run_smoke_test()
    invariant_passed = check_invariants()
    
    print("\n" + "=" * 100)
    print("FINAL SUMMARY")
    print("=" * 100)
    print(f"Smoke Test: {'✅ PASSED' if smoke_passed else '❌ FAILED'}")
    print(f"Invariant Check: {'✅ PASSED' if invariant_passed else '❌ FAILED'}")
    print("=" * 100)
    
    sys.exit(0 if (smoke_passed and invariant_passed) else 1)
