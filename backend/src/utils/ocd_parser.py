"""
OCD-ID parser utility for government level categorization

This module provides functions to parse Open Civic Data (OCD) identifiers
and determine government levels (federal, state, local).

Feature: 003-address-lookup (User Story 2 - T038-T039)
Reference: specs/001-api-integration-research/ocd-id-analysis.md
"""

import re
from typing import Dict, Optional


def parse_government_level(ocd_id: str) -> str:
    """
    Determine government level from OCD division identifier

    Args:
        ocd_id: OCD division identifier (e.g., "ocd-division/country:us/state:wa/cd:7")

    Returns:
        Government level: "federal", "state", or "local"

    Raises:
        ValueError: If OCD-ID format is invalid or not US-based

    Examples:
        >>> parse_government_level("ocd-division/country:us")
        "federal"
        >>> parse_government_level("ocd-division/country:us/state:wa/cd:7")
        "federal"
        >>> parse_government_level("ocd-division/country:us/state:wa")
        "state"
        >>> parse_government_level("ocd-division/country:us/state:wa/county:king")
        "local"

    Government Level Categorization (T039):
    - Federal: country:us OR congressional district (cd:)
    - State: state:XX OR state legislative (sldu:, sldl:)
    - Local: county:, place:, or other local subdivisions
    """
    # Validate format
    if not ocd_id or not ocd_id.startswith("ocd-division/"):
        raise ValueError(f"Invalid OCD-ID format: {ocd_id}")

    # Check for US country code
    if "country:us" not in ocd_id:
        raise ValueError(f"Non-US OCD-ID not supported: {ocd_id}")

    # Remove prefix for easier parsing
    parts = ocd_id.replace("ocd-division/", "")

    # Pattern 1: Federal level - Congressional district (cd:)
    if re.search(r"/cd:\d+", parts):
        return "federal"

    # Pattern 2: Federal level - Country only (no further divisions)
    # e.g., "country:us" or "country:us/district:dc"
    if parts == "country:us" or parts == "country:us/district:dc":
        return "federal"

    # Pattern 3: Local level - County
    if re.search(r"/county:[a-z_]+", parts):
        return "local"

    # Pattern 4: Local level - Place/City
    if re.search(r"/place:[a-z_]+", parts):
        return "local"

    # Pattern 5: State legislative - Upper chamber (sldu:)
    if re.search(r"/sldu:\d+", parts):
        return "state"

    # Pattern 6: State legislative - Lower chamber (sldl:)
    if re.search(r"/sldl:\d+", parts):
        return "state"

    # Pattern 7: State-wide (state:XX with no further divisions)
    if re.match(r"country:us/state:[a-z]{2}$", parts):
        return "state"

    # Default: If we have state but don't match other patterns, assume state
    if "/state:" in parts:
        return "state"

    # If none of the above, it's likely a local subdivision we don't recognize
    return "local"


def parse_ocd_id(ocd_id: str) -> Dict[str, Optional[str]]:
    """
    Parse OCD-ID into component parts

    Args:
        ocd_id: OCD division identifier

    Returns:
        Dictionary with parsed components:
        - country: Country code (e.g., 'us')
        - state: State abbreviation (e.g., 'wa') if present
        - division_type: Type of division ('cd', 'sldu', 'sldl', 'county', 'place') if present
        - identifier: District number or name if present
        - government_level: Determined government level ('federal', 'state', 'local')

    Raises:
        ValueError: If OCD-ID format is invalid

    Examples:
        >>> parse_ocd_id("ocd-division/country:us/state:wa/cd:7")
        {
            'country': 'us',
            'state': 'wa',
            'division_type': 'cd',
            'identifier': '7',
            'government_level': 'federal'
        }
    """
    # Validate format
    if not ocd_id or not ocd_id.startswith("ocd-division/"):
        raise ValueError(f"Invalid OCD-ID format: {ocd_id}")

    # Remove prefix and split into parts
    parts_str = ocd_id.replace("ocd-division/", "")
    parts = parts_str.split("/")

    # Parse components
    components = {}
    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            components[key] = value

    # Determine division type and identifier
    # Check for specific division types
    for div_type in ["cd", "sldu", "sldl", "county", "place", "district"]:
        if div_type in components:
            components["division_type"] = div_type
            components["identifier"] = components[div_type]
            break

    # Add government level
    components["government_level"] = parse_government_level(ocd_id)

    return components
