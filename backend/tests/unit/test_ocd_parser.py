"""
Unit tests for OCD-ID parser utility (US2 - T027-T029)

Tests for parsing OCD identifiers and categorizing government levels.

TDD: These tests should FAIL until backend/src/utils/ocd_parser.py is implemented.
"""

import pytest


def test_parse_government_level_federal():
    """Test parsing federal-level OCD-IDs (T027)"""
    from src.utils.ocd_parser import parse_government_level

    # Test federal (country-level only)
    assert parse_government_level("ocd-division/country:us") == "federal"

    # Test congressional districts (federal)
    assert parse_government_level("ocd-division/country:us/state:wa/cd:7") == "federal"
    assert parse_government_level("ocd-division/country:us/state:ca/cd:12") == "federal"
    assert parse_government_level("ocd-division/country:us/state:ny/cd:10") == "federal"


def test_parse_government_level_state():
    """Test parsing state-level OCD-IDs (T028)"""
    from src.utils.ocd_parser import parse_government_level

    # Test state-wide (no district)
    assert parse_government_level("ocd-division/country:us/state:wa") == "state"
    assert parse_government_level("ocd-division/country:us/state:ca") == "state"
    assert parse_government_level("ocd-division/country:us/state:ny") == "state"

    # Test state legislative upper chamber (senate)
    assert parse_government_level("ocd-division/country:us/state:wa/sldu:43") == "state"
    assert parse_government_level("ocd-division/country:us/state:ca/sldu:15") == "state"

    # Test state legislative lower chamber (house)
    assert parse_government_level("ocd-division/country:us/state:wa/sldl:43") == "state"
    assert parse_government_level("ocd-division/country:us/state:tx/sldl:102") == "state"


def test_parse_government_level_local():
    """Test parsing local-level OCD-IDs (T029)"""
    from src.utils.ocd_parser import parse_government_level

    # Test county level
    assert parse_government_level("ocd-division/country:us/state:wa/county:king") == "local"
    assert parse_government_level("ocd-division/country:us/state:ca/county:los_angeles") == "local"

    # Test city/place level
    assert parse_government_level("ocd-division/country:us/state:wa/place:seattle") == "local"
    assert parse_government_level("ocd-division/country:us/state:ny/place:new_york") == "local"
    assert parse_government_level("ocd-division/country:us/state:ca/place:san_francisco") == "local"

    # Test nested local divisions
    assert (
        parse_government_level("ocd-division/country:us/state:wa/county:king/place:seattle")
        == "local"
    )


def test_parse_government_level_invalid_format():
    """Test error handling for invalid OCD-ID formats"""
    from src.utils.ocd_parser import parse_government_level

    # Test invalid formats
    with pytest.raises(ValueError):
        parse_government_level("not-an-ocd-id")

    with pytest.raises(ValueError):
        parse_government_level("ocd-division/country:ca")  # Non-US country

    with pytest.raises(ValueError):
        parse_government_level("")  # Empty string


def test_parse_ocd_id_components():
    """Test parsing OCD-ID into component parts"""
    from src.utils.ocd_parser import parse_ocd_id

    # Test federal
    result = parse_ocd_id("ocd-division/country:us")
    assert result["country"] == "us"
    assert result["government_level"] == "federal"
    assert "state" not in result

    # Test state
    result = parse_ocd_id("ocd-division/country:us/state:wa")
    assert result["country"] == "us"
    assert result["state"] == "wa"
    assert result["government_level"] == "state"

    # Test congressional district
    result = parse_ocd_id("ocd-division/country:us/state:wa/cd:7")
    assert result["country"] == "us"
    assert result["state"] == "wa"
    assert result["division_type"] == "cd"
    assert result["identifier"] == "7"
    assert result["government_level"] == "federal"

    # Test state legislative upper
    result = parse_ocd_id("ocd-division/country:us/state:ca/sldu:15")
    assert result["division_type"] == "sldu"
    assert result["identifier"] == "15"
    assert result["government_level"] == "state"

    # Test state legislative lower
    result = parse_ocd_id("ocd-division/country:us/state:wa/sldl:43")
    assert result["division_type"] == "sldl"
    assert result["identifier"] == "43"
    assert result["government_level"] == "state"

    # Test county
    result = parse_ocd_id("ocd-division/country:us/state:wa/county:king")
    assert result["division_type"] == "county"
    assert result["identifier"] == "king"
    assert result["government_level"] == "local"

    # Test place/city
    result = parse_ocd_id("ocd-division/country:us/state:wa/place:seattle")
    assert result["division_type"] == "place"
    assert result["identifier"] == "seattle"
    assert result["government_level"] == "local"


def test_parse_ocd_id_edge_cases():
    """Test edge cases in OCD-ID parsing"""
    from src.utils.ocd_parser import parse_ocd_id

    # Washington DC (special case - no state)
    result = parse_ocd_id("ocd-division/country:us/district:dc")
    assert result["government_level"] == "federal"

    # At-large congressional districts
    result = parse_ocd_id("ocd-division/country:us/state:mt/cd:0")
    assert result["identifier"] == "0"
    assert result["government_level"] == "federal"
