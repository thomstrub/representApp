"""
Unit tests for Google Maps Geocoding client

Tests written FIRST following TDD approach (Red-Green-Refactor).
These tests define the expected behavior of GoogleMapsClient before implementation.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import googlemaps


class TestGoogleMapsClient:
    """Test cases for GoogleMapsClient geocoding functionality"""
    
    def setup_method(self):
        """Set up test fixtures with proper mocking"""
        # Mock both parameter store and googlemaps client during setup
        with patch('src.utils.parameter_store.get_google_maps_api_key', return_value="test-api-key"):
            with patch('src.services.google_maps.googlemaps.Client') as mock_client_class:
                mock_client_class.return_value = Mock()
                from src.services.google_maps import GoogleMapsClient
                from src.utils.errors import ApiException, ErrorCode
                # Store classes for use in tests
                self.ApiException = ApiException
                self.ErrorCode = ErrorCode
                self.client = GoogleMapsClient()
        
    def test_successful_geocoding(self, successful_geocoding_response):
        """
        Test successful address geocoding returns coordinates
        
        RED PHASE: This test should FAIL since GoogleMapsClient doesn't exist yet
        """
        # Mock the googlemaps.Client and its geocode method
        with patch('src.services.google_maps.googlemaps.Client') as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance
            mock_client_instance.geocode.return_value = successful_geocoding_response
            
            # Override the client's googlemaps client with our mock
            self.client.client = mock_client_instance
            
            # Test the geocoding functionality
            result = self.client.geocode("1600 Pennsylvania Avenue NW, Washington, DC")
            
            # Verify the result structure
            assert result is not None
            assert 'latitude' in result
            assert 'longitude' in result
            assert 'formatted_address' in result
            
            # Verify coordinate values from fixture
            assert result['latitude'] == 38.8976763
            assert result['longitude'] == -77.0365298
            assert result['formatted_address'] == "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA"
            
            # Verify googlemaps client was called correctly
            mock_client_instance.geocode.assert_called_once_with(
                "1600 Pennsylvania Avenue NW, Washington, DC",
                timeout=5
            )
    
    def test_invalid_address_returns_empty_result(self, empty_geocoding_response):
        """
        Test that invalid/unfound address returns empty result without raising exception
        
        RED PHASE: Should FAIL - GoogleMapsClient.geocode() doesn't exist yet
        """
        mock_client_instance = Mock()
        mock_client_instance.geocode.return_value = empty_geocoding_response
        self.client.client = mock_client_instance
        
        # Test geocoding invalid address
        result = self.client.geocode("Invalid Address XYZ123NonExistent")
        
        # Should return None for invalid addresses (no exception raised)
        assert result is None
        
        # Verify the API was still called
        mock_client_instance.geocode.assert_called_once_with(
            "Invalid Address XYZ123NonExistent",
            timeout=5
        )
    
    def test_timeout_error_raises_api_exception(self):
        """
        Test that geocoding API timeout raises appropriate ApiException
        
        RED PHASE: Should FAIL - GoogleMapsClient doesn't exist yet
        """
        from googlemaps.exceptions import Timeout
        
        mock_client_instance = Mock()
        mock_client_instance.geocode.side_effect = Timeout("Request timed out")
        self.client.client = mock_client_instance
        
        # Should raise ApiException with EXTERNAL_SERVICE_ERROR
        with pytest.raises(self.ApiException) as exc_info:
            self.client.geocode("Any Address", timeout=5)
        
        # Verify exception details
        assert exc_info.value.code == self.ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503
        assert "timeout" in exc_info.value.message.lower()
        assert "Google Maps" in exc_info.value.message
    
    def test_authentication_error_raises_api_exception(self):
        """
        Test that geocoding API authentication error raises appropriate ApiException
        
        RED PHASE: Should FAIL - GoogleMapsClient doesn't exist yet
        """
        from googlemaps.exceptions import ApiError
        
        mock_client_instance = Mock()
        mock_client_instance.geocode.side_effect = ApiError("REQUEST_DENIED")
        self.client.client = mock_client_instance
        
        # Should raise ApiException with EXTERNAL_SERVICE_ERROR
        with pytest.raises(self.ApiException) as exc_info:
            self.client.geocode("Any Address")
        
        # Verify exception details
        assert exc_info.value.code == self.ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503
        assert "authentication" in exc_info.value.message.lower() or "api key" in exc_info.value.message.lower()
        assert "Google Maps" in exc_info.value.message
    
    def test_ambiguous_address_returns_first_result(self, ambiguous_geocoding_response):
        """
        Test that ambiguous address (multiple results) returns first result
        
        RED PHASE: Should FAIL - GoogleMapsClient doesn't exist yet
        """
        mock_client_instance = Mock()
        mock_client_instance.geocode.return_value = ambiguous_geocoding_response
        self.client.client = mock_client_instance
        
        # Test geocoding ambiguous address
        result = self.client.geocode("Springfield")  # Many Springfields in USA
        
        # Should return the first result
        assert result is not None
        assert result['latitude'] == 39.7817213  # Springfield, IL (first in fixture)
        assert result['longitude'] == -89.6501481
        assert result['formatted_address'] == "Springfield, IL, USA"
        
        # Verify the API was called
        mock_client_instance.geocode.assert_called_once_with(
            "Springfield",
            timeout=5
        )