"""
Test configuration and fixtures
"""

import pytest
import os
import sys
from pathlib import Path

# Add backend directory to Python path so 'src' module can be imported
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["DDB_TABLE_NAME"] = "test-representatives"
os.environ["LOG_LEVEL"] = "DEBUG"


# Test fixtures for Google Maps Geocoding API responses
@pytest.fixture
def successful_geocoding_response():
    """Fixture for successful Google Maps geocoding API response"""
    return [
        {
            "address_components": [
                {"long_name": "1600", "short_name": "1600", "types": ["street_number"]},
                {
                    "long_name": "Pennsylvania Avenue Northwest",
                    "short_name": "Pennsylvania Avenue NW",
                    "types": ["route"],
                },
                {
                    "long_name": "Northwest Washington",
                    "short_name": "Northwest Washington",
                    "types": ["neighborhood", "political"],
                },
                {
                    "long_name": "Washington",
                    "short_name": "Washington",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "District of Columbia",
                    "short_name": "DC",
                    "types": ["administrative_area_level_1", "political"],
                },
                {
                    "long_name": "United States",
                    "short_name": "US",
                    "types": ["country", "political"],
                },
                {"long_name": "20500", "short_name": "20500", "types": ["postal_code"]},
            ],
            "formatted_address": "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA",
            "geometry": {
                "location": {"lat": 38.8976763, "lng": -77.0365298},
                "location_type": "ROOFTOP",
                "viewport": {
                    "northeast": {"lat": 38.8990252802915, "lng": -77.0351808197085},
                    "southwest": {"lat": 38.8963273197085, "lng": -77.0378787802915},
                },
            },
            "place_id": "ChIJGVtI4by3t4kRr51d_Qm_x58",
            "types": ["street_address"],
        }
    ]


@pytest.fixture
def seattle_geocoding_response():
    """Fixture for Seattle address geocoding response"""
    return [
        {
            "address_components": [
                {
                    "long_name": "Pike Place Market",
                    "short_name": "Pike Place Market",
                    "types": ["establishment", "point_of_interest"],
                },
                {
                    "long_name": "Seattle",
                    "short_name": "Seattle",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "King County",
                    "short_name": "King County",
                    "types": ["administrative_area_level_2", "political"],
                },
                {
                    "long_name": "Washington",
                    "short_name": "WA",
                    "types": ["administrative_area_level_1", "political"],
                },
                {
                    "long_name": "United States",
                    "short_name": "US",
                    "types": ["country", "political"],
                },
            ],
            "formatted_address": "Pike Place Market, Seattle, WA, USA",
            "geometry": {
                "location": {"lat": 47.6105, "lng": -122.3115},
                "location_type": "GEOMETRIC_CENTER",
                "viewport": {
                    "northeast": {"lat": 47.6118489802915, "lng": -122.3101510197085},
                    "southwest": {"lat": 47.6091510197085, "lng": -122.3128489802915},
                },
            },
            "place_id": "ChIJ-bfVTh8VkFQRDZLQnmioK9s",
            "types": ["establishment", "point_of_interest"],
        }
    ]


@pytest.fixture
def empty_geocoding_response():
    """Fixture for geocoding response with no results (invalid address)"""
    return []


@pytest.fixture
def ambiguous_geocoding_response():
    """Fixture for geocoding response with multiple results"""
    return [
        {
            "address_components": [
                {
                    "long_name": "Springfield",
                    "short_name": "Springfield",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "Illinois",
                    "short_name": "IL",
                    "types": ["administrative_area_level_1", "political"],
                },
            ],
            "formatted_address": "Springfield, IL, USA",
            "geometry": {
                "location": {"lat": 39.7817213, "lng": -89.6501481},
                "location_type": "APPROXIMATE",
            },
            "place_id": "ChIJf2ymoNx_c4gRvCLvUUzUKuk",
            "types": ["locality", "political"],
        },
        {
            "address_components": [
                {
                    "long_name": "Springfield",
                    "short_name": "Springfield",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "Missouri",
                    "short_name": "MO",
                    "types": ["administrative_area_level_1", "political"],
                },
            ],
            "formatted_address": "Springfield, MO, USA",
            "geometry": {
                "location": {"lat": 37.2089572, "lng": -93.2922989},
                "location_type": "APPROXIMATE",
            },
            "place_id": "ChIJf9mn-md1yIcRik_0BKzrj9E",
            "types": ["locality", "political"],
        },
    ]


