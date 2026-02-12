"""
Tests for OpenStates geolocation-based representative lookup

Feature: 005-geolocation-lookup
User Story 2: OpenStates geo endpoint integration (Tasks T021-T026)

Tests are written FIRST following TDD approach - these should FAIL before implementation.
"""

import pytest
from unittest.mock import Mock, patch
import requests
from src.services.openstates import OpenStatesClient
from src.utils.errors import ApiException, ErrorCode


class TestOpenStatesGeoEndpoint:
    """Test suite for OpenStates geo endpoint functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = OpenStatesClient(api_key="test_api_key")
        self.test_coordinates = {
            "latitude": 47.6105,
            "longitude": -122.3115,  # Seattle, WA coordinates
        }

    @patch("src.services.openstates.requests.get")
    def test_successful_geo_endpoint_query(self, mock_get):
        """T021: Test successful query to OpenStates /people.geo endpoint"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "ocd-person/test-person-1",
                    "name": "Jane Smith",
                    "current_role": {
                        "title": "State Senator",
                        "division_id": "ocd-division/country:us/state:wa/sldu:43",
                    },
                    "party": [{"name": "Democratic"}],
                    "email": "jane.smith@example.gov",
                    "capitol_office": {
                        "voice": "360-786-7667",
                        "address": "123 Capitol Way, Olympia, WA 98504",
                    },
                    "links": [{"url": "https://jane.smith.wa.gov"}],
                    "jurisdiction": {"name": "Washington"},
                    "image": "https://example.com/jane.jpg",
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call the method (this should exist after implementation)
        result = self.client.get_representatives_by_coordinates(
            self.test_coordinates["latitude"], self.test_coordinates["longitude"]
        )

        # Verify API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args

        # Check URL
        assert "/people.geo" in call_args[0][0]  # URL contains geo endpoint

        # Check headers
        headers = call_args[1]["headers"]
        assert headers["X-API-Key"] == "test_api_key"
        assert headers["Accept"] == "application/json"

        # Check parameters include coordinates
        params = call_args[1]["params"]
        assert params["lat"] == 47.6105
        assert params["lng"] == -122.3115

        # Check timeout
        assert call_args[1]["timeout"] == 10

        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 1

        rep = result[0]
        assert rep["id"] == "ocd-person/test-person-1"
        assert rep["name"] == "Jane Smith"
        assert rep["office"] == "State Senator"
        assert rep["party"] == "Democratic"
        assert rep["email"] == "jane.smith@example.gov"
        assert rep["phone"] == "360-786-7667"
        assert rep["address"] == "123 Capitol Way, Olympia, WA 98504"
        assert rep["website"] == "https://jane.smith.wa.gov"
        assert rep["photo_url"] == "https://example.com/jane.jpg"
        assert rep["government_level"] == "state"  # Parsed from division_id
        assert rep["jurisdiction"] == "Washington"

    @patch("src.services.openstates.requests.get")
    def test_empty_results_valid_coordinates(self, mock_get):
        """T022: Test empty results for valid coordinates with no data"""
        # Mock API response with no results
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        result = self.client.get_representatives_by_coordinates(45.0, -120.0)

        # Should return empty list, not raise exception
        assert isinstance(result, list)
        assert len(result) == 0

    @patch("src.services.openstates.requests.get")
    def test_rate_limit_error(self, mock_get):
        """T023: Test OpenStates rate limit error handling"""
        # Mock 429 rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_get.return_value = mock_response

        with pytest.raises(ApiException) as exc_info:
            self.client.get_representatives_by_coordinates(47.6105, -122.3115)

        # Verify correct error handling
        assert exc_info.value.code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert exc_info.value.status_code == 503
        assert "rate limit" in exc_info.value.message.lower()

    @patch("src.services.openstates.requests.get")
    def test_timeout_error(self, mock_get):
        """T024: Test OpenStates timeout error handling"""
        # Mock timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(ApiException) as exc_info:
            self.client.get_representatives_by_coordinates(47.6105, -122.3115)

        # Verify correct error handling
        assert exc_info.value.code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc_info.value.status_code == 503
        assert "timed out" in exc_info.value.message.lower()

    def test_coordinate_validation(self):
        """T028: Test coordinate validation (lat: -90 to 90, lng: -180 to 180)"""
        # Test invalid latitude (too high)
        with pytest.raises(ValueError) as exc_info:
            self.client.get_representatives_by_coordinates(91.0, -122.0)
        assert "latitude" in str(exc_info.value).lower()

        # Test invalid latitude (too low)
        with pytest.raises(ValueError) as exc_info:
            self.client.get_representatives_by_coordinates(-91.0, -122.0)
        assert "latitude" in str(exc_info.value).lower()

        # Test invalid longitude (too high)
        with pytest.raises(ValueError) as exc_info:
            self.client.get_representatives_by_coordinates(47.0, 181.0)
        assert "longitude" in str(exc_info.value).lower()

        # Test invalid longitude (too low)
        with pytest.raises(ValueError) as exc_info:
            self.client.get_representatives_by_coordinates(47.0, -181.0)
        assert "longitude" in str(exc_info.value).lower()

        # Test valid coordinates (should not raise)
        # This will fail until implementation, but tests the validation logic
        try:
            # These are edge cases that should be valid
            self.client.get_representatives_by_coordinates(90.0, 180.0)  # Max valid
            self.client.get_representatives_by_coordinates(-90.0, -180.0)  # Min valid
            self.client.get_representatives_by_coordinates(0.0, 0.0)  # Equator/Prime meridian
        except ValueError:
            pytest.fail("Valid coordinates should not raise ValueError")
        except ApiException:
            # API exceptions are OK for now (we're just testing validation)
            pass

    @patch("src.services.openstates.requests.get")
    def test_transformation_to_representative_model(self, mock_get):
        """T025: Test OpenStates response transformation to Representative model"""
        # Mock response with various data scenarios
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    # Complete data scenario
                    "id": "ocd-person/complete-person",
                    "name": "Complete Person",
                    "current_role": {
                        "title": "State Representative",
                        "division_id": "ocd-division/country:us/state:wa/sldl:43",
                    },
                    "party": [{"name": "Republican"}],
                    "email": "complete@example.gov",
                    "capitol_office": {"voice": "123-456-7890", "address": "123 Test St"},
                    "links": [{"url": "https://complete.example.gov"}],
                    "jurisdiction": {"name": "Washington State"},
                    "image": "https://example.com/complete.jpg",
                },
                {
                    # Minimal data scenario (missing optional fields)
                    "id": "ocd-person/minimal-person",
                    "name": "Minimal Person",
                    "current_role": {
                        "title": "State Senator",
                        "division_id": "ocd-division/country:us/state:wa/sldu:21",
                    },
                    # Missing: party, email, capitol_office, links, jurisdiction, image
                },
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_representatives_by_coordinates(47.6105, -122.3115)

        # Verify transformation for complete data
        complete_rep = result[0]
        assert complete_rep["id"] == "ocd-person/complete-person"
        assert complete_rep["name"] == "Complete Person"
        assert complete_rep["office"] == "State Representative"
        assert complete_rep["party"] == "Republican"
        assert complete_rep["email"] == "complete@example.gov"
        assert complete_rep["phone"] == "123-456-7890"
        assert complete_rep["address"] == "123 Test St"
        assert complete_rep["website"] == "https://complete.example.gov"
        assert complete_rep["photo_url"] == "https://example.com/complete.jpg"
        assert complete_rep["government_level"] == "state"  # From division_id parsing
        assert complete_rep["jurisdiction"] == "Washington State"

        # Verify transformation for minimal data (None for missing fields)
        minimal_rep = result[1]
        assert minimal_rep["id"] == "ocd-person/minimal-person"
        assert minimal_rep["name"] == "Minimal Person"
        assert minimal_rep["office"] == "State Senator"
        assert minimal_rep["party"] is None
        assert minimal_rep["email"] is None
        assert minimal_rep["phone"] is None
        assert minimal_rep["address"] is None
        assert minimal_rep["website"] is None
        assert minimal_rep["photo_url"] is None
        assert minimal_rep["government_level"] == "state"
        assert minimal_rep["jurisdiction"] == "Unknown"  # Default for missing jurisdiction

    @patch("src.services.openstates.requests.get")
    def test_government_level_grouping(self, mock_get):
        """T026: Test government level classification from division IDs"""
        # Mock response with different government levels
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "ocd-person/federal-person",
                    "name": "Federal Rep",
                    "current_role": {
                        "title": "U.S. Representative",
                        "division_id": "ocd-division/country:us/state:wa/cd:7",  # Congressional district
                    },
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us/government",
                        "name": "United States",
                        "classification": "country"
                    },
                },
                {
                    "id": "ocd-person/state-person",
                    "name": "State Rep",
                    "current_role": {
                        "title": "State Representative",
                        "division_id": "ocd-division/country:us/state:wa/sldl:43",  # State legislative
                    },
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us/state:wa/government",
                        "name": "Washington",
                        "classification": "state"
                    },
                },
                {
                    "id": "ocd-person/local-person",
                    "name": "Local Rep",
                    "current_role": {
                        "title": "City Council Member",
                        "division_id": "ocd-division/country:us/state:wa/place:seattle",  # Local
                    },
                    "jurisdiction": {
                        "id": "ocd-jurisdiction/country:us/state:wa/place:seattle/government",
                        "name": "Seattle",
                        "classification": "municipality"
                    },
                },
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_representatives_by_coordinates(47.6105, -122.3115)

        # Verify government level classification
        levels = [rep["government_level"] for rep in result]
        expected_levels = ["federal", "state", "local"]
        assert levels == expected_levels

        # Verify names match expected government levels
        assert result[0]["name"] == "Federal Rep"
        assert result[1]["name"] == "State Rep"
        assert result[2]["name"] == "Local Rep"
