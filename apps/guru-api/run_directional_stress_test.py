#!/usr/bin/env python3
"""
Shadbala Directional Stress Test — Sunset Saturn Case.
Input: 1985-11-20 17:30:00, New Delhi (28.61, 77.21), Asia/Kolkata.
Validates Dig Bala (house-based) per BPHS Ch 27.
"""
from datetime import datetime

from src.utils.timezone import get_julian_day, local_to_utc
from src.jyotish.kundli_engine import get_planet_positions, get_planet_house
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses
from src.jyotish.strength.shadbala import calculate_shadbala

DOB = "1985-11-20"
TIME = "17:30:00"
LAT = 28.61
LON = 77.21
TZ = "Asia/Kolkata"

def main():
    date_obj = datetime.strptime(DOB, "%Y-%m-%d").date()
    hour, minute, second = 17, 30, 0
    birth_dt_local = datetime.combine(
        date_obj,
        datetime.min.time().replace(hour=hour, minute=minute, second=second)
    )
    birth_dt_utc = local_to_utc(birth_dt_local, TZ)
    jd = get_julian_day(birth_dt_utc)

    planets = get_planet_positions(jd)
    asc = get_ascendant(jd, LAT, LON)
    house_cusps = get_houses(jd, LAT, LON)
    shadbala = calculate_shadbala(jd, LAT, LON, timezone=TZ)

    # Rahu/Ketu: must not appear in shadbala (BPHS no Dig Bala)
    rahu_ketu_in_result = [p for p in ["Rahu", "Ketu"] if p in shadbala]
    if rahu_ketu_in_result:
        print("FAIL: Rahu/Ketu in shadbala result:", rahu_ketu_in_result)
    else:
        print("Rahu/Ketu: not in Shadbala (BPHS compliant)")

    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    print("\n| Planet   | House | Dig Bala (Virupas) | Total (Rupas) |")
    print("|----------|-------|--------------------|---------------|")
    for p in order:
        if p not in planets or p not in shadbala:
            continue
        house = get_planet_house(planets[p], asc, house_cusps)
        dig = shadbala[p]["dig_bala"]
        rupas = shadbala[p]["shadbala_in_rupas"]
        print(f"| {p:<8} | {house:>5} | {dig:>18.2f} | {rupas:>13.2f} |")

    # Assertions
    saturn_dig = shadbala["Saturn"]["dig_bala"]
    mercury_dig = shadbala["Mercury"]["dig_bala"]
    jupiter_dig = shadbala["Jupiter"]["dig_bala"]
    sun_dig = shadbala["Sun"]["dig_bala"]
    dig_values = [(name, shadbala[name]["dig_bala"]) for name in order if name in shadbala]
    highest_dig_planet = max(dig_values, key=lambda x: x[1])[0]

    print("\n--- Assertions ---")
    print(f"Saturn has highest Dig Bala: {highest_dig_planet == 'Saturn'} (highest: {highest_dig_planet} = {saturn_dig})")
    print(f"Mercury Dig ~0-5: {0 <= mercury_dig <= 5} (actual: {mercury_dig})")
    print(f"Jupiter Dig ~0-5: {0 <= jupiter_dig <= 5} (actual: {jupiter_dig})")
    print(f"Saturn Dig peak 55-60: {55 <= saturn_dig <= 60} (actual: {saturn_dig})")
    print(f"Rahu/Ketu no Dig Bala: {len(rahu_ketu_in_result) == 0}")


if __name__ == "__main__":
    main()