# Test fixtures for OpenStates /people.geo API responses
@pytest.fixture
def successful_openstates_geo_response():
    """Fixture for successful OpenStates geo API response with federal, state, and local representatives"""
    return {
        "results": [
            {
                "id": "ocd-person/550e8400-e29b-41d4-a716-446655440000",
                "name": "Adam Smith",
                "family_name": "Smith",
                "given_name": "Adam",
                "party": [{"name": "Democratic", "classification": "party"}],
                "current_role": {
                    "title": "Representative",
                    "org_classification": "upper",
                    "district": "9",
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us",
                        "name": "United States",
                        "classification": "country",
                    },
                },
                "contact_details": [
                    {"type": "email", "value": "https://adamsmith.house.gov/contact/email-me"}
                ],
                "image": "https://unitedstates.github.io/images/congress/450x550/S000510.jpg",
            },
            {
                "id": "ocd-person/660e8400-e29b-41d4-a716-446655440001",
                "name": "Patty Murray",
                "family_name": "Murray",
                "given_name": "Patty",
                "party": [{"name": "Democratic", "classification": "party"}],
                "current_role": {
                    "title": "Senator",
                    "org_classification": "upper",
                    "district": "Washington",
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us",
                        "name": "United States",
                        "classification": "country",
                    },
                },
                "contact_details": [
                    {"type": "email", "value": "https://www.murray.senate.gov/write-to-patty/"}
                ],
            },
            {
                "id": "ocd-person/770e8400-e29b-41d4-a716-446655440002",
                "name": "Maria Cantwell",
                "family_name": "Cantwell",
                "given_name": "Maria",
                "party": [{"name": "Democratic", "classification": "party"}],
                "current_role": {
                    "title": "Senator",
                    "org_classification": "upper",
                    "district": "Washington",
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us",
                        "name": "United States",
                        "classification": "country",
                    },
                },
            },
            {
                "id": "ocd-person/880e8400-e29b-41d4-a716-446655440003",
                "name": "Jay Inslee",
                "family_name": "Inslee",
                "given_name": "Jay",
                "party": [{"name": "Democratic", "classification": "party"}],
                "current_role": {
                    "title": "Governor",
                    "org_classification": "executive",
                    "district": "Washington",
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us/state:wa",
                        "name": "Washington",
                        "classification": "state",
                    },
                },
            },
            {
                "id": "ocd-person/990e8400-e29b-41d4-a716-446655440004",
                "name": "Jenny Durkan",
                "family_name": "Durkan",
                "given_name": "Jenny",
                "party": [{"name": "Nonpartisan", "classification": "party"}],
                "current_role": {
                    "title": "Mayor",
                    "org_classification": "executive",
                    "district": "Seattle",
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us/state:wa/place:seattle",
                        "name": "Seattle",
                        "classification": "municipality",
                    },
                },
            },
        ],
        "pagination": {"page": 1, "per_page": 20, "total_items": 5, "total_pages": 1},
    }


@pytest.fixture
def empty_openstates_geo_response():
    """Fixture for OpenStates geo API response with no representatives"""
    return {
        "results": [],
        "pagination": {"page": 1, "per_page": 20, "total_items": 0, "total_pages": 0},
    }


@pytest.fixture
def partial_openstates_geo_response():
    """Fixture for OpenStates geo API response with only federal representatives (no state/local)"""
    return {
        "results": [
            {
                "id": "ocd-person/550e8400-e29b-41d4-a716-446655440000",
                "name": "Adam Smith",
                "family_name": "Smith",
                "given_name": "Adam",
                "party": [{"name": "Republican", "classification": "party"}],
                "current_role": {
                    "title": "Representative",
                    "org_classification": "lower",
                    "district": "4",
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us",
                        "name": "United States",
                        "classification": "country",
                    },
                },
            }
        ],
        "pagination": {"page": 1, "per_page": 20, "total_items": 1, "total_pages": 1},
    }
