#!/usr/bin/env python3
"""
Test Different D3 Hypotheses to Match JHora
Systematically tests various D3 calculation methods to find JHora's rule.
"""

import math

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Known JHora D3 outputs (Birth 3)
JHORA_D3_BIRTH3 = {
    "Moon": {"d1_sign": "Virgo", "d1_idx": 5, "deg": 11.3237, "div": 1, "jhora_d3": "Aquarius", "jhora_idx": 10},
    "Jupiter": {"d1_sign": "Taurus", "d1_idx": 1, "deg": 14.8664, "div": 1, "jhora_d3": "Cancer", "jhora_idx": 3}
}

# Our engine (Parāśara standard)
def our_engine_d3(sign_idx: int, deg_in_sign: float) -> int:
    l = int(math.floor(deg_in_sign / 10.0))
    if l >= 3: l = 2
    return (sign_idx + l * 4) % 12


def test_hypothesis(name: str, func, test_cases: list):
    """Test a hypothesis function against known JHora outputs."""
    print(f"\n{'='*80}")
    print(f"HYPOTHESIS: {name}")
    print(f"{'='*80}")
    
    all_match = True
    for case in test_cases:
        planet = case["planet"]
        d1_idx = case["d1_idx"]
        deg = case["deg"]
        expected_idx = case["jhora_idx"]
        
        result_idx = func(d1_idx, deg)
        result_sign = SIGN_NAMES[result_idx]
        expected_sign = SIGN_NAMES[expected_idx]
        match = "✅" if result_idx == expected_idx else "❌"
        
        if result_idx != expected_idx:
            all_match = False
        
        print(f"{planet:10} | D1: {SIGN_NAMES[d1_idx]:12} (idx {d1_idx:2}) | "
              f"Deg: {deg:7.4f}° | Div: {case['div']} | "
              f"Result: {result_sign:12} (idx {result_idx:2}) | "
              f"Expected: {expected_sign:12} (idx {expected_idx:2}) | {match}")
    
    print(f"\nStatus: {'✅ ALL MATCH' if all_match else '❌ MISMATCH'}")
    return all_match


# Hypothesis 1: Sign-specific offsets for division 1
def hypothesis_sign_specific_offsets(sign_idx: int, deg_in_sign: float) -> int:
    """Different offset per sign for division 1."""
    l = int(math.floor(deg_in_sign / 10.0))
    if l >= 3: l = 2
    
    if l == 0:
        return sign_idx  # Div 0: same sign
    elif l == 1:
        # Division 1: sign-specific offsets
        # Moon (Virgo, idx 5): needs +1 → offset = 5
        # Jupiter (Taurus, idx 1): needs -2 → offset = 11 (or -1)
        # This doesn't work - need lookup table
        sign_offsets_div1 = {
            5: 5,  # Virgo: +5 (9→10)
            1: 2,  # Taurus: +2 (5→3, wait that's +10 mod 12 = -2)
        }
        offset = sign_offsets_div1.get(sign_idx, 4)  # Default to +4
        return (sign_idx + offset) % 12
    else:  # l == 2
        return (sign_idx + 8) % 12  # Div 2: +8


# Hypothesis 2: Jagannatha Hora lookup table (traditional)
# Based on classical Drekkana where each sign has specific Drekkana lords
def hypothesis_jhora_lookup_table(sign_idx: int, deg_in_sign: float) -> int:
    """JHora D3 using lookup table based on sign and division."""
    l = int(math.floor(deg_in_sign / 10.0))
    if l >= 3: l = 2
    
    # Classical Drekkana lords (traditional method)
    # Each sign's three Drekkana are ruled by specific signs
    # This is a complex lookup - let me try a different approach
    
    # Try: For division 1, use different progression
    if l == 0:
        return sign_idx
    elif l == 1:
        # Maybe division 1 uses a different offset pattern
        # Test: Maybe it's based on sign element or modality?
        return (sign_idx + 4) % 12  # Default
    else:
        return (sign_idx + 8) % 12


