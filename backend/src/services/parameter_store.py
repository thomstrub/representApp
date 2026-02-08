"""
Parameter Store service for retrieving API keys from AWS Systems Manager

This service provides secure API key retrieval with caching to minimize
Parameter Store API calls. Used for Google Civic and OpenStates API keys.

Feature: 003-address-lookup (User Story 1 - T016)
"""
import boto3
from functools import lru_cache
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

from src.utils.errors import ApiException, ErrorCode

logger = Logger(service="parameter_store")


@lru_cache(maxsize=10)
def get_api_key(parameter_name: str) -> str:
    """
    Retrieve API key from AWS Systems Manager Parameter Store
    
    Args:
        parameter_name: Parameter Store path (e.g., '/represent-app/google-civic-api-key')
    
    Returns:
        str: The decrypted API key value
    
    Raises:
        ApiException: If parameter not found or access denied
    
    Notes:
        - Results are cached using @lru_cache to minimize Parameter Store calls
        - Requests decryption (WithDecryption=True) for SecureString parameters
        - Cache holds up to 10 different parameters
    """
    logger.info(f"Retrieving API key from Parameter Store: {parameter_name}")
    
    try:
        ssm_client = boto3.client('ssm')
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
        
        api_key = response['Parameter']['Value']
        logger.info(f"Successfully retrieved API key: {parameter_name}")
        return api_key
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        logger.error(
            f"Failed to retrieve parameter {parameter_name}: {error_code} - {error_message}"
        )
        
        # Convert AWS errors to ApiException
        raise ApiException(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"Failed to retrieve API key: {error_message}",
            status_code=500,
            details=f"Parameter: {parameter_name}, Error: {error_code}"
        )
