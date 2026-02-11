"""
Integration tests for end-to-end address-to-representatives flow

User Story 3 (T037-T042): Complete geolocation-based lookup integration
Tests the entire flow: address → geocoding → coordinates → representatives

Following TDD: These tests should FAIL before implementation, then PASS after implementation
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from moto import mock_aws
import boto3
from typing import Dict, Any, List

from src.handlers.address_lookup import lambda_handler
from src.utils.errors import ApiException, ErrorCode


# T008: Test fixtures for geocoding responses
@pytest.fixture
def mock_geocoding_response():
    """Mock response from Google Maps Geocoding API"""
    return [
        {
            "formatted_address": "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA",
            "geometry": {
                "location": {"lat": 38.8976763, "lng": -77.0365298},
                "location_type": "ROOFTOP",
            },
            "place_id": "ChIJGVtI4by3t4kRr51d_Qm_x58",
            "types": ["street_address"],
        }
    ]


# T009: Test fixtures for OpenStates geo responses
@pytest.fixture
def mock_openstates_geo_response():
    """Mock response from OpenStates /people.geo endpoint"""
    return {
        "results": [
            {
                "id": "ocd-person/55a28978-7661-5a33-a2be-a505a07e2a8e",
                "name": "Joe Biden",
                "party": "Democratic",
                "current_role": {
                    "title": "President",
                    "org_classification": "executive",
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
        ],
        "pagination": {"per_page": 10, "page": 1, "max_page": 1, "total_items": 1},
    }


@pytest.fixture
def mock_lambda_context():
    """Mock Lambda context for testing"""
    context = Mock()
    context.aws_request_id = "test-request-123"
    context.function_name = "address-lookup-handler"
    context.memory_limit_in_mb = 128
    context.remaining_time_in_millis = lambda: 30000
    return context


class TestAddressToRepresentativesIntegration:
    """Integration tests for complete address-to-representatives flow"""

    @mock_aws
    def setup_method(self, method):
        """Set up test environment with mocked Parameter Store"""
        # Create mock Parameter Store entries
        ssm_client = boto3.client("ssm", region_name="us-east-1")
        ssm_client.put_parameter(
            Name="/represent-app/google-maps-api-key",
            Value="mock-google-maps-key",
            Type="SecureString",
        )
        ssm_client.put_parameter(
            Name="/represent-app/openstates-api-key",
            Value="mock-openstates-key",
            Type="SecureString",
        )

    def create_api_gateway_event(self, address: str) -> Dict[str, Any]:
        """Create mock API Gateway HTTP API v2 event"""
        return {
            "version": "2.0",
            "routeKey": "GET /representatives",
            "rawPath": "/representatives",
            "rawQueryString": f"address={address}",
            "headers": {"accept": "application/json", "content-type": "application/json"},
            "queryStringParameters": {"address": address},
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "test-api-id",
                "domainName": "test-api.execute-api.us-east-1.amazonaws.com",
                "http": {"method": "GET", "path": "/representatives", "protocol": "HTTP/1.1"},
                "requestId": "test-request-123",
                "stage": "$default",
            },
        }

    # T037: Test for complete address flow
    @mock_aws
    @patch("googlemaps.Client")
    @patch("requests.get")
    def test_complete_address_to_representatives_flow_success(
        self,
        mock_requests_get,
        mock_googlemaps_client,
        mock_geocoding_response,
        mock_openstates_geo_response,
        mock_lambda_context,
    ):
        """Test successful end-to-end flow: address → geocoding → coordinates → representatives"""
        # Setup mocks
        mock_gmaps_instance = Mock()
        mock_googlemaps_client.return_value = mock_gmaps_instance
        mock_gmaps_instance.geocode.return_value = mock_geocoding_response

        mock_response = Mock()
        mock_response.json.return_value = mock_openstates_geo_response
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        # Create test event
        event = self.create_api_gateway_event("1600 Pennsylvania Avenue NW, Washington, DC")

        # Execute handler
        result = lambda_handler(event, mock_lambda_context)

        # Verify response structure
        assert result["statusCode"] == 200
        body = json.loads(result["body"])

        # Verify response contains required sections
        assert "representatives" in body
        assert "metadata" in body
        assert "warnings" in body

        # Verify representatives are grouped by government level
        representatives = body["representatives"]
        assert "federal" in representatives
        assert "state" in representatives
        assert "local" in representatives

        # Verify federal representative was found
        federal_reps = representatives["federal"]
        assert len(federal_reps) == 1
        assert federal_reps[0]["name"] == "Joe Biden"
        assert federal_reps[0]["position"] == "President"
        assert federal_reps[0]["state"] == "United States"

        # Verify metadata includes geocoded information
        metadata = body["metadata"]
        assert metadata["address"] == "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA"
        assert metadata["coordinates"]["latitude"] == 38.8976763
        assert metadata["coordinates"]["longitude"] == -77.0365298
        assert metadata["total_count"] == 1
        assert "federal" in metadata["government_levels"]

        # Verify API calls were made correctly
        mock_gmaps_instance.geocode.assert_called_once_with(
            "1600 Pennsylvania Avenue NW, Washington, DC", timeout=5
        )
        mock_requests_get.assert_called_once()

        # Verify OpenStates API call parameters
        call_args = mock_requests_get.call_args
        assert "/people.geo" in call_args[0][0]  # URL contains geo endpoint
        params = call_args[1]["params"]
        assert params["lat"] == 38.8976763
        assert params["lng"] == -77.0365298
        assert params["apikey"] == "mock-openstates-key"

    # T038: Test for urban address with all government levels
    @mock_aws
    @patch("googlemaps.Client")
    @patch("requests.get")
    def test_urban_address_all_government_levels(
        self, mock_requests_get, mock_googlemaps_client, mock_lambda_context
    ):
        """Test urban address returning representatives from federal, state, and local levels"""
        # Mock geocoding response for Seattle
        seattle_geocoding = [
            {
                "formatted_address": "1600 7th Ave, Seattle, WA 98101, USA",
                "geometry": {
                    "location": {"lat": 47.6105, "lng": -122.3115},
                    "location_type": "ROOFTOP",
                },
            }
        ]

        # Mock OpenStates response with all government levels
        multi_level_response = {
            "results": [
                {
                    "id": "ocd-person/federal-rep",
                    "name": "Adam Smith",
                    "party": "Democratic",
                    "current_role": {"title": "Representative", "district": "WA-9"},
                    "jurisdiction": {"name": "United States", "classification": "country"},
                },
                {
                    "id": "ocd-person/state-rep",
                    "name": "Rebecca Saldaña",
                    "party": "Democratic",
                    "current_role": {"title": "Senator", "district": "37"},
                    "jurisdiction": {"name": "Washington", "classification": "state"},
                },
                {
                    "id": "ocd-person/local-rep",
                    "name": "Bruce Harrell",
                    "party": "Nonpartisan",
                    "current_role": {"title": "Mayor"},
                    "jurisdiction": {"name": "Seattle", "classification": "municipality"},
                },
            ]
        }

        # Setup mocks
        mock_gmaps_instance = Mock()
        mock_googlemaps_client.return_value = mock_gmaps_instance
        mock_gmaps_instance.geocode.return_value = seattle_geocoding

        mock_response = Mock()
        mock_response.json.return_value = multi_level_response
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        # Execute test
        event = self.create_api_gateway_event("1600 7th Ave, Seattle, WA")
        result = lambda_handler(event, mock_lambda_context)

        # Verify all government levels have representatives
        assert result["statusCode"] == 200
        body = json.loads(result["body"])

        representatives = body["representatives"]
        assert len(representatives["federal"]) == 1
        assert len(representatives["state"]) == 1
        assert len(representatives["local"]) == 1

        assert representatives["federal"][0]["name"] == "Adam Smith"
        assert representatives["state"][0]["name"] == "Rebecca Saldaña"
        assert representatives["local"][0]["name"] == "Bruce Harrell"

        # Verify metadata reflects all levels
        metadata = body["metadata"]
        assert metadata["total_count"] == 3
        assert set(metadata["government_levels"]) == {"federal", "state", "local"}

    # T039: Test for rural address or partial data
    @mock_aws
    @patch("googlemaps.Client")
    @patch("requests.get")
    def test_rural_address_partial_data(
        self, mock_requests_get, mock_googlemaps_client, mock_lambda_context
    ):
        """Test rural address that may have limited representative data"""
        # Mock geocoding for rural Wyoming
        rural_geocoding = [
            {
                "formatted_address": "123 Ranch Rd, Cheyenne, WY 82001, USA",
                "geometry": {"location": {"lat": 41.1400, "lng": -104.8202}},
            }
        ]

        # Mock limited OpenStates response (only federal representatives)
        limited_response = {
            "results": [
                {
                    "id": "ocd-person/wy-senator",
                    "name": "John Barrasso",
                    "party": "Republican",
                    "current_role": {"title": "Senator"},
                    "jurisdiction": {"name": "United States", "classification": "country"},
                }
            ]
        }

        # Setup mocks
        mock_gmaps_instance = Mock()
        mock_googlemaps_client.return_value = mock_gmaps_instance
        mock_gmaps_instance.geocode.return_value = rural_geocoding

        mock_response = Mock()
        mock_response.json.return_value = limited_response
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        # Execute test
        event = self.create_api_gateway_event("123 Ranch Rd, Cheyenne, WY")
        result = lambda_handler(event, mock_lambda_context)

        # Verify partial data handling
        assert result["statusCode"] == 200
        body = json.loads(result["body"])

        representatives = body["representatives"]
        assert len(representatives["federal"]) == 1
        assert len(representatives["state"]) == 0
        assert len(representatives["local"]) == 0

        # Should include warning about partial data
        assert isinstance(body["warnings"], list)

    # T040: Test for zip code only input
    @mock_aws
    @patch("googlemaps.Client")
    @patch("requests.get")
    def test_zip_code_only_input(
        self, mock_requests_get, mock_googlemaps_client, mock_lambda_context
    ):
        """Test lookup using zip code only (should work but may be less precise)"""
        # Mock geocoding for zip code (returns centroid)
        zipcode_geocoding = [
            {
                "formatted_address": "Seattle, WA 98101, USA",
                "geometry": {
                    "location": {"lat": 47.6097, "lng": -122.3331},
                    "location_type": "APPROXIMATE",  # Less precise than ROOFTOP
                },
            }
        ]

        mock_response_data = {
            "results": [
                {
                    "id": "test-rep",
                    "name": "Test Representative",
                    "current_role": {"title": "Representative"},
                    "jurisdiction": {"name": "United States", "classification": "country"},
                }
            ]
        }

        # Setup mocks
        mock_gmaps_instance = Mock()
        mock_googlemaps_client.return_value = mock_gmaps_instance
        mock_gmaps_instance.geocode.return_value = zipcode_geocoding

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        # Execute test
        event = self.create_api_gateway_event("98101")
        result = lambda_handler(event, mock_lambda_context)

        # Verify successful lookup despite less precise geocoding
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["metadata"]["address"] == "Seattle, WA 98101, USA"

    # T041: Test for invalid address returning 400 error
    @mock_aws
    @patch("googlemaps.Client")
    def test_invalid_address_error(self, mock_googlemaps_client, mock_lambda_context):
        """Test invalid address that cannot be geocoded returns 400 error"""
        # Mock geocoding returning empty results (invalid address)
        mock_gmaps_instance = Mock()
        mock_googlemaps_client.return_value = mock_gmaps_instance
        mock_gmaps_instance.geocode.return_value = []  # Empty results

        # Execute test
        event = self.create_api_gateway_event("InvalidAddressXYZ123")
        result = lambda_handler(event, mock_lambda_context)

        # Verify 400 error response
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"]["code"] == "INVALID_REQUEST"
        assert "geocoded" in body["error"]["message"].lower()

    # T042: Test for response structure matching API contract
    @mock_aws
    @patch("googlemaps.Client")
    @patch("requests.get")
    def test_response_structure_matches_api_contract(
        self,
        mock_requests_get,
        mock_googlemaps_client,
        mock_geocoding_response,
        mock_openstates_geo_response,
        mock_lambda_context,
    ):
        """Test that response structure exactly matches the API contract specification"""
        # Setup mocks
        mock_gmaps_instance = Mock()
        mock_googlemaps_client.return_value = mock_gmaps_instance
        mock_gmaps_instance.geocode.return_value = mock_geocoding_response

        mock_response = Mock()
        mock_response.json.return_value = mock_openstates_geo_response
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        # Execute test
        event = self.create_api_gateway_event("1600 Pennsylvania Avenue NW, Washington, DC")
        result = lambda_handler(event, mock_lambda_context)

        # Verify HTTP response structure
        assert result["statusCode"] == 200
        assert "headers" in result
        assert result["headers"]["Content-Type"] == "application/json"

        # Verify JSON body structure matches contract
        body = json.loads(result["body"])

        # Top-level structure
        required_top_level = ["representatives", "metadata", "warnings"]
        for field in required_top_level:
            assert field in body, f"Missing required field: {field}"

        # Representatives structure
        representatives = body["representatives"]
        required_levels = ["federal", "state", "local"]
        for level in required_levels:
            assert level in representatives, f"Missing government level: {level}"
            assert isinstance(representatives[level], list), f"{level} should be a list"

        # Representative object structure
        if representatives["federal"]:
            rep = representatives["federal"][0]
            required_rep_fields = [
                "id",
                "name",
                "position",
                "state",
                "party",
                "contact_info",
                "created_at",
                "updated_at",
            ]
            for field in required_rep_fields:
                assert field in rep, f"Missing representative field: {field}"

            # Contact info structure
            contact_info = rep["contact_info"]
            assert isinstance(contact_info, dict), "contact_info should be a dict"
            # Note: email, phone, image can be null but should be present as keys

        # Metadata structure
        metadata = body["metadata"]
        required_metadata = ["address", "coordinates", "total_count", "government_levels"]
        for field in required_metadata:
            assert field in metadata, f"Missing metadata field: {field}"

        # Coordinates structure
        coordinates = metadata["coordinates"]
        assert "latitude" in coordinates and "longitude" in coordinates
        assert isinstance(coordinates["latitude"], (int, float))
        assert isinstance(coordinates["longitude"], (int, float))

        # Government levels should be list
        assert isinstance(metadata["government_levels"], list)

        # Warnings should be list
        assert isinstance(body["warnings"], list)
