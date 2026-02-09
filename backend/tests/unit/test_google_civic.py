"""
Unit tests for Google Civic API client (US1 - T011-T014)

Tests for converting street addresses to OCD identifiers using Google Civic Information API.

TDD: These tests should FAIL until backend/src/services/google_civic.py is implemented.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests


def test_google_civic_client_initialization():
    """Test GoogleCivicClient initializes with API key (T011)"""
    from src.services.google_civic import GoogleCivicClient
    
    # Act
    client = GoogleCivicClient(api_key="test-key-123")
    
    # Assert
    assert client.api_key == "test-key-123"
    assert client.base_url == "https://www.googleapis.com/civicinfo/v2"


def test_lookup_divisions_success():
    """Test successful address lookup returns OCD-IDs (T012)"""
    from src.services.google_civic import GoogleCivicClient
    
    # Arrange
    mock_response = {
        "divisions": {
            "ocd-division/country:us": {
                "name": "United States"
            },
            "ocd-division/country:us/state:dc": {
                "name": "District of Columbia"
            },
            "ocd-division/country:us/state:dc/cd:98": {
                "name": "District of Columbia's At-Large Congressional District"
            }
        }
    }
    
    client = GoogleCivicClient(api_key="test-key")
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        # Act
        divisions = client.lookup_divisions("1600 Pennsylvania Ave NW, Washington, DC 20500")
        
        # Assert
        assert len(divisions) == 3
        assert divisions[0]['ocd_id'] == "ocd-division/country:us"
        assert divisions[0]['name'] == "United States"
        assert divisions[1]['ocd_id'] == "ocd-division/country:us/state:dc"
        assert divisions[2]['name'] == "District of Columbia's At-Large Congressional District"
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'params' in call_args.kwargs
        assert call_args.kwargs['params']['address'] == "1600 Pennsylvania Ave NW, Washington, DC 20500"
        assert call_args.kwargs['params']['key'] == "test-key"


def test_lookup_divisions_address_not_found():
    """Test handling of invalid/not found addresses (404) (T013)"""
    from src.services.google_civic import GoogleCivicClient
    from src.utils.errors import ApiException, ErrorCode
    
    client = GoogleCivicClient(api_key="test-key")
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": {
                "message": "No divisions found for the provided address"
            }
        }
        mock_get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            client.lookup_divisions("123 Fake Street, Nowhere, XX 00000")
        
        assert exc_info.value.code == ErrorCode.ADDRESS_NOT_FOUND
        assert exc_info.value.status_code == 404
        assert "No divisions found" in exc_info.value.message or "not found" in exc_info.value.message.lower()


def test_lookup_divisions_rate_limit_exceeded():
    """Test handling of rate limit errors (429) (T014)"""
    from src.services.google_civic import GoogleCivicClient
    from src.utils.errors import ApiException, ErrorCode
    
    client = GoogleCivicClient(api_key="test-key")
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {
                "message": "Rate limit exceeded"
            }
        }
        mock_get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            client.lookup_divisions("Any Address")
        
        assert exc_info.value.code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert exc_info.value.status_code == 503
        assert "rate limit" in exc_info.value.message.lower()


def test_lookup_divisions_request_timeout():
    """Test handling of network timeouts"""
    from src.services.google_civic import GoogleCivicClient
    from src.utils.errors import ApiException, ErrorCode
    
    client = GoogleCivicClient(api_key="test-key")
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            client.lookup_divisions("Any Address")
        
        assert exc_info.value.code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503
        assert "timeout" in exc_info.value.message.lower() or "unavailable" in exc_info.value.message.lower()


def test_lookup_divisions_connection_error():
    """Test handling of connection errors"""
    from src.services.google_civic import GoogleCivicClient
    from src.utils.errors import ApiException, ErrorCode
    
    client = GoogleCivicClient(api_key="test-key")
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")
        
        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            client.lookup_divisions("Any Address")
        
        assert exc_info.value.code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503


def test_lookup_divisions_empty_address():
    """Test validation of empty addresses"""
    from src.services.google_civic import GoogleCivicClient
    from src.utils.errors import ApiException, ErrorCode
    
    client = GoogleCivicClient(api_key="test-key")
    
    # Act & Assert
    with pytest.raises(ApiException) as exc_info:
        client.lookup_divisions("")
    
    assert exc_info.value.code == ErrorCode.INVALID_ADDRESS
    assert exc_info.value.status_code == 400


def test_lookup_divisions_address_too_long():
    """Test validation of addresses exceeding 500 characters"""
    from src.services.google_civic import GoogleCivicClient
    from src.utils.errors import ApiException, ErrorCode
    
    client = GoogleCivicClient(api_key="test-key")
    long_address = "A" * 501  # 501 characters
    
    # Act & Assert
    with pytest.raises(ApiException) as exc_info:
        client.lookup_divisions(long_address)
    
    assert exc_info.value.code == ErrorCode.INVALID_ADDRESS
    assert exc_info.value.status_code == 400
    assert "500" in exc_info.value.message