# Hypothesis 3: Reverse direction for certain signs
def hypothesis_reverse_direction(sign_idx: int, deg_in_sign: float) -> int:
    """Some signs use reverse direction."""
    l = int(math.floor(deg_in_sign / 10.0))
    if l >= 3: l = 2
    
    if l == 0:
        return sign_idx
    elif l == 1:
        # Try: Even signs reverse, odd signs forward?
        # Virgo (5, odd): needs +1 → but our gives +4, so maybe +5?
        # Taurus (1, odd): needs -2 → our gives +4, so maybe +2?
        # This doesn't work either
        
        # Try: Maybe it's based on whether sign is movable/fixed/dual?
        # Virgo is dual, Taurus is fixed
        # This doesn't give a clear pattern
        
        # Let me try: Maybe division 1 uses a different multiplier?
        # Moon: (5 + 1*5) % 12 = 10 ✅
        # Jupiter: (1 + 1*2) % 12 = 3 ✅
        # But this is planet-specific, not universal
        
        # Actually, let me check if there's a sign-based lookup
        # For division 1, maybe each sign maps to a specific target?
        div1_map = {
            5: 10,  # Virgo → Aquarius
            1: 3,   # Taurus → Cancer
        }
        if sign_idx in div1_map:
            return div1_map[sign_idx]
        return (sign_idx + 4) % 12  # Default
    else:
        return (sign_idx + 8) % 12


# Hypothesis 4: Different division boundaries
def hypothesis_different_boundaries(sign_idx: int, deg_in_sign: float) -> int:
    """Maybe JHora uses different division boundaries."""
    # Try different division sizes
    # Moon: 11.3237° - maybe it's in division 2?
    # Jupiter: 14.8664° - maybe it's in division 2?
    
    # Test: Maybe division 1 is 0-12° instead of 0-10°?
    if deg_in_sign < 12.0:
        l = 0
    elif deg_in_sign < 24.0:
        l = 1
    else:
        l = 2
    
    if l == 0:
        return sign_idx
    elif l == 1:
        return (sign_idx + 4) % 12
    else:
        return (sign_idx + 8) % 12


# Hypothesis 5: Element-based offsets
def hypothesis_element_based(sign_idx: int, deg_in_sign: float) -> int:
    """Different offsets based on sign element."""
    l = int(math.floor(deg_in_sign / 10.0))
    if l >= 3: l = 2
    
    # Elements: Fire (0,4,8), Earth (1,5,9), Air (2,6,10), Water (3,7,11)
    element = sign_idx % 4
    
    if l == 0:
        return sign_idx
    elif l == 1:
        # Try element-based offsets
        element_offsets = {0: 4, 1: 2, 2: 4, 3: 4}  # Test values
        offset = element_offsets.get(element, 4)
        return (sign_idx + offset) % 12
    else:
        return (sign_idx + 8) % 12


def main():
    """Test all hypotheses."""
    test_cases = [
        {
            "planet": "Moon",
            "d1_sign": "Virgo",
            "d1_idx": 5,
            "deg": 11.3237,
            "div": 1,
            "jhora_d3": "Aquarius",
            "jhora_idx": 10
        },
        {
            "planet": "Jupiter",
            "d1_sign": "Taurus",
            "d1_idx": 1,
            "deg": 14.8664,
            "div": 1,
            "jhora_d3": "Cancer",
            "jhora_idx": 3
        }
    ]
    
    print("="*80)
    print("TESTING JHORA D3 HYPOTHESES")
    print("="*80)
    print("\nKnown JHora outputs (Birth 3):")
    print("  Moon (Virgo, 11.3237°, div 1): Aquarius (idx 10)")
    print("  Jupiter (Taurus, 14.8664°, div 1): Cancer (idx 3)")
    print("\nOur engine (Parāśara standard):")
    print("  Moon: (5 + 1*4) % 12 = 9 (Capricorn) ❌")
    print("  Jupiter: (1 + 1*4) % 12 = 5 (Virgo) ❌")
    
    # Test hypotheses
    hypotheses = [
        ("Sign-Specific Offsets (Lookup)", hypothesis_sign_specific_offsets),
        ("JHora Lookup Table", hypothesis_jhora_lookup_table),
        ("Reverse Direction", hypothesis_reverse_direction),
        ("Different Boundaries", hypothesis_different_boundaries),
        ("Element-Based", hypothesis_element_based),
    ]
    
    for name, func in hypotheses:
        test_hypothesis(name, func, test_cases)
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("\nNeed more data points to derive universal rule.")
    print("Current hypotheses require sign-specific logic, which violates")
    print("the requirement for ONE universal rule.")
    print("\nNext step: Get JHora D3 data for ALL planets in ALL three births")
    print("to identify the pattern.")


if __name__ == "__main__":
    main()

