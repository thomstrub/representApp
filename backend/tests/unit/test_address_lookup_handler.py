"""
Unit tests for address lookup API handler (US3 - T046-T051)

Tests for the /representatives endpoint that integrates Google Civic and OpenStates.

TDD: These tests should FAIL until backend/src/handlers/api.py is updated for US3.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import time


def test_address_lookup_success():
    """Test successful address lookup returns representatives (T046)"""
    from src.handlers.address_lookup import lookup_representatives_by_address
    
    # Mock GoogleCivicClient
    mock_divisions = [
        {"ocd_id": "ocd-division/country:us", "name": "United States"},
        {"ocd_id": "ocd-division/country:us/state:wa", "name": "Washington"},
        {"ocd_id": "ocd-division/country:us/state:wa/cd:7", "name": "Congressional District 7"}
    ]
    
    # Mock OpenStatesClient
    mock_representatives = [
        {
            "id": "ocd-person/fed-001",
            "name": "John Federal",
            "office": "US Representative",
            "party": "Democratic",
            "email": "john@house.gov",
            "phone": "202-555-0100",
            "address": "Washington, DC",
            "website": "https://john.house.gov",
            "photo_url": "https://example.com/john.jpg",
            "government_level": "federal",
            "jurisdiction": "Congressional District 7"
        },
        {
            "id": "ocd-person/state-001",
            "name": "Jane State",
            "office": "State Senator",
            "party": "Republican",
            "email": "jane@leg.wa.gov",
            "phone": "360-555-0200",
            "address": "Olympia, WA",
            "website": "https://jane.wa.gov",
            "photo_url": "https://example.com/jane.jpg",
            "government_level": "state",
            "jurisdiction": "Washington"
        }
    ]
    
    with patch('src.handlers.address_lookup.get_api_key') as mock_get_key, \
         patch('src.handlers.address_lookup.GoogleCivicClient') as MockGoogleClient, \
         patch('src.handlers.address_lookup.OpenStatesClient') as MockOpenStatesClient:
        
        # Setup mocks
        mock_get_key.return_value = "test-key"
        
        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.return_value = mock_divisions
        
        mock_openstates = MockOpenStatesClient.return_value
        mock_openstates.get_representatives_by_division.return_value = mock_representatives
        
        # Act
        address = "1600 Pennsylvania Ave NW, Washington, DC 20500"
        result = lookup_representatives_by_address(address)
        
        # Assert
        assert result['address'] == address
        assert 'representatives' in result
        assert len(result['representatives']) >= 2
        
        # Check metadata
        assert 'metadata' in result
        assert result['metadata']['division_count'] == 3
        assert 'response_time_ms' in result['metadata']
        assert result['metadata']['response_time_ms'] > 0
        assert 'government_levels' in result['metadata']
        
        # Check representatives have correct structure
        rep = result['representatives'][0]
        assert 'id' in rep
        assert 'name' in rep
        assert 'office' in rep
        assert 'government_level' in rep


def test_address_lookup_missing_parameter():
    """Test API returns 400 when address parameter is missing (T047)"""
    from src.handlers.address_lookup import lookup_representatives_by_address
    from src.utils.errors import ApiException, ErrorCode
    
    # Missing address (None)
    with pytest.raises(ApiException) as exc_info:
        lookup_representatives_by_address(None)
    
    assert exc_info.value.code == ErrorCode.MISSING_PARAMETER
    assert exc_info.value.status_code == 400
    assert "address" in exc_info.value.message.lower()


def test_address_lookup_address_not_found():
    """Test API returns 404 when Google Civic finds no divisions (T048)"""
    from src.handlers.address_lookup import lookup_representatives_by_address
    from src.utils.errors import ApiException, ErrorCode
    
    with patch('src.handlers.address_lookup.get_api_key') as mock_get_key, \
         patch('src.handlers.address_lookup.GoogleCivicClient') as MockGoogleClient:
        
        mock_get_key.return_value = "test-key"
        
        # Mock GoogleCivicClient to raise ADDRESS_NOT_FOUND
        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.side_effect = ApiException(
            code=ErrorCode.ADDRESS_NOT_FOUND,
            message="No divisions found for address",
            status_code=404
        )
        
        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            lookup_representatives_by_address("123 Fake Street, Nowhere, XX 00000")
        
        assert exc_info.value.code == ErrorCode.ADDRESS_NOT_FOUND
        assert exc_info.value.status_code == 404


def test_address_lookup_external_service_error():
    """Test API returns 503 when external service fails (T049)"""
    from src.handlers.address_lookup import lookup_representatives_by_address
    from src.utils.errors import ApiException, ErrorCode
    
    with patch('src.handlers.address_lookup.get_api_key') as mock_get_key, \
         patch('src.handlers.address_lookup.GoogleCivicClient') as MockGoogleClient:
        
        mock_get_key.return_value = "test-key"
        
        # Mock GoogleCivicClient to raise external service error
        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.side_effect = ApiException(
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            message="Google Civic API unavailable",
            status_code=503
        )
        
        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            lookup_representatives_by_address("1600 Pennsylvania Ave NW")
        
        assert exc_info.value.code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503


def test_address_lookup_internal_error():
    """Test API returns 500 for unexpected internal errors (T050)"""
    from src.handlers.address_lookup import lookup_representatives_by_address
    from src.utils.errors import ApiException, ErrorCode
    
    with patch('src.handlers.address_lookup.get_api_key') as mock_get_key, \
         patch('src.handlers.address_lookup.GoogleCivicClient') as MockGoogleClient:
        
        mock_get_key.return_value = "test-key"
        
        # Mock unexpected exception
        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.side_effect = RuntimeError("Unexpected error")
        
        # Act & Assert - Should be caught and wrapped
        with pytest.raises(ApiException) as exc_info:
            lookup_representatives_by_address("Any address")
        
        assert exc_info.value.code == ErrorCode.INTERNAL_ERROR
        assert exc_info.value.status_code == 500


def test_address_lookup_partial_results_with_warnings():
    """Test API returns partial results with warnings when some divisions lack data (T051)"""
    from src.handlers.address_lookup import lookup_representatives_by_address
    
    # Mock divisions from Google Civic
    mock_divisions = [
        {"ocd_id": "ocd-division/country:us", "name": "United States"},
        {"ocd_id": "ocd-division/country:us/state:ca", "name": "California"},
        {"ocd_id": "ocd-division/country:us/state:ca/county:alameda", "name": "Alameda County"}
    ]
    
    # Mock OpenStates - some divisions have no data
    def mock_get_reps(ocd_id):
        if ocd_id == "ocd-division/country:us/state:ca/county:alameda":
            return []  # No county-level data
        return [
            {
                "id": f"ocd-person/test-{ocd_id[-3:]}",
                "name": "Test Representative",
                "office": "Senator",
                "party": "Democratic",
                "email": None,
                "phone": None,
                "address": None,
                "website": None,
                "photo_url": None,
                "government_level": "federal",
                "jurisdiction": "Test"
            }
        ]
    
    with patch('src.handlers.address_lookup.get_api_key') as mock_get_key, \
         patch('src.handlers.address_lookup.GoogleCivicClient') as MockGoogleClient, \
         patch('src.handlers.address_lookup.OpenStatesClient') as MockOpenStatesClient:
        
        mock_get_key.return_value = "test-key"
        
        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.return_value = mock_divisions
        
        mock_openstates = MockOpenStatesClient.return_value
        mock_openstates.get_representatives_by_division.side_effect = mock_get_reps
        
        # Act
        result = lookup_representatives_by_address("123 Main St, Oakland, CA 94612")
        
        # Assert - Should have representatives but also warnings
        assert 'representatives' in result
        assert len(result['representatives']) > 0
        
        # Check warnings array
        assert 'warnings' in result
        assert len(result['warnings']) > 0
        
        # Verify warning indicates missing data for county
        warning_found = any(
            "alameda" in w.lower() or "county" in w.lower()
            for w in result['warnings']
        )
        assert warning_found, "Expected warning about missing county data"


def test_representative_deduplication():
    """Test that duplicate representatives are removed"""
    from src.handlers.address_lookup import lookup_representatives_by_address
    
    mock_divisions = [
        {"ocd_id": "ocd-division/country:us/state:wa", "name": "Washington"},
        {"ocd_id": "ocd-division/country:us/state:wa/cd:7", "name": "CD 7"}
    ]
    
    # Same representative returned for multiple divisions
    duplicate_rep = {
        "id": "ocd-person/same-001",
        "name": "Same Person",
        "office": "US Senator",
        "party": "Independent",
        "email": "same@senate.gov",
        "phone": None,
        "address": None,
        "website": None,
        "photo_url": None,
        "government_level": "federal",
        "jurisdiction": "Washington"
    }
    
    with patch('src.handlers.address_lookup.get_api_key') as mock_get_key, \
         patch('src.handlers.address_lookup.GoogleCivicClient') as MockGoogleClient, \
         patch('src.handlers.address_lookup.OpenStatesClient') as MockOpenStatesClient:
        
        mock_get_key.return_value = "test-key"
        
        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.return_value = mock_divisions
        
        mock_openstates = MockOpenStatesClient.return_value
        # Return same rep for all divisions
        mock_openstates.get_representatives_by_division.return_value = [duplicate_rep]
        
        # Act
        result = lookup_representatives_by_address("Seattle, WA")
        
        # Assert - Should only have 1 representative despite 2 divisions
        assert len(result['representatives']) == 1
        assert result['representatives'][0]['id'] == "ocd-person/same-001"


def test_government_level_categorization():
    """Test representatives are categorized by government level"""
    from src.handlers.address_lookup import lookup_representatives_by_address
    
    mock_divisions = [
        {"ocd_id": "ocd-division/country:us", "name": "United States"},
        {"ocd_id": "ocd-division/country:us/state:ny", "name": "New York"}
    ]
    
    mock_reps = [
        {
            "id": "fed-001",
            "name": "Federal Rep",
            "office": "Senator",
            "party": None,
            "email": None,
            "phone": None,
            "address": None,
            "website": None,
            "photo_url": None,
            "government_level": "federal",
            "jurisdiction": "US"
        },
        {
            "id": "state-001",
            "name": "State Rep",
            "office": "State Senator",
            "party": None,
            "email": None,
            "phone": None,
            "address": None,
            "website": None,
            "photo_url": None,
            "government_level": "state",
            "jurisdiction": "NY"
        }
    ]
    
    with patch('src.handlers.address_lookup.get_api_key') as mock_get_key, \
         patch('src.handlers.address_lookup.GoogleCivicClient') as MockGoogleClient, \
         patch('src.handlers.address_lookup.OpenStatesClient') as MockOpenStatesClient:
        
        mock_get_key.return_value = "test-key"
        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.return_value = mock_divisions
        mock_openstates = MockOpenStatesClient.return_value
        mock_openstates.get_representatives_by_division.return_value = mock_reps
        
        # Act
        result = lookup_representatives_by_address("New York, NY")
        
        # Assert metadata includes government levels
        assert 'metadata' in result
        assert 'government_levels' in result['metadata']
        gov_levels = result['metadata']['government_levels']
        assert 'federal' in gov_levels
        assert 'state' in gov_levels
