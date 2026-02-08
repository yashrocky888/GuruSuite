"""
Structured output safety lock.
LLM missing a section → structured still returns valid output.
"""

import pytest
from src.api.prediction_routes import _assemble_structured_output, REQUIRED_STRUCTURED_SECTIONS


def test_missing_sections_inject_empty():
    """Simulate LLM missing sections → all required keys present with safe values."""
    declarations = "Moon currently transits Leo in your 1st house."
    parsed = {"panchanga": "On this day...", "dasha": "Moon Mahadasha"}
    # Missing: chandra_bala, tara_bala, major_transits, dharmic_guidance, throne, moon_movement
    guidance_str, structured = _assemble_structured_output(declarations, parsed, {})
    for key in REQUIRED_STRUCTURED_SECTIONS:
        assert key in structured
        assert isinstance(structured[key], str)
        assert structured[key] is not None
    assert "On this day" in guidance_str
    assert "Moon Mahadasha" in guidance_str


def test_empty_parsed_still_valid():
    """Fully empty parsed → no failure, valid structure."""
    declarations = ""
    parsed = {}
    guidance_str, structured = _assemble_structured_output(declarations, parsed, {})
    for key in REQUIRED_STRUCTURED_SECTIONS:
        assert key in structured
        assert isinstance(structured[key], str)
        assert structured[key] is not None
    # throne is always set from get_canonical_throne (non-empty); others may be "" when parsed empty


def test_none_values_become_empty():
    """None values → empty string (except throne, always canonical)."""
    parsed = {k: None for k in REQUIRED_STRUCTURED_SECTIONS}
    _, structured = _assemble_structured_output("", parsed, {})
    for key in REQUIRED_STRUCTURED_SECTIONS:
        assert isinstance(structured[key], str)
        assert structured[key] is not None
    # throne always set from get_canonical_throne; others coerce None to ""
