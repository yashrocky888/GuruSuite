"""
Golden test for D24, D30, D40 varga calculations.
Tests against Prokerala ground truth data.

Test Birth: 16-05-1995, 18:38 IST, Bangalore (Lahiri Ayanamsa)
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from jyotish.varga_drik import calculate_varga_sign

# Ground truth from Prokerala (LOCKED)
PROKERALA_GROUND_TRUTH = {
    "D24": {
        "Ascendant": 4,   # Leo
        "Sun": 4,         # Leo
        "Moon": 0,        # Aries
        "Mars": 5,        # Virgo
        "Mercury": 8,     # Sagittarius
        "Jupiter": 5,     # Virgo
        "Venus": 8,       # Sagittarius
        "Saturn": 2,      # Gemini
        "Rahu": 11,       # Pisces
        "Ketu": 11,       # Pisces
    },
    "D27": {
        "Ascendant": 11,  # Pisces
        "Sun": 4,         # Leo
        "Moon": 7,        # Scorpio
        "Mars": 2,        # Gemini
        "Mercury": 10,    # Aquarius
        "Jupiter": 1,     # Taurus
        "Venus": 5,       # Virgo
        "Saturn": 8,      # Sagittarius
        "Rahu": 3,        # Cancer
        "Ketu": 9,        # Capricorn
    },
    "D30": {
        "Ascendant": 1,   # Taurus
        "Sun": 1,         # Taurus
        "Moon": 7,        # Scorpio
        "Mars": 0,        # Aries
        "Mercury": 9,     # Capricorn
        "Jupiter": 11,    # Pisces
        "Venus": 10,      # Aquarius
        "Saturn": 6,      # Libra
        "Rahu": 8,        # Sagittarius
        "Ketu": 8,        # Sagittarius
    },
    "D40": {
        "Ascendant": 9,   # Capricorn
        "Sun": 8,         # Sagittarius
        "Moon": 0,        # Aries
        "Mars": 9,        # Capricorn
        "Mercury": 11,    # Pisces
        "Jupiter": 6,     # Libra
        "Venus": 8,       # Sagittarius
        "Saturn": 2,     # Gemini
        "Rahu": 1,        # Taurus
        "Ketu": 1,        # Taurus
    },
    "D45": {
        "Ascendant": 7,   # Scorpio
        "Sun": 6,         # Libra
        "Moon": 5,        # Virgo
        "Mars": 7,        # Scorpio
        "Mercury": 1,     # Taurus
        "Jupiter": 8,     # Sagittarius
        "Venus": 8,       # Sagittarius
        "Saturn": 11,     # Pisces
        "Rahu": 4,        # Leo
        "Ketu": 4,        # Leo
    },
    "D60": {
        "Ascendant": 11,  # Pisces
        "Sun": 3,         # Cancer
        "Moon": 9,        # Capricorn
        "Mars": 8,        # Sagittarius
        "Mercury": 9,     # Capricorn
        "Jupiter": 8,     # Sagittarius
        "Venus": 11,      # Pisces
        "Saturn": 7,      # Scorpio
        "Rahu": 3,        # Cancer
        "Ketu": 9,        # Capricorn
    },
}

# D1 data for test birth (16-05-1995, 18:38 IST, Bangalore)
D1_DATA = {
    "Ascendant": {"sign_index": 7, "long_in_sign": 2.2799},   # Scorpio
    "Sun": {"sign_index": 1, "long_in_sign": 1.4138},         # Taurus
    "Moon": {"sign_index": 7, "long_in_sign": 25.2501},       # Scorpio
    "Mars": {"sign_index": 4, "long_in_sign": 2.2504},        # Leo
    "Mercury": {"sign_index": 1, "long_in_sign": 22.1178},   # Taurus
    "Jupiter": {"sign_index": 7, "long_in_sign": 18.6872},   # Scorpio
    "Venus": {"sign_index": 0, "long_in_sign": 5.6886},      # Aries
    "Saturn": {"sign_index": 10, "long_in_sign": 28.8956},   # Aquarius
    "Rahu": {"sign_index": 6, "long_in_sign": 10.7944},      # Libra
    "Ketu": {"sign_index": 0, "long_in_sign": 10.7944},      # Aries
}


class TestProkeralaGolden:
    """Golden tests against Prokerala ground truth"""
    
    @pytest.mark.parametrize("varga", ["D24", "D27", "D30", "D40", "D45", "D60"])
    def test_varga_against_prokerala(self, varga):
        """Test each varga against Prokerala ground truth"""
        ground_truth = PROKERALA_GROUND_TRUTH[varga]
        mismatches = []
        
        for planet_name, d1_info in D1_DATA.items():
            sign_index = d1_info["sign_index"]
            long_in_sign = d1_info["long_in_sign"]
            expected = ground_truth[planet_name]
            
            result = calculate_varga_sign(sign_index, long_in_sign, varga)
            
            if result != expected:
                mismatches.append(
                    f"{planet_name}: got {result} (sign {result}), expected {expected} (sign {expected})"
                )
        
        if mismatches:
            pytest.fail(
                f"{varga} mismatches with Prokerala:\n" + "\n".join(mismatches)
            )
    
    def test_d24_all_planets(self):
        """Test D24 against all planets"""
        varga = "D24"
        ground_truth = PROKERALA_GROUND_TRUTH[varga]
        
        for planet_name, d1_info in D1_DATA.items():
            sign_index = d1_info["sign_index"]
            long_in_sign = d1_info["long_in_sign"]
            expected = ground_truth[planet_name]
            
            result = calculate_varga_sign(sign_index, long_in_sign, varga)
            assert result == expected, (
                f"D24 {planet_name}: got sign_index {result}, expected {expected}"
            )
    
    def test_d30_all_planets(self):
        """Test D30 against all planets"""
        varga = "D30"
        ground_truth = PROKERALA_GROUND_TRUTH[varga]
        
        for planet_name, d1_info in D1_DATA.items():
            sign_index = d1_info["sign_index"]
            long_in_sign = d1_info["long_in_sign"]
            expected = ground_truth[planet_name]
            
            result = calculate_varga_sign(sign_index, long_in_sign, varga)
            assert result == expected, (
                f"D30 {planet_name}: got sign_index {result}, expected {expected}"
            )
    
    def test_d40_all_planets(self):
        """Test D40 against all planets"""
        varga = "D40"
        ground_truth = PROKERALA_GROUND_TRUTH[varga]
        
        for planet_name, d1_info in D1_DATA.items():
            sign_index = d1_info["sign_index"]
            long_in_sign = d1_info["long_in_sign"]
            expected = ground_truth[planet_name]
            
            result = calculate_varga_sign(sign_index, long_in_sign, varga)
            assert result == expected, (
                f"D40 {planet_name}: got sign_index {result}, expected {expected}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

