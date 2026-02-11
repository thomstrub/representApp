"""
Unit tests for address lookup API handler (User Story 3 - T043)

Tests for the /representatives endpoint using geolocation flow:
address → Google Maps geocoding → OpenStates geo endpoint

TDD: These tests should FAIL until AddressLookupHandler is updated for new geolocation flow.
Updated from Google Civic API to Google Maps + OpenStates geo endpoint integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from moto import mock_aws
import boto3


@mock_aws
@patch("src.services.google_maps.GoogleMapsClient")
@patch("src.services.openstates.OpenStatesClient")
def test_address_lookup_success_geolocation_flow(MockOpenStatesClient, MockGoogleMapsClient):
    """Test successful address lookup using new geolocation flow (T043)"""
    # Setup mock Parameter Store
    ssm_client = boto3.client("ssm", region_name="us-east-1")
    ssm_client.put_parameter(
        Name="/represent-app/google-maps-api-key", Value="mock-google-maps-key", Type="SecureString"
    )
    ssm_client.put_parameter(
        Name="/represent-app/openstates-api-key", Value="mock-openstates-key", Type="SecureString"
    )

    from src.handlers.address_lookup import AddressLookupHandler

    # Mock Google Maps geocoding response
    mock_geocoding_result = {
        "latitude": 38.8976763,
        "longitude": -77.0365298,
        "formatted_address": "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA",
    }

    # Mock OpenStates geo response
    mock_openstates_reps = [
        {
            "id": "ocd-person/president-001",
            "name": "Joe Biden",
            "party": "Democratic",
            "current_role": {
                "title": "President",
                "district": "United States",
                "division_id": "ocd-division/country:us",
            },
            "jurisdiction": {
                "id": "ocd-jurisdiction/country:us/government",
                "name": "United States",
                "classification": "country",
            },
            "email": "president@whitehouse.gov",
            "image": "https://example.com/biden.jpg",
        }
    ]

    # Setup mocks
    MockGoogleMapsClient = Mock()
    mock_gmaps_instance = Mock()
    MockGoogleMapsClient.return_value = mock_gmaps_instance
    mock_gmaps_instance.geocode.return_value = mock_geocoding_result

    MockOpenStatesClient = Mock()
    mock_openstates_instance = Mock()
    MockOpenStatesClient.return_value = mock_openstates_instance
    mock_openstates_instance.get_representatives_by_coordinates.return_value = mock_openstates_reps

    with (
        patch("src.handlers.address_lookup.GoogleMapsClient", MockGoogleMapsClient),
        patch("src.handlers.address_lookup.OpenStatesClient", MockOpenStatesClient),
    ):

        # Act
        handler = AddressLookupHandler()
        result = handler.handle("1600 Pennsylvania Avenue NW, Washington, DC")

        # Assert structure
        assert "representatives" in result
        assert "metadata" in result
        assert "warnings" in result

        # Assert representatives grouped by government level
        representatives = result["representatives"]
        assert "federal" in representatives
        assert "state" in representatives
        assert "local" in representatives

        # Assert federal representative found
        assert len(representatives["federal"]) == 1
        federal_rep = representatives["federal"][0]
        assert federal_rep["name"] == "Joe Biden"
        assert federal_rep["position"] == "President"
        assert federal_rep["state"] == "United States"

        # Assert metadata includes geocoding information
        metadata = result["metadata"]
        assert metadata["address"] == "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA"
        assert metadata["coordinates"]["latitude"] == 38.8976763
        assert metadata["coordinates"]["longitude"] == -77.0365298
        assert metadata["total_count"] == 1
        assert "federal" in metadata["government_levels"]

        # Verify API calls made correctly
        mock_gmaps_instance.geocode.assert_called_once_with(
            "1600 Pennsylvania Avenue NW, Washington, DC", timeout=5
        )
        mock_openstates_instance.get_representatives_by_coordinates.assert_called_once_with(
            38.8976763, -77.0365298
        )


@mock_aws
@patch("src.services.google_maps.GoogleMapsClient")
@patch("src.services.openstates.OpenStatesClient")
def test_address_lookup_missing_parameter(MockOpenStatesClient, MockGoogleMapsClient):
    """Test handler returns appropriate error when address parameter is missing (T043)"""
    from src.handlers.address_lookup import AddressLookupHandler
    from src.utils.errors import ApiException, ErrorCode

    # Setup mock Parameter Store
    ssm_client = boto3.client("ssm", region_name="us-east-1")
    ssm_client.put_parameter(
        Name="/represent-app/google-maps-api-key",
        Value="mock-google-maps-key",
        Type="SecureString",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/represent-app/openstates-api-key",
        Value="mock-openstates-key",
        Type="SecureString",
        Overwrite=True,
    )

    # Mock both clients
    MockGoogleMapsClient = Mock()
    mock_gmaps_instance = Mock()
    MockGoogleMapsClient.return_value = mock_gmaps_instance

    MockOpenStatesClient = Mock()
    mock_openstates_instance = Mock()
    MockOpenStatesClient.return_value = mock_openstates_instance

    with (
        patch("src.handlers.address_lookup.GoogleMapsClient", MockGoogleMapsClient),
        patch("src.handlers.address_lookup.OpenStatesClient", MockOpenStatesClient),
    ):
        # Act & Assert
        handler = AddressLookupHandler()
        with pytest.raises(ApiException) as exc_info:
            handler.handle(None)

        assert exc_info.value.code == ErrorCode.MISSING_PARAMETER
        assert exc_info.value.status_code == 400
        assert "address" in exc_info.value.message.lower()

        # Test empty string
        with pytest.raises(ApiException) as exc_info:
            handler.handle("")

        assert exc_info.value.code == ErrorCode.MISSING_PARAMETER
        assert exc_info.value.status_code == 400


@mock_aws
@patch("src.services.google_maps.GoogleMapsClient")
@patch("src.services.openstates.OpenStatesClient")
def test_address_lookup_geocoding_failure(MockOpenStatesClient, MockGoogleMapsClient):
    """Test handler returns 400 when address cannot be geocoded (T043)"""
    # Setup mock Parameter Store
    ssm_client = boto3.client("ssm", region_name="us-east-1")
    ssm_client.put_parameter(
        Name="/represent-app/google-maps-api-key", Value="mock-google-maps-key", Type="SecureString"
    )
    ssm_client.put_parameter(
        Name="/represent-app/openstates-api-key", Value="mock-openstates-key", Type="SecureString"
    )

    from src.handlers.address_lookup import AddressLookupHandler
    from src.utils.errors import ApiException, ErrorCode

    # Mock Google Maps to return None (no geocoding results)
    MockGoogleMapsClient = Mock()
    mock_gmaps_instance = Mock()
    MockGoogleMapsClient.return_value = mock_gmaps_instance
    mock_gmaps_instance.geocode.return_value = None

    # Mock OpenStatesClient
    MockOpenStatesClient = Mock()
    mock_openstates_instance = Mock()
    MockOpenStatesClient.return_value = mock_openstates_instance

    with (
        patch("src.handlers.address_lookup.GoogleMapsClient", MockGoogleMapsClient),
        patch("src.handlers.address_lookup.OpenStatesClient", MockOpenStatesClient),
    ):
        handler = AddressLookupHandler()

        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            handler.handle("InvalidAddressXYZ123")

        assert exc_info.value.code == ErrorCode.INVALID_ADDRESS
        assert exc_info.value.status_code == 400
        assert "geocoded" in exc_info.value.message.lower()


@mock_aws
@patch("src.services.google_maps.GoogleMapsClient")
@patch("src.services.openstates.OpenStatesClient")
def test_address_lookup_geocoding_service_error(MockOpenStatesClient, MockGoogleMapsClient):
    """Test handler returns 503 when Google Maps service fails (T043)"""
    # Setup mock Parameter Store
    ssm_client = boto3.client("ssm", region_name="us-east-1")
    ssm_client.put_parameter(
        Name="/represent-app/google-maps-api-key",
        Value="mock-google-maps-key",
        Type="SecureString",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/represent-app/openstates-api-key",
        Value="mock-openstates-key",
        Type="SecureString",
        Overwrite=True,
    )

    from src.handlers.address_lookup import AddressLookupHandler
    from src.utils.errors import ApiException, ErrorCode

    # Mock Google Maps to raise external service error
    MockGoogleMapsClient = Mock()
    mock_gmaps_instance = Mock()
    MockGoogleMapsClient.return_value = mock_gmaps_instance
    mock_gmaps_instance.geocode.side_effect = ApiException(
        code=ErrorCode.EXTERNAL_SERVICE_ERROR, message="Google Maps API timeout", status_code=503
    )

    # Mock OpenStatesClient
    MockOpenStatesClient = Mock()
    mock_openstates_instance = Mock()
    MockOpenStatesClient.return_value = mock_openstates_instance

    with (
        patch("src.handlers.address_lookup.GoogleMapsClient", MockGoogleMapsClient),
        patch("src.handlers.address_lookup.OpenStatesClient", MockOpenStatesClient),
    ):
        handler = AddressLookupHandler()

        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            handler.handle("Any Address")

        assert exc_info.value.code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503


@mock_aws
@patch("src.services.google_maps.GoogleMapsClient")
@patch("src.services.openstates.OpenStatesClient")
def test_address_lookup_openstates_service_error(MockOpenStatesClient, MockGoogleMapsClient):
    """Test handler returns 503 when OpenStates service fails (T043)"""
    # Setup mock Parameter Store
    ssm_client = boto3.client("ssm", region_name="us-east-1")
    ssm_client.put_parameter(
        Name="/represent-app/google-maps-api-key", Value="mock-google-maps-key", Type="SecureString"
    )
    ssm_client.put_parameter(
        Name="/represent-app/openstates-api-key", Value="mock-openstates-key", Type="SecureString"
    )

    from src.handlers.address_lookup import AddressLookupHandler
    from src.utils.errors import ApiException, ErrorCode

    # Mock successful geocoding
    mock_geocoding_result = {
        "latitude": 47.6105,
        "longitude": -122.3115,
        "formatted_address": "Seattle, WA, USA",
    }

    MockGoogleMapsClient = Mock()
    mock_gmaps_instance = Mock()
    MockGoogleMapsClient.return_value = mock_gmaps_instance
    mock_gmaps_instance.geocode.return_value = mock_geocoding_result

    # Mock OpenStates to raise service error
    MockOpenStatesClient = Mock()
    mock_openstates_instance = Mock()
    MockOpenStatesClient.return_value = mock_openstates_instance
    mock_openstates_instance.get_representatives_by_coordinates.side_effect = ApiException(
        code=ErrorCode.RATE_LIMIT_EXCEEDED,
        message="OpenStates rate limit exceeded",
        status_code=503,
    )

    with (
        patch("src.handlers.address_lookup.GoogleMapsClient", MockGoogleMapsClient),
        patch("src.handlers.address_lookup.OpenStatesClient", MockOpenStatesClient),
    ):

        handler = AddressLookupHandler()

        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            handler.handle("Seattle, WA")

        assert exc_info.value.code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert exc_info.value.status_code == 503


@mock_aws
@patch("src.services.google_maps.GoogleMapsClient")
@patch("src.services.openstates.OpenStatesClient")
def test_address_lookup_no_representatives_found(MockOpenStatesClient, MockGoogleMapsClient):
    """Test handler handles case when no representatives found for coordinates (T043)"""
    # Setup mock Parameter Store
    ssm_client = boto3.client("ssm", region_name="us-east-1")
    ssm_client.put_parameter(
        Name="/represent-app/google-maps-api-key", Value="mock-google-maps-key", Type="SecureString"
    )
    ssm_client.put_parameter(
        Name="/represent-app/openstates-api-key", Value="mock-openstates-key", Type="SecureString"
    )

    from src.handlers.address_lookup import AddressLookupHandler

    # Mock successful geocoding for remote location
    mock_geocoding_result = {
        "latitude": 41.1400,
        "longitude": -104.8202,
        "formatted_address": "123 Remote Location Rd, Rural Area, WY 82001, USA",
    }

    MockGoogleMapsClient = Mock()
    mock_gmaps_instance = Mock()
    MockGoogleMapsClient.return_value = mock_gmaps_instance
    mock_gmaps_instance.geocode.return_value = mock_geocoding_result

    # Mock OpenStates returning empty results (no error, just no data)
    MockOpenStatesClient = Mock()
    mock_openstates_instance = Mock()
    MockOpenStatesClient.return_value = mock_openstates_instance
    mock_openstates_instance.get_representatives_by_coordinates.return_value = []  # Empty list

    with (
        patch("src.handlers.address_lookup.GoogleMapsClient", MockGoogleMapsClient),
        patch("src.handlers.address_lookup.OpenStatesClient", MockOpenStatesClient),
    ):

        handler = AddressLookupHandler()

        # Act
        result = handler.handle("123 Remote Location Rd, Rural Area, WY")

        # Assert - Should return structured response with empty results
        assert "representatives" in result
        assert "metadata" in result
        assert "warnings" in result

        # All government levels should be empty
        representatives = result["representatives"]
        assert len(representatives["federal"]) == 0
        assert len(representatives["state"]) == 0
        assert len(representatives["local"]) == 0

        # Metadata should still include geocoded information
        metadata = result["metadata"]
        assert metadata["address"] == "123 Remote Location Rd, Rural Area, WY 82001, USA"
        assert metadata["coordinates"]["latitude"] == 41.1400
        assert metadata["total_count"] == 0
        assert metadata["government_levels"] == []

        # Should include warning about no data
        assert len(result["warnings"]) > 0
        assert any("no representative data" in w.lower() for w in result["warnings"])
