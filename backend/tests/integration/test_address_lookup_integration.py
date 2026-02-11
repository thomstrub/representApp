"""
Integration test for full address lookup flow (US3 - T052)

Tests the complete journey: API Gateway → Lambda → Google Civic → OpenStates → Response

TDD: This test should FAIL until full US3 implementation is complete.
"""

import pytest
from unittest.mock import Mock, patch
import json


@pytest.mark.integration
def test_full_address_lookup_flow():
    """
    Test complete address lookup flow from API Gateway event to JSON response

    Flow: API Gateway Event → Lambda Handler → GoogleCivic → OpenStates → Formatted Response
    """
    from src.handlers.address_lookup import lambda_handler

    # Mock API Gateway event
    event = {
        "version": "2.0",
        "routeKey": "GET /representatives",
        "rawPath": "/representatives",
        "rawQueryString": "address=1600+Pennsylvania+Ave+NW,+Washington+DC+20500",
        "queryStringParameters": {"address": "1600 Pennsylvania Ave NW, Washington DC 20500"},
        "requestContext": {
            "http": {"method": "GET", "path": "/representatives"},
            "requestId": "test-request-123",
        },
    }

    # Mock Lambda context
    mock_context = Mock()
    mock_context.request_id = "test-request-123"
    mock_context.function_name = "address-lookup-function"

    # Mock Google Civic API response
    mock_civic_response = [
        {"ocd_id": "ocd-division/country:us", "name": "United States"},
        {"ocd_id": "ocd-division/country:us/district:dc", "name": "District of Columbia"},
        {"ocd_id": "ocd-division/country:us/district:dc/cd:98", "name": "DC At-Large"},
    ]

    # Mock OpenStates API response
    mock_openstates_response = [
        {
            "id": "ocd-person/president-001",
            "name": "President Example",
            "office": "President of the United States",
            "party": "Independent",
            "email": "president@whitehouse.gov",
            "phone": "202-555-0100",
            "address": "1600 Pennsylvania Ave NW, Washington, DC 20500",
            "website": "https://www.whitehouse.gov",
            "photo_url": "https://example.com/president.jpg",
            "government_level": "federal",
            "jurisdiction": "United States",
        }
    ]

    with (
        patch("src.handlers.address_lookup.get_api_key") as mock_get_key,
        patch("src.handlers.address_lookup.GoogleCivicClient") as MockGoogleClient,
        patch("src.handlers.address_lookup.OpenStatesClient") as MockOpenStatesClient,
    ):

        # Setup mocks
        mock_get_key.return_value = "test-api-key"

        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.return_value = mock_civic_response

        mock_openstates = MockOpenStatesClient.return_value
        mock_openstates.get_representatives_by_division.return_value = mock_openstates_response

        # Act
        response = lambda_handler(event, mock_context)

        # Assert HTTP response structure
        assert response["statusCode"] == 200
        assert "body" in response
        assert "headers" in response
        assert response["headers"]["Content-Type"] == "application/json"

        # Parse response body
        body = json.loads(response["body"])

        # Assert response structure
        assert "address" in body
        assert body["address"] == "1600 Pennsylvania Ave NW, Washington DC 20500"
        assert "representatives" in body
        assert "metadata" in body
        assert "warnings" in body

        # Assert representatives
        assert len(body["representatives"]) > 0
        rep = body["representatives"][0]
        assert rep["id"] == "ocd-person/president-001"
        assert rep["name"] == "President Example"
        assert rep["government_level"] == "federal"

        # Assert metadata
        metadata = body["metadata"]
        assert "division_count" in metadata
        assert metadata["division_count"] == 3
        assert "response_time_ms" in metadata
        assert metadata["response_time_ms"] > 0
        assert "government_levels" in metadata
        assert "federal" in metadata["government_levels"]


