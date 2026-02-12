"""
Unit tests for OpenStates API client (US2 - T023-T026, T030)

Tests for retrieving representative information from OpenStates API using OCD-IDs.

TDD: These tests should FAIL until backend/src/services/openstates.py is implemented.
"""

import pytest
from unittest.mock import Mock, patch
import requests


def test_openstates_client_initialization():
    """Test OpenStatesClient initializes with API key (T023)"""
    from src.services.openstates import OpenStatesClient

    # Act
    client = OpenStatesClient(api_key="test-key-456")

    # Assert
    assert client.api_key == "test-key-456"
    assert client.base_url == "https://v3.openstates.org"


def test_get_representatives_by_division_success():
    """Test successful representative lookup by OCD-ID (T024)"""
    from src.services.openstates import OpenStatesClient

    # Arrange - Mock OpenStates API response
    mock_response = {
        "results": [
            {
                "id": "ocd-person/12345-abc",
                "name": "John Smith",
                "current_role": {
                    "title": "State Senator",
                    "district": "43",
                    "division_id": "ocd-division/country:us/state:wa/sldu:43",
                },
                "party": [{"name": "Democratic"}],
                "email": "senator.smith@leg.wa.gov",
                "capitol_office": {
                    "voice": "360-555-0100",
                    "address": "123 Capitol Way, Olympia, WA 98501",
                },
                "links": [{"url": "https://smith.wa.gov"}],
                "image": "https://openstates.org/images/smith.jpg",
                "jurisdiction": {"name": "Washington"},
            }
        ],
        "pagination": {"total_items": 1},
    }

    client = OpenStatesClient(api_key="test-key")

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Act
        representatives = client.get_representatives_by_division(
            "ocd-division/country:us/state:wa/sldu:43"
        )

        # Assert
        assert len(representatives) == 1
        rep = representatives[0]

        # Check Representative model fields
        assert rep["id"] == "ocd-person/12345-abc"
        assert rep["name"] == "John Smith"
        assert rep["office"] == "State Senator"
        assert rep["party"] == "Democratic"
        assert rep["email"] == "senator.smith@leg.wa.gov"
        assert rep["phone"] == "360-555-0100"
        assert rep["address"] == "123 Capitol Way, Olympia, WA 98501"
        assert rep["website"] == "https://smith.wa.gov"
        assert rep["photo_url"] == "https://openstates.org/images/smith.jpg"
        assert rep["government_level"] == "state"
        assert rep["jurisdiction"] == "Washington"

        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "headers" in call_args.kwargs
        assert call_args.kwargs["headers"]["X-API-Key"] == "test-key"


def test_get_representatives_by_division_empty_results():
    """Test handling of divisions with no representatives (T025)"""
    from src.services.openstates import OpenStatesClient

    # Arrange - Mock empty response
    mock_response = {"results": [], "pagination": {"total_items": 0}}

    client = OpenStatesClient(api_key="test-key")

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Act
        representatives = client.get_representatives_by_division(
            "ocd-division/country:us/state:wy/county:teton"
        )

        # Assert - Should return empty list, not raise exception
        assert representatives == []


def test_get_representatives_by_division_rate_limit():
    """Test handling of rate limit errors (429) (T026)"""
    from src.services.openstates import OpenStatesClient
    from src.utils.errors import ApiException, ErrorCode

    client = OpenStatesClient(api_key="test-key")

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_get.return_value = mock_response

        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            client.get_representatives_by_division("ocd-division/country:us/state:ca")

        assert exc_info.value.code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert exc_info.value.status_code == 503
        assert "rate limit" in exc_info.value.message.lower()


def test_deduplication_by_representative_id():
    """Test that duplicate representatives are removed by ID (T030)"""
    from src.services.openstates import OpenStatesClient

    # Arrange - Mock response with duplicate (same person in multiple queries)
    mock_response = {
        "results": [
            {
                "id": "ocd-person/12345-abc",
                "name": "Jane Doe",
                "current_role": {
                    "title": "US Senator",
                    "district": "WA",
                    "division_id": "ocd-division/country:us/state:wa",
                },
                "party": [{"name": "Democratic"}],
                "jurisdiction": {"name": "Washington"},
            },
            {
                "id": "ocd-person/12345-abc",  # Same ID - duplicate
                "name": "Jane A. Doe",  # Slightly different name
                "current_role": {
                    "title": "US Senator",
                    "district": "WA",
                    "division_id": "ocd-division/country:us/state:wa",
                },
                "party": [{"name": "Democratic"}],
                "jurisdiction": {"name": "Washington"},
            },
            {
                "id": "ocd-person/67890-xyz",  # Different person
                "name": "John Smith",
                "current_role": {
                    "title": "US Representative",
                    "district": "7",
                    "division_id": "ocd-division/country:us/state:wa/cd:7",
                },
                "party": [{"name": "Republican"}],
                "jurisdiction": {"name": "Washington"},
            },
        ],
        "pagination": {"total_items": 3},
    }

    client = OpenStatesClient(api_key="test-key")

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Act
        representatives = client.get_representatives_by_division("ocd-division/country:us/state:wa")

        # Assert - Should only have 2 unique representatives
        assert len(representatives) == 2
        rep_ids = [rep["id"] for rep in representatives]
        assert "ocd-person/12345-abc" in rep_ids
        assert "ocd-person/67890-xyz" in rep_ids
        # Check that we kept the first occurrence
        jane = next(r for r in representatives if r["id"] == "ocd-person/12345-abc")
        assert jane["name"] == "Jane Doe"  # First occurrence, not "Jane A. Doe"


def test_get_representatives_invalid_api_key():
    """Test handling of invalid API key (401 Unauthorized)"""
    from src.services.openstates import OpenStatesClient
    from src.utils.errors import ApiException, ErrorCode

    client = OpenStatesClient(api_key="invalid-key")

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_get.return_value = mock_response

        # Act & Assert - Use a state division so it actually makes the API call
        with pytest.raises(ApiException) as exc_info:
            client.get_representatives_by_division("ocd-division/country:us/state:wa/sldu:43")

        assert exc_info.value.code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503


def test_get_representatives_network_timeout():
    """Test handling of network timeouts"""
    from src.services.openstates import OpenStatesClient
    from src.utils.errors import ApiException, ErrorCode

    client = OpenStatesClient(api_key="test-key")

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            client.get_representatives_by_division("ocd-division/country:us/state:ca")

        assert exc_info.value.code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503
