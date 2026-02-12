"""
Integration tests for Google Civic API full flow (US1 - T015)

Tests the complete flow: Parameter Store → Google Civic API → OCD-IDs

TDD: These tests should FAIL until services are implemented.

Note: Can be run with real API keys or mocked for CI/CD.
"""

import pytest
from unittest.mock import patch, Mock
import os


@pytest.mark.integration
def test_google_civic_full_flow_with_parameter_store():
    """
    Test complete flow: retrieve API key from Parameter Store, call Google Civic API

    This uses mocked Parameter Store but real Google Civic API structure.
    For real API testing, set GOOGLE_CIVIC_API_KEY environment variable.
    """
    from src.services.parameter_store import get_api_key
    from src.services.google_civic import GoogleCivicClient

    # Mock Parameter Store response
    mock_ssm_response = {
        "Parameter": {"Value": os.getenv("GOOGLE_CIVIC_API_KEY", "test-integration-key")}
    }

    #  Mock Google Civic API response with realistic data
    mock_civic_response = {
        "divisions": {
            "ocd-division/country:us": {"name": "United States"},
            "ocd-division/country:us/state:ca": {"name": "California"},
            "ocd-division/country:us/state:ca/cd:12": {
                "name": "California's 12th Congressional District"
            },
            "ocd-division/country:us/state:ca/sldl:17": {
                "name": "California State Assembly district 17"
            },
            "ocd-division/country:us/state:ca/sldu:11": {
                "name": "California State Senate district 11"
            },
        }
    }

    with patch("boto3.client") as mock_boto:
        mock_ssm = Mock()
        mock_ssm.get_parameter.return_value = mock_ssm_response
        mock_boto.return_value = mock_ssm

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_civic_response
            mock_get.return_value = mock_response

            # Act
            api_key = get_api_key("/represent-app/google-civic-api-key")
            client = GoogleCivicClient(api_key=api_key)
            divisions = client.lookup_divisions("123 Main St, San Francisco, CA 94102")

            # Assert
            assert len(divisions) == 5
            assert any(d["ocd_id"] == "ocd-division/country:us" for d in divisions)
            assert any(d["ocd_id"] == "ocd-division/country:us/state:ca" for d in divisions)
            assert any(
                d["ocd_id"].startswith("ocd-division/country:us/state:ca/cd:") for d in divisions
            )

            # Verify all divisions have required fields
            for division in divisions:
                assert "ocd_id" in division
                assert "name" in division
                assert division["ocd_id"].startswith("ocd-division/country:us")


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("GOOGLE_CIVIC_API_KEY"), reason="Requires real API key")
def test_google_civic_real_api_call():
    """
    Test with REAL Google Civic API (skipped unless GOOGLE_CIVIC_API_KEY set)

    Run with: GOOGLE_CIVIC_API_KEY=your_key pytest -m integration
    """
    from src.services.google_civic import GoogleCivicClient

    # Use real API key from environment
    api_key = os.getenv("GOOGLE_CIVIC_API_KEY")
    client = GoogleCivicClient(api_key=api_key)

    # Act - use a known address
    divisions = client.lookup_divisions("1600 Pennsylvania Ave NW, Washington, DC 20500")

    # Assert - should get at least country, state, and congressional district
    assert len(divisions) >= 3
    assert any(d["ocd_id"] == "ocd-division/country:us" for d in divisions)
    assert any("dc" in d["ocd_id"].lower() for d in divisions)

    # Verify structure
    for division in divisions:
        assert "ocd_id" in division
        assert "name" in division
        assert len(division["name"]) > 0


@pytest.mark.integration
def test_google_civic_error_handling_in_full_flow():
    """Test that errors propagate correctly through the full flow"""
    from src.services.parameter_store import get_api_key
    from src.services.google_civic import GoogleCivicClient
    from src.utils.errors import ApiException, ErrorCode

    # Mock successful Parameter Store call
    mock_ssm_response = {"Parameter": {"Value": "test-key"}}

    with patch("boto3.client") as mock_boto:
        mock_ssm = Mock()
        mock_ssm.get_parameter.return_value = mock_ssm_response
        mock_boto.return_value = mock_ssm

        # Mock Google Civic API returning 404
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": {"message": "Not found"}}
            mock_get.return_value = mock_response

            # Act
            api_key = get_api_key("/represent-app/google-civic-api-key")
            client = GoogleCivicClient(api_key=api_key)

            # Assert - error should propagate as ApiException
            with pytest.raises(ApiException) as exc_info:
                client.lookup_divisions("Invalid Address")

            assert exc_info.value.code == ErrorCode.ADDRESS_NOT_FOUND
            assert exc_info.value.status_code == 404
