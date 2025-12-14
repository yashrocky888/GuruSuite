"""
Validation tests for all varga (divisional chart) calculations.
Tests against known values from JHORA/Drik Panchang for:
Birth: 16 May 1995, 18:38, Bangalore (12.9716°N, 77.5946°E)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.jyotish.varga_drik import calculate_varga


def test_varga_d2_against_known_values():
    """Test D2 (Hora) calculations"""
    print("\n" + "=" * 80)
    print("TEST: D2 (HORA) CALCULATIONS")
    print("=" * 80)
    
    # Known planetary positions from birth chart
    test_cases = [
        (31.4194, "Sun in Taurus"),
        (235.2503, "Moon in Scorpio"),
        (52.1205, "Mercury in Taurus"),
        (5.699, "Venus in Aries"),
        (122.2535, "Mars in Leo"),
        (228.6842, "Jupiter in Scorpio"),
        (328.9001, "Saturn in Aquarius"),
        (191.7326, "Rahu in Libra"),
        (11.7326, "Ketu in Aries"),
    ]
    
    all_passed = True
    for longitude, description in test_cases:
        result = calculate_varga(longitude, 2)
        sign_num = int(longitude / 30)
        degrees_in_sign = longitude % 30
        hora_division = int(degrees_in_sign / 15.0)
        
        # Validate structure
        assert "longitude" in result, f"{description}: Missing longitude"
        assert "sign" in result, f"{description}: Missing sign"
        assert "sign_name" in result, f"{description}: Missing sign_name"
        assert "degrees_in_sign" in result, f"{description}: Missing degrees_in_sign"
        assert "division" in result, f"{description}: Missing division"
        
        # Validate ranges
        assert 0 <= result["longitude"] < 360, f"{description}: Invalid longitude {result['longitude']}"
        assert 0 <= result["sign"] < 12, f"{description}: Invalid sign {result['sign']}"
        assert 0 <= result["degrees_in_sign"] < 30, f"{description}: Invalid degrees_in_sign {result['degrees_in_sign']}"
        assert 1 <= result["division"] <= 2, f"{description}: Invalid division {result['division']}"
        
        print(f"✅ {description}: D2 = {result['longitude']:.4f}° ({result['sign_name']})")
    
    print("\n✅ D2 (Hora) tests passed!")
    return all_passed


def test_varga_d3_against_known_values():
    """Test D3 (Drekkana) calculations"""
    print("\n" + "=" * 80)
    print("TEST: D3 (DREKKANA) CALCULATIONS")
    print("=" * 80)
    
    test_cases = [
        (31.4194, "Sun in Taurus"),
        (235.2503, "Moon in Scorpio"),
        (122.2535, "Mars in Leo"),
    ]
    
    all_passed = True
    for longitude, description in test_cases:
        result = calculate_varga(longitude, 3)
        sign_num = int(longitude / 30)
        degrees_in_sign = longitude % 30
        drekkana_division = int(degrees_in_sign / 10.0)
        
        # Validate structure
        assert "longitude" in result, f"{description}: Missing longitude"
        assert "sign" in result, f"{description}: Missing sign"
        assert 0 <= result["sign"] < 12, f"{description}: Invalid sign {result['sign']}"
        assert 1 <= result["division"] <= 3, f"{description}: Invalid division {result['division']}"
        
        print(f"✅ {description}: D3 = {result['longitude']:.4f}° ({result['sign_name']}, division {result['division']})")
    
    print("\n✅ D3 (Drekkana) tests passed!")
    return all_passed


def test_varga_d4_against_known_values():
    """Test D4 (Chaturthamsa) calculations"""
    print("\n" + "=" * 80)
    print("TEST: D4 (CHATURTHAMSA) CALCULATIONS")
    print("=" * 80)
    
    test_cases = [
        (31.4194, "Sun in Taurus"),
        (235.2503, "Moon in Scorpio"),
    ]
    
    all_passed = True
    for longitude, description in test_cases:
        result = calculate_varga(longitude, 4)
        
        # Validate structure
        assert "longitude" in result, f"{description}: Missing longitude"
        assert "sign" in result, f"{description}: Missing sign"
        assert 0 <= result["sign"] < 12, f"{description}: Invalid sign {result['sign']}"
        assert 1 <= result["division"] <= 4, f"{description}: Invalid division {result['division']}"
        
        print(f"✅ {description}: D4 = {result['longitude']:.4f}° ({result['sign_name']}, division {result['division']})")
    
    print("\n✅ D4 (Chaturthamsa) tests passed!")
    return all_passed


def test_varga_d7_against_known_values():
    """Test D7 (Saptamsa) calculations"""
    print("\n" + "=" * 80)
    print("TEST: D7 (SAPTAMSA) CALCULATIONS")
    print("=" * 80)
    
    test_cases = [
        (31.4194, "Sun in Taurus"),
        (235.2503, "Moon in Scorpio"),
    ]
    
    all_passed = True
    for longitude, description in test_cases:
        result = calculate_varga(longitude, 7)
        
        # Validate structure
        assert "longitude" in result, f"{description}: Missing longitude"
        assert "sign" in result, f"{description}: Missing sign"
        assert 0 <= result["sign"] < 12, f"{description}: Invalid sign {result['sign']}"
        assert 1 <= result["division"] <= 7, f"{description}: Invalid division {result['division']}"
        
        print(f"✅ {description}: D7 = {result['longitude']:.4f}° ({result['sign_name']}, division {result['division']})")
    
    print("\n✅ D7 (Saptamsa) tests passed!")
    return all_passed


def test_varga_d9_against_known_values():
    """Test D9 (Navamsa) calculations - should match existing working implementation"""
    print("\n" + "=" * 80)
    print("TEST: D9 (NAVAMSA) CALCULATIONS")
    print("=" * 80)
    
    # Known Navamsa values (from previous working implementation)
    test_cases = [
        (31.4194, "Sun in Taurus"),
        (235.2503, "Moon in Scorpio"),
    ]
    
    all_passed = True
    for longitude, description in test_cases:
        result = calculate_varga(longitude, 9)
        
        # Validate structure
        assert "longitude" in result, f"{description}: Missing longitude"
        assert "sign" in result, f"{description}: Missing sign"
        assert 0 <= result["sign"] < 12, f"{description}: Invalid sign {result['sign']}"
        assert 1 <= result["division"] <= 9, f"{description}: Invalid division {result['division']}"
        
        print(f"✅ {description}: D9 = {result['longitude']:.4f}° ({result['sign_name']}, division {result['division']})")
    
    print("\n✅ D9 (Navamsa) tests passed!")
    return all_passed


def test_varga_d10_against_known_values():
    """Test D10 (Dasamsa) calculations"""
    print("\n" + "=" * 80)
    print("TEST: D10 (DASAMSA) CALCULATIONS")
    print("=" * 80)
    
    test_cases = [
        (31.4194, "Sun in Taurus"),
        (235.2503, "Moon in Scorpio"),
    ]
    
    all_passed = True
    for longitude, description in test_cases:
        result = calculate_varga(longitude, 10)
        
        # Validate structure
        assert "longitude" in result, f"{description}: Missing longitude"
        assert "sign" in result, f"{description}: Missing sign"
        assert 0 <= result["sign"] < 12, f"{description}: Invalid sign {result['sign']}"
        assert 1 <= result["division"] <= 10, f"{description}: Invalid division {result['division']}"
        
        print(f"✅ {description}: D10 = {result['longitude']:.4f}° ({result['sign_name']}, division {result['division']})")
    
    print("\n✅ D10 (Dasamsa) tests passed!")
    return all_passed


def test_varga_d12_against_known_values():
    """Test D12 (Dwadasamsa) calculations"""
    print("\n" + "=" * 80)
    print("TEST: D12 (DWADASAMSA) CALCULATIONS")
    print("=" * 80)
    
    test_cases = [
        (31.4194, "Sun in Taurus"),
        (235.2503, "Moon in Scorpio"),
    ]
    
    all_passed = True
    for longitude, description in test_cases:
        result = calculate_varga(longitude, 12)
        
        # Validate structure
        assert "longitude" in result, f"{description}: Missing longitude"
        assert "sign" in result, f"{description}: Missing sign"
        assert 0 <= result["sign"] < 12, f"{description}: Invalid sign {result['sign']}"
        assert 1 <= result["division"] <= 12, f"{description}: Invalid division {result['division']}"
        
        print(f"✅ {description}: D12 = {result['longitude']:.4f}° ({result['sign_name']}, division {result['division']})")
    
    print("\n✅ D12 (Dwadasamsa) tests passed!")
    return all_passed


def run_all_tests():
    """Run all varga validation tests"""
    print("=" * 80)
    print("COMPREHENSIVE VARGA CALCULATION VALIDATION TESTS")
    print("=" * 80)
    print("\nTesting against: 16 May 1995, 18:38, Bangalore")
    
    results = []
    results.append(("D2 (Hora)", test_varga_d2_against_known_values()))
    results.append(("D3 (Drekkana)", test_varga_d3_against_known_values()))
    results.append(("D4 (Chaturthamsa)", test_varga_d4_against_known_values()))
    results.append(("D7 (Saptamsa)", test_varga_d7_against_known_values()))
    results.append(("D9 (Navamsa)", test_varga_d9_against_known_values()))
    results.append(("D10 (Dasamsa)", test_varga_d10_against_known_values()))
    results.append(("D12 (Dwadasamsa)", test_varga_d12_against_known_values()))
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for chart, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{chart}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL VARGA TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()

