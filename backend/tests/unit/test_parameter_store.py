"""
Unit tests for Parameter Store service (US1 - T010)

Tests for retrieving and caching API keys from AWS Systems Manager Parameter Store.

TDD: These tests should FAIL until backend/src/services/parameter_store.py is implemented.
"""

import pytest
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError


def test_get_api_key_success():
    """Test successful API key retrieval from Parameter Store"""
    from src.services.parameter_store import get_api_key

    # Mock SSM client response
    mock_response = {"Parameter": {"Value": "test-api-key-12345"}}

    with patch("boto3.client") as mock_boto_client:
        mock_ssm = Mock()
        mock_ssm.get_parameter.return_value = mock_response
        mock_boto_client.return_value = mock_ssm

        # Act
        api_key = get_api_key("/represent-app/test-api-key")

        # Assert
        assert api_key == "test-api-key-12345"
        mock_ssm.get_parameter.assert_called_once_with(
            Name="/represent-app/test-api-key", WithDecryption=True
        )


def test_get_api_key_caching():
    """Test that API keys are cached with @lru_cache to minimize Parameter Store calls"""
    from src.services.parameter_store import get_api_key

    mock_response = {"Parameter": {"Value": "cached-key-67890"}}

    with patch("boto3.client") as mock_boto_client:
        mock_ssm = Mock()
        mock_ssm.get_parameter.return_value = mock_response
        mock_boto_client.return_value = mock_ssm

        # Act - call twice
        key1 = get_api_key("/represent-app/cached-key")
        key2 = get_api_key("/represent-app/cached-key")

        # Assert - SSM should only be called once due to caching
        assert key1 == key2 == "cached-key-67890"
        assert mock_ssm.get_parameter.call_count == 1


def test_get_api_key_parameter_not_found():
    """Test error handling when Parameter Store parameter doesn't exist"""
    from src.services.parameter_store import get_api_key
    from src.utils.errors import ApiException, ErrorCode

    # Mock SSM client error
    error_response = {"Error": {"Code": "ParameterNotFound", "Message": "Parameter not found"}}
    mock_error = ClientError(error_response, "GetParameter")

    with patch("boto3.client") as mock_boto_client:
        mock_ssm = Mock()
        mock_ssm.get_parameter.side_effect = mock_error
        mock_boto_client.return_value = mock_ssm

        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            get_api_key("/represent-app/missing-key")

        assert exc_info.value.code == ErrorCode.INTERNAL_ERROR
        assert "Parameter not found" in exc_info.value.message
        assert exc_info.value.status_code == 500


def test_get_api_key_access_denied():
    """Test error handling when IAM permissions are insufficient"""
    from src.services.parameter_store import get_api_key
    from src.utils.errors import ApiException, ErrorCode

    # Mock access denied error
    error_response = {
        "Error": {"Code": "AccessDeniedException", "Message": "User is not authorized"}
    }
    mock_error = ClientError(error_response, "GetParameter")

    with patch("boto3.client") as mock_boto_client:
        mock_ssm = Mock()
        mock_ssm.get_parameter.side_effect = mock_error
        mock_boto_client.return_value = mock_ssm

        # Act & Assert
        with pytest.raises(ApiException) as exc_info:
            get_api_key("/represent-app/denied-key")

        assert exc_info.value.code == ErrorCode.INTERNAL_ERROR
        assert "not authorized" in exc_info.value.message
