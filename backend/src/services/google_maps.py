"""
Google Maps Geocoding client for address-to-coordinates conversion

Replaces Google Civic Information API with Google Maps Geocoding API
for more reliable address-to-location conversion.
"""

import googlemaps
from googlemaps.exceptions import ApiError, Timeout, HTTPError, TransportError
from aws_lambda_powertools import Logger
from typing import Optional, Dict, Any
from ..utils.errors import ApiException, ErrorCode

logger = Logger()


class GoogleMapsClient:
    """Client for Google Maps Geocoding API"""

    def __init__(self, api_key: str):
        """
        Initialize Google Maps client

        Args:
            api_key: Google Maps API key for Geocoding API
        """
        self.api_key = api_key
        self.client = googlemaps.Client(key=api_key)
        logger.info("Google Maps client initialized successfully")

    def geocode(self, address: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Geocode an address to latitude/longitude coordinates

        Args:
            address: Street address to geocode (e.g., "1600 Pennsylvania Ave NW, Washington, DC")
            timeout: Request timeout in seconds (default: 5)

        Returns:
            Dict with latitude, longitude, and formatted_address, or None if no results

        Raises:
            ApiException: For API errors, timeouts, or authentication failures
        """
        try:
            logger.info(
                f"Geocoding address with timeout {timeout}s", extra={"address_length": len(address)}
            )

            # Call Google Maps Geocoding API
            results = self.client.geocode(address, timeout=timeout)

            # Handle empty results (invalid/unfound address)
            if not results:
                logger.info("No geocoding results found for address")
                return None

            # Extract first result (handles ambiguous addresses)
            first_result = results[0]
            location = first_result["geometry"]["location"]

            # Build response structure
            geocoding_result = {
                "latitude": location["lat"],
                "longitude": location["lng"],
                "formatted_address": first_result["formatted_address"],
            }

            logger.info(
                "Geocoding successful",
                extra={
                    "latitude": geocoding_result["latitude"],
                    "longitude": geocoding_result["longitude"],
                    "location_type": first_result["geometry"].get("location_type"),
                    "results_count": len(results),
                },
            )

            return geocoding_result

        except Timeout as e:
            logger.error(f"Google Maps API timeout after {timeout} seconds: {str(e)}")
            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message=f"Google Maps geocoding timeout after {timeout} seconds",
                status_code=503,
                details=str(e),
            )

        except ApiError as e:
            logger.error(f"Google Maps API authentication or request error: {str(e)}")
            # Handle specific API errors
            error_message = str(e)
            if "REQUEST_DENIED" in error_message or "INVALID_REQUEST" in error_message:
                message = "Google Maps API key authentication error"
            else:
                message = f"Google Maps API error: {error_message}"

            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message=message,
                status_code=503,
                details=str(e),
            )

        except (HTTPError, TransportError) as e:
            logger.error(f"Google Maps API network error: {str(e)}")
            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="Google Maps API network error",
                status_code=503,
                details=str(e),
            )

        except Exception as e:
            logger.error(f"Unexpected error during geocoding: {str(e)}")
            raise ApiException(
                code=ErrorCode.INTERNAL_ERROR,
                message="Unexpected error during address geocoding",
                status_code=500,
                details=str(e),
            )