@pytest.mark.integration
def test_full_flow_with_error_handling():
    """Test that errors are properly formatted in the response"""
    from src.handlers.address_lookup import lambda_handler

    # Event with missing address parameter
    event = {
        "version": "2.0",
        "routeKey": "GET /representatives",
        "rawPath": "/representatives",
        "rawQueryString": "",
        "queryStringParameters": None,
        "requestContext": {
            "http": {"method": "GET", "path": "/representatives"},
            "requestId": "test-request-456",
        },
    }

    mock_context = Mock()
    mock_context.request_id = "test-request-456"

    # Act
    response = lambda_handler(event, mock_context)

    # Assert error response
    assert response["statusCode"] == 400
    assert "body" in response

    body = json.loads(response["body"])
    assert "error" in body
    assert body["error"]["code"] == "MISSING_PARAMETER"
    assert "address" in body["error"]["message"].lower()


@pytest.mark.integration
def test_full_flow_with_partial_results():
    """Test that partial results with warnings are handled correctly"""
    from src.handlers.address_lookup import lambda_handler

    event = {
        "version": "2.0",
        "routeKey": "GET /representatives",
        "rawPath": "/representatives",
        "rawQueryString": "address=Seattle,+WA",
        "queryStringParameters": {"address": "Seattle, WA"},
        "requestContext": {
            "http": {"method": "GET", "path": "/representatives"},
            "requestId": "test-request-789",
        },
    }

    mock_context = Mock()
    mock_context.request_id = "test-request-789"

    # Mock responses - some divisions have no data
    mock_civic_response = [
        {"ocd_id": "ocd-division/country:us/state:wa", "name": "Washington"},
        {"ocd_id": "ocd-division/country:us/state:wa/place:seattle", "name": "Seattle"},
    ]

    def mock_get_reps(ocd_id):
        if "place:seattle" in ocd_id:
            return []  # No local data
        return [
            {
                "id": "ocd-person/state-001",
                "name": "State Representative",
                "office": "Governor",
                "party": "Democratic",
                "email": None,
                "phone": None,
                "address": None,
                "website": None,
                "photo_url": None,
                "government_level": "state",
                "jurisdiction": "Washington",
            }
        ]

    with (
        patch("src.handlers.address_lookup.get_api_key") as mock_get_key,
        patch("src.handlers.address_lookup.GoogleCivicClient") as MockGoogleClient,
        patch("src.handlers.address_lookup.OpenStatesClient") as MockOpenStatesClient,
    ):

        mock_get_key.return_value = "test-key"

        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.return_value = mock_civic_response

        mock_openstates = MockOpenStatesClient.return_value
        mock_openstates.get_representatives_by_division.side_effect = mock_get_reps

        # Act
        response = lambda_handler(event, mock_context)

        # Assert successful partial result
        assert response["statusCode"] == 200

        body = json.loads(response["body"])
        assert "representatives" in body
        assert len(body["representatives"]) > 0

        # Assert warnings present
        assert "warnings" in body
        assert len(body["warnings"]) > 0

        # Verify warning mentions the division with no data
        warning_text = " ".join(body["warnings"])
        assert "seattle" in warning_text.lower() or "no data" in warning_text.lower()


@pytest.mark.integration
def test_performance_metadata():
    """Test that response includes performance metrics"""
    from src.handlers.address_lookup import lambda_handler

    event = {
        "version": "2.0",
        "routeKey": "GET /representatives",
        "rawPath": "/representatives",
        "rawQueryString": "address=Test+Address",
        "queryStringParameters": {"address": "Test Address"},
        "requestContext": {
            "http": {"method": "GET", "path": "/representatives"},
            "requestId": "perf-test",
        },
    }

    mock_context = Mock()

    with (
        patch("src.handlers.address_lookup.get_api_key") as mock_get_key,
        patch("src.handlers.address_lookup.GoogleCivicClient") as MockGoogleClient,
        patch("src.handlers.address_lookup.OpenStatesClient") as MockOpenStatesClient,
    ):

        mock_get_key.return_value = "test-key"

        mock_google = MockGoogleClient.return_value
        mock_google.lookup_divisions.return_value = [
            {"ocd_id": "ocd-division/country:us", "name": "US"}
        ]

        mock_openstates = MockOpenStatesClient.return_value
        mock_openstates.get_representatives_by_division.return_value = []

        # Act
        response = lambda_handler(event, mock_context)

        # Assert
        body = json.loads(response["body"])
        assert "metadata" in body
        assert "response_time_ms" in body["metadata"]
        assert isinstance(body["metadata"]["response_time_ms"], (int, float))
        assert body["metadata"]["response_time_ms"] >= 0
