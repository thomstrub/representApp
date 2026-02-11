"""
Parameter Store utility for secure API key retrieval

Provides centralized access to AWS Systems Manager Parameter Store
for managing API keys securely across the application.
"""
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from aws_lambda_powertools import Logger
from .errors import ApiException, ErrorCode

logger = Logger()


class ParameterStoreClient:
    """Client for retrieving parameters from AWS Systems Manager Parameter Store"""
    
    def __init__(self):
        """Initialize SSM client"""
        self.ssm = boto3.client('ssm')
    
    def get_parameter(self, parameter_name: str, decrypt: bool = True) -> str:
        """
        Retrieve a parameter from Parameter Store
        
        Args:
            parameter_name: Full parameter path (e.g., '/represent-app/google-maps-api-key')
            decrypt: Whether to decrypt SecureString parameters
            
        Returns:
            Parameter value as string
            
        Raises:
            ApiException: If parameter cannot be retrieved
        """
        try:
            logger.info(f"Retrieving parameter: {parameter_name}")
            
            response = self.ssm.get_parameter(
                Name=parameter_name,
                WithDecryption=decrypt
            )
            
            parameter_value = response['Parameter']['Value']
            
            # Don't log the actual value for security
            logger.info(f"Successfully retrieved parameter: {parameter_name}")
            
            return parameter_value
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code == 'ParameterNotFound':
                logger.error(f"Parameter not found: {parameter_name}")
                raise ApiException(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Configuration parameter not found: {parameter_name}",
                    status_code=500,
                    details=f"Parameter {parameter_name} does not exist in Parameter Store"
                )
            elif error_code == 'AccessDenied':
                logger.error(f"Access denied to parameter: {parameter_name}")
                raise ApiException(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="Access denied to configuration parameter",
                    status_code=500,
                    details=f"Insufficient permissions to access {parameter_name}"
                )
            else:
                logger.error(f"AWS error retrieving parameter {parameter_name}: {str(e)}")
                raise ApiException(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="Failed to retrieve configuration parameter",
                    status_code=500,
                    details=str(e)
                )
                
        except BotoCoreError as e:
            logger.error(f"BotoCore error retrieving parameter {parameter_name}: {str(e)}")
            raise ApiException(
                code=ErrorCode.INTERNAL_ERROR,
                message="AWS service error during configuration retrieval", 
                status_code=500,
                details=str(e)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving parameter {parameter_name}: {str(e)}")
            raise ApiException(
                code=ErrorCode.INTERNAL_ERROR,
                message="Unexpected error during configuration retrieval",
                status_code=500,
                details=str(e)
            )


# Predefined parameter paths for consistency
class ParameterPaths:
    """Standard parameter paths used across the application"""
    GOOGLE_MAPS_API_KEY = "/represent-app/google-maps-api-key"
    OPENSTATES_API_KEY = "/represent-app/openstates-api-key"
    GOOGLE_CIVIC_API_KEY = "/represent-app/google-civic-api-key"  # Legacy - will be removed


# Global instance for easy access
parameter_store_client = ParameterStoreClient()


def get_google_maps_api_key() -> str:
    """Convenience function to get Google Maps API key"""
    return parameter_store_client.get_parameter(ParameterPaths.GOOGLE_MAPS_API_KEY)


def get_openstates_api_key() -> str:
    """Convenience function to get OpenStates API key"""
    return parameter_store_client.get_parameter(ParameterPaths.OPENSTATES_API_KEY)


def get_google_civic_api_key() -> str:
    """Convenience function to get Google Civic API key (LEGACY - will be removed)"""
    return parameter_store_client.get_parameter(ParameterPaths.GOOGLE_CIVIC_API_KEY)