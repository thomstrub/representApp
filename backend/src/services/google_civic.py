"""
Google Civic Information API client for address-to-OCD-ID conversion

This service converts user-provided street addresses into Open Civic Data (OCD)
identifiers representing political divisions (country, state, county, city, districts).

Feature: 003-address-lookup (User Story 1 - T017-T022)
API Documentation: https://developers.google.com/civic-information/docs/v2
"""
import requests
from typing import List, Dict, Any
from aws_lambda_powertools import Logger, Tracer

from src.utils.errors import ApiException, ErrorCode

logger = Logger(service="google_civic_client")
tracer = Tracer(service="google_civic_client")


class GoogleCivicClient:
    """
    Client for Google Civic Information API
    
    Provides address lookup functionality to retrieve political divisions
    and their OCD identifiers.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize Google Civic API client
        
        Args:
            api_key: Google API key for Civic Information API
        """
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/civicinfo/v2"
        logger.info("GoogleCivicClient initialized")
    
    @tracer.capture_method
    def lookup_divisions(self, address: str) -> List[Dict[str, Any]]:
        """
        Look up political divisions for a given address
        
        Args:
            address: Street address to look up (e.g., "1600 Pennsylvania Ave NW, Washington, DC 20500")
        
        Returns:
            List of divisions with 'ocd_id' and 'name' fields
            Example: [
                {"ocd_id": "ocd-division/country:us", "name": "United States"},
                {"ocd_id": "ocd-division/country:us/state:dc", "name": "District of Columbia"}
            ]
        
        Raises:
            ApiException: 
                - INVALID_ADDRESS (400) if address is empty or exceeds 500 characters
                - ADDRESS_NOT_FOUND (404) if no divisions found for address
                - RATE_LIMIT_EXCEEDED (503) if API rate limit exceeded
                - EXTERNAL_SERVICE_ERROR (503) for network/timeout errors
        """
        # T018: Input validation
        if not address or not address.strip():
            logger.warning("Empty address provided")
            raise ApiException(
                code=ErrorCode.INVALID_ADDRESS,
                message="Address cannot be empty",
                status_code=400
            )
        
        if len(address) > 500:
            logger.warning(f"Address exceeds 500 characters: {len(address)} chars")
            raise ApiException(
                code=ErrorCode.INVALID_ADDRESS,
                message="Address cannot exceed 500 characters",
                status_code=400
            )
        
        logger.info(f"Looking up divisions for address: {address}")
        tracer.put_annotation(key="address_length", value=len(address))
        
        # T018: Make API request to divisionsByAddress endpoint
        endpoint = f"{self.base_url}/divisionsByAddress"
        params = {
            "address": address,
            "key": self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            tracer.put_metadata(key="response_status", value=response.status_code)
            
            # T019: Handle 404 - Address not found
            if response.status_code == 404:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Address not found")
                logger.warning(f"Address not found: {address}")
                raise ApiException(
                    code=ErrorCode.ADDRESS_NOT_FOUND,
                    message=f"No divisions found for the provided address: {error_message}",
                    status_code=404
                )
            
            # T020: Handle 429 - Rate limit exceeded
            if response.status_code == 429:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Rate limit exceeded")
                logger.error(f"Rate limit exceeded for Google Civic API")
                raise ApiException(
                    code=ErrorCode.RATE_LIMIT_EXCEEDED,
                    message="Google Civic API rate limit exceeded. Please try again later.",
                    status_code=503,
                    details=error_message
                )
            
            # Handle other non-200 status codes
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    logger.error(f"Unexpected status code from Google Civic API: {response.status_code}, message: {error_message}")
                except:
                    logger.error(f"Unexpected status code from Google Civic API: {response.status_code}, body: {response.text}")
                raise ApiException(
                    code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                    message=f"Google Civic API returned error: {response.status_code}",
                    status_code=503
                )
            
            # T018: Parse successful response
            data = response.json()
            divisions_data = data.get("divisions", {})
            
            # Transform to list format with ocd_id and name
            divisions = []
            for ocd_id, div_info in divisions_data.items():
                divisions.append({
                    "ocd_id": ocd_id,
                    "name": div_info.get("name", "")
                })
            
            logger.info(f"Successfully retrieved {len(divisions)} divisions")
            tracer.put_annotation(key="division_count", value=len(divisions))
            
            return divisions
        
        # T020: Handle network timeouts
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout calling Google Civic API: {str(e)}")
            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="Google Civic API request timed out. Service may be unavailable.",
                status_code=503,
                details=str(e)
            )
        
        # T020: Handle connection errors
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error calling Google Civic API: {str(e)}")
            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="Unable to connect to Google Civic API. Service may be unavailable.",
                status_code=503,
                details=str(e)
            )
        
        except ApiException:
            # Re-raise our own exceptions
            raise
        
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error calling Google Civic API: {str(e)}")
            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="An unexpected error occurred while calling Google Civic API",
                status_code=503,
                details=str(e)
            )
