#!/usr/bin/env python3
"""
Shadbala Golden Rupa Test — Backend validation.
Canonical input: 1990-04-14 12:00:00, Ujjain (23.1765, 75.7885), Asia/Kolkata.
Expected: Sun in Aries, 10th house, peak Dig Bala, high Ucha Bala.
"""
from datetime import datetime

from src.utils.timezone import get_julian_day, local_to_utc
from src.jyotish.kundli_engine import get_planet_positions, get_planet_house
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses
from src.jyotish.strength.shadbala import calculate_shadbala
from src.utils.converters import degrees_to_sign, get_sign_name

DOB = "1990-04-14"
TIME = "12:00:00"
LAT = 23.1765
LON = 75.7885
TZ = "Asia/Kolkata"

def main():
    # Build JD
    date_obj = datetime.strptime(DOB, "%Y-%m-%d").date()
    hour, minute, second = 12, 0, 0
    birth_dt_local = datetime.combine(
        date_obj,
        datetime.min.time().replace(hour=hour, minute=minute, second=second)
    )
    birth_dt_utc = local_to_utc(birth_dt_local, TZ)
    jd = get_julian_day(birth_dt_utc)

    # Planet positions and house
    planets = get_planet_positions(jd)
    sun_long = planets.get("Sun", 0.0)
    sign_num, deg_in_sign = degrees_to_sign(sun_long)
    sign_name = get_sign_name(sign_num)

    asc = get_ascendant(jd, LAT, LON)
    house_cusps = get_houses(jd, LAT, LON)
    sun_house = get_planet_house(sun_long, asc, house_cusps)

    # Shadbala
    shadbala = calculate_shadbala(jd, LAT, LON, timezone=TZ)
    sun = shadbala["Sun"]

    sthana = sun["sthana_bala"]
    uchcha = sun["sthana_bala_components"]["uchcha_bala"]
    dig = sun["dig_bala"]
    kala = sun["kala_bala"]
    total_rupas = sun["shadbala_in_rupas"]
    rank = sun["relative_rank"]

    # Rank #1 planet
    by_rupas = sorted(shadbala.items(), key=lambda x: x[1]["shadbala_in_rupas"], reverse=True)
    top_planet = by_rupas[0][0]
    top_rupas = by_rupas[0][1]["shadbala_in_rupas"]

    # Dig Bala: who has highest
    by_dig = sorted(shadbala.items(), key=lambda x: x[1]["dig_bala"], reverse=True)
    top_dig_planet = by_dig[0][0]
    top_dig = by_dig[0][1]["dig_bala"]

    print("=== Shadbala Golden Rupa Test — Result ===\n")
    print("Sun Position:")
    print(f"  Sign: {sign_name} (index {sign_num})")
    print(f"  Longitude: {sun_long:.4f}° ({sign_num*30 + deg_in_sign:.2f}° in sign)")
    print(f"  House: {sun_house}th")
    print()
    print("Sub-Bala Scores (Sun):")
    print(f"  Sthana Bala: {sthana}")
    print(f"    Uchcha Bala: {uchcha}")
    print(f"  Dig Bala: {dig}")
    print(f"  Kaala Bala: {kala}")
    print()
    print("Total Shadbala:")
    print(f"  {total_rupas} Rupas")
    print(f"  Rank among planets: #{rank}")
    print(f"  Strongest planet by Rupas: {top_planet} ({top_rupas} Rupas)")
    print(f"  Highest Dig Bala: {top_dig_planet} ({top_dig})")
    print()

    # Hard assertions
    fail_reasons = []
    if total_rupas <= 1.25:
        fail_reasons.append("total_rupas <= 1.25")
    if dig < 55:
        fail_reasons.append("dig_bala < 55")
    if sthana <= 100:
        fail_reasons.append("sthana_bala <= 100")
    if rank != 1:
        fail_reasons.append("Sun not ranked #1")
    if sign_name != "Aries":
        fail_reasons.append("Sun not in Aries (test premise)")
    if uchcha < 55:
        fail_reasons.append("uchcha_bala < 55")
    if top_dig_planet != "Sun":
        fail_reasons.append("Sun does not have highest Dig Bala")

    verdict = "FAIL" if fail_reasons else "PASS"
    print("Verdict:", verdict)
    if fail_reasons:
        print("Reasons:", ", ".join(fail_reasons))


if __name__ == "__main__":
    main()
