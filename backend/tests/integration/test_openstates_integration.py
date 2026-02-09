"""
Integration tests for OpenStates API client (US2 - T031)

Tests the full flow: Parameter Store → OpenStates API → Representative data transformation

TDD: These tests should FAIL until backend/src/services/openstates.py is implemented.
"""
import pytest
from unittest.mock import Mock, patch
import os


@pytest.mark.integration
def test_openstates_full_flow_with_parameter_store():
    """
    Test complete flow: retrieve API key from Parameter Store, call OpenStates API
    
    This uses mocked Parameter Store and OpenStates API.
    For real API testing, set OPENSTATES_API_KEY environment variable.
    """
    from src.services.parameter_store import get_api_key
    from src.services.openstates import OpenStatesClient
    from src.utils.ocd_parser import parse_government_level
    
    # Mock Parameter Store response
    with patch('boto3.client') as mock_boto_client:
        mock_ssm = Mock()
        mock_ssm.get_parameter.return_value = {
            'Parameter': {
                'Value': 'test-openstates-key-789'
            }
        }
        mock_boto_client.return_value = mock_ssm
        
        # Get API key from Parameter Store
        api_key = get_api_key('/represent-app/openstates-api-key')
        assert api_key == 'test-openstates-key-789'
        
        # Mock OpenStates API response
        mock_openstates_response = {
            "results": [
                {
                    "id": "ocd-person/fedcba98-7654-3210-fedc-ba9876543210",
                    "name": "Maria Garcia",
                    "current_role": {
                        "title": "State Representative",
                        "district": "37",
                        "division_id": "ocd-division/country:us/state:ca/sldl:37"
                    },
                    "party": [{"name": "Democratic"}],
                    "email": "maria.garcia@assembly.ca.gov",
                    "capitol_office": {
                        "voice": "916-555-0200",
                        "address": "State Capitol, Sacramento, CA 95814"
                    },
                    "links": [
                        {"url": "https://a37.asmdc.org"}
                    ],
                    "image": "https://openstates.org/images/garcia.jpg",
                    "jurisdiction": {"name": "California"}
                }
            ],
            "pagination": {
                "total_items": 1
            }
        }
        
        # Create client and call API
        client = OpenStatesClient(api_key=api_key)
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_openstates_response
            
            # Act
            ocd_id = "ocd-division/country:us/state:ca/sldl:37"
            representatives = client.get_representatives_by_division(ocd_id)
            
            # Assert - Full data transformation
            assert len(representatives) == 1
            rep = representatives[0]
            
            # Check all Representative model fields
            assert rep['id'] == "ocd-person/fedcba98-7654-3210-fedc-ba9876543210"
            assert rep['name'] == "Maria Garcia"
            assert rep['office'] == "State Representative"
            assert rep['party'] == "Democratic"
            assert rep['email'] == "maria.garcia@assembly.ca.gov"
            assert rep['phone'] == "916-555-0200"
            assert rep['address'] == "State Capitol, Sacramento, CA 95814"
            assert rep['website'] == "https://a37.asmdc.org"
            assert rep['photo_url'] == "https://openstates.org/images/garcia.jpg"
            assert rep['government_level'] == "state"
            assert rep['jurisdiction'] == "California"
            
            # Test government level parsing integration
            gov_level = parse_government_level(ocd_id)
            assert gov_level == "state"
            assert rep['government_level'] == gov_level


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get('OPENSTATES_API_KEY'),
    reason="Requires real OPENSTATES_API_KEY environment variable"
)
def test_openstates_real_api_call():
    """
    Test with real OpenStates API (requires OPENSTATES_API_KEY env var)
    
    This test is skipped unless OPENSTATES_API_KEY is set.
    Use for manual verification of API integration.
    """
    from src.services.openstates import OpenStatesClient
    
    api_key = os.environ['OPENSTATES_API_KEY']
    client = OpenStatesClient(api_key=api_key)
    
    # Test with California state (known to have data)
    representatives = client.get_representatives_by_division(
        "ocd-division/country:us/state:ca"
    )
    
    # Assert we got results
    assert len(representatives) > 0
    
    # Check fields are populated
    rep = representatives[0]
    assert rep['id']
    assert rep['name']
    assert rep['office']
    assert rep['government_level'] in ['federal', 'state', 'local']
    assert rep['jurisdiction']


@pytest.mark.integration
def test_openstates_error_handling_in_full_flow():
    """Test that errors propagate correctly through the full flow"""
    from src.services.openstates import OpenStatesClient
    from src.utils.errors import ApiException, ErrorCode
    
    client = OpenStatesClient(api_key="test-key")
    
    # Mock rate limit error
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            client.get_representatives_by_division("ocd-division/country:us/state:wa")
        
        assert exc_info.value.code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert exc_info.value.status_code == 503


@pytest.mark.integration
def test_multiple_divisions_workflow():
    """Test querying multiple divisions and aggregating results"""
    from src.services.openstates import OpenStatesClient
    
    client = OpenStatesClient(api_key="test-key")
    
    # Mock different responses for different divisions (keyed by state code)
    # Note: OpenStates only tracks state legislators, federal divisions are skipped
    responses = {
        "wa": {
            "results": [
                {
                    "id": "ocd-person/sen-001",
                    "name": "Senator Example",
                    "current_role": {
                        "title": "State Senator",
                        "district": "43",
                        "division_id": "ocd-division/country:us/state:wa/sldu:43"
                    },
                    "party": [{"name": "Democratic"}],
                    "jurisdiction": {"name": "Washington"}
                }
            ],
            "pagination": {"total_items": 1}
        },
        "ca": {
            "results": [
                {
                    "id": "ocd-person/asm-001",
                    "name": "Assembly Member Example",
                    "current_role": {
                        "title": "Assembly Member",
                        "district": "15",
                        "division_id": "ocd-division/country:us/state:ca/sldl:15"
                    },
                    "party": [{"name": "Democratic"}],
                    "jurisdiction": {"name": "California"}
                }
            ],
            "pagination": {"total_items": 1}
        }
    }
    
    def mock_get_side_effect(*args, **kwargs):
        """Return different responses based on URL params"""
        params = kwargs.get('params', {})
        jurisdiction = params.get('jurisdiction', '')
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = responses.get(
            jurisdiction,
            {"results": [], "pagination": {"total_items": 0}}
        )
        return mock_response
    
    with patch('requests.get', side_effect=mock_get_side_effect):
# Query multiple divisions (including federal which will be skipped)
        divisions = [
            "ocd-division/country:us",  # Federal - will be skipped
            "ocd-division/country:us/state:wa/sldu:43",  # State - will query
            "ocd-division/country:us/state:ca/sldl:15"  # State - will query
        ]

        all_representatives = []
        for division_id in divisions:
            reps = client.get_representatives_by_division(division_id)
            all_representatives.extend(reps)

        # Assert we got representatives from both state queries (federal was skipped)
        assert len(all_representatives) == 2
        assert all_representatives[0]['name'] == "Senator Example"
        assert all_representatives[1]['name'] == "Assembly Member Example"
        
        # Verify distinct representatives (no President since federal was skipped)
        rep_ids = [rep['id'] for rep in all_representatives]
        assert "ocd-person/sen-001" in rep_ids
        assert "ocd-person/asm-001" in rep_ids
