"""
Address-based representative lookup handler

Main Lambda handler for User Story 3: API Gateway endpoint that accepts addresses
and returns representatives using geolocation flow (Google Maps + OpenStates geo endpoint).

Feature: 005-geolocation-lookup (User Story 3 - T044-T054)
"""

import time
from typing import Dict, Any, List
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.services.google_maps import GoogleMapsClient
from src.services.openstates import OpenStatesClient
from src.utils.validators import validate_address
from src.utils.errors import ApiException, ErrorCode

# T044-T052: Lambda Powertools structured logging and X-Ray tracing
logger = Logger(service="address_lookup_geolocation")
tracer = Tracer(service="address_lookup_geolocation")


class AddressLookupHandler:
    """Handler for address-to-representatives lookup using geolocation flow"""

    def __init__(self):
        """
        Initialize handler with Google Maps and OpenStates clients

        T044: Initialize GoogleMapsClient instead of GoogleCivicClient
        """
        try:
            logger.info("Initializing AddressLookupHandler with geolocation clients")

            # Get API keys from Parameter Store
            from src.utils.parameter_store import (
                get_google_maps_api_key,
                get_openstates_api_key,
            )

            google_maps_key = get_google_maps_api_key()
            openstates_key = get_openstates_api_key()

            # Initialize clients with API keys
            self.google_maps_client = GoogleMapsClient(google_maps_key)
            self.openstates_client = OpenStatesClient(openstates_key)

            logger.info("Successfully initialized geolocation clients")

        except Exception as e:
            logger.error(f"Failed to initialize AddressLookupHandler: {str(e)}")
            raise ApiException(
                code=ErrorCode.INTERNAL_ERROR,
                message="Failed to initialize address lookup service",
                status_code=500,
                details=str(e),
            )

    def handle(self, address: str) -> Dict[str, Any]:
        """
        Handle address lookup request using geolocation flow

        T045-T051: Replace Google Civic flow with geocoding → coordinates → OpenStates geo

        Args:
            address: Street address to lookup representatives for

        Returns:
            Dict containing representatives grouped by government level, metadata, and warnings

        Raises:
            ApiException: For validation errors, service failures, or invalid addresses
        """
        start_time = time.time()

        # T051: Input validation
        if not address or not isinstance(address, str) or not address.strip():
            logger.warning("Missing or invalid address parameter")
            raise ApiException(
                code=ErrorCode.MISSING_PARAMETER,
                message="Address parameter is required and cannot be empty",
                status_code=400,
            )

        address = address.strip()
        logger.info("Processing address lookup", extra={"address_length": len(address)})
        tracer.put_annotation(key="address_length", value=len(address))

        try:
            # T045: Replace Google Civic flow with geocoding call
            # T046: Add coordinate extraction from geocoding result
            geocoding_start = time.time()
            geocoding_result = self.google_maps_client.geocode(address)
            geocoding_time = time.time() - geocoding_start

            if not geocoding_result:
                logger.warning("Address could not be geocoded", extra={"address": address})
                raise ApiException(
                    code=ErrorCode.INVALID_ADDRESS,
                    message="Address could not be geocoded. Please verify the address and try again.",
                    status_code=400,
                )

            latitude = geocoding_result["latitude"]
            longitude = geocoding_result["longitude"]
            formatted_address = geocoding_result["formatted_address"]

            logger.info(
                "Address geocoded successfully",
                extra={
                    "latitude": latitude,
                    "longitude": longitude,
                    "geocoding_time_ms": round(geocoding_time * 1000, 2),
                },
            )
            tracer.put_annotation(key="geocoding_success", value=True)
            tracer.put_metadata(key="coordinates", value={"lat": latitude, "lng": longitude})

            # T047: Add OpenStates geo endpoint call with coordinates
            openstates_start = time.time()
            openstates_representatives = self.openstates_client.get_representatives_by_coordinates(
                latitude, longitude
            )
            openstates_time = time.time() - openstates_start

            logger.info(
                "OpenStates geo lookup completed",
                extra={
                    "representatives_found": len(openstates_representatives),
                    "openstates_time_ms": round(openstates_time * 1000, 2),
                },
            )
            tracer.put_annotation(
                key="representatives_found", value=len(openstates_representatives)
            )

            # T048: Group representatives by government level
            # Note: OpenStatesClient already transforms the data, so we use it directly
            grouped_representatives = self._group_by_government_level(
                openstates_representatives
            )

            # T049: Build final response with metadata (address, coordinates, total_count, government_levels)
            total_time = time.time() - start_time
            total_count = sum(len(reps) for reps in grouped_representatives.values())
            government_levels = [
                level for level, reps in grouped_representatives.items() if len(reps) > 0
            ]

            # T050: Add warnings array for partial results
            warnings = []
            if total_count == 0:
                warnings.append("No representative data available for this location")
            elif len(government_levels) < 3:  # Less than federal, state, local
                missing_levels = set(["federal", "state", "local"]) - set(government_levels)
                if missing_levels:
                    warnings.append(
                        f"Limited representative data: missing {', '.join(sorted(missing_levels))} level representatives"
                    )

            # T052: Add performance logging
            logger.info(
                "Address lookup completed successfully",
                extra={
                    "total_time_ms": round(total_time * 1000, 2),
                    "geocoding_time_ms": round(geocoding_time * 1000, 2),
                    "openstates_time_ms": round(openstates_time * 1000, 2),
                    "total_representatives": total_count,
                    "government_levels_found": len(government_levels),
                },
            )

            # Build final response structure
            response = {
                "representatives": grouped_representatives,
                "metadata": {
                    "address": formatted_address,
                    "coordinates": {"latitude": latitude, "longitude": longitude},
                    "total_count": total_count,
                    "government_levels": government_levels,
                },
                "warnings": warnings,
            }

            return response

        except ApiException:
            # T051: Verify error handling preserves existing error codes and messages
            # Re-raise ApiExceptions as-is (preserves error codes)
            raise
        except Exception as e:
            # T051: Wrap unexpected exceptions
            logger.error(f"Unexpected error in address lookup: {str(e)}")
            raise ApiException(
                code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred during address lookup",
                status_code=500,
                details=str(e),
            )

    def _group_by_government_level(
        self, representatives: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group representatives by government level

        Args:
            representatives: List of representative dictionaries (already transformed by OpenStatesClient)

        Returns:
            Dict with federal, state, local keys containing representative dicts
        """
        grouped = {"federal": [], "state": [], "local": []}

        for rep_data in representatives:
            # Get government level from transformed data
            government_level = rep_data.get("government_level", "state")
            
            if government_level in grouped:
                grouped[government_level].append(rep_data)
            else:
                # Fallback to state if unexpected level
                grouped["state"].append(rep_data)

        return grouped


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for API Gateway HTTP API v2 events

    Handles GET /representatives?address={address} requests using new geolocation flow

    Args:
        event: API Gateway HTTP API v2 event
        context: Lambda context

    Returns:
        HTTP response with status code, headers, and JSON body
    """
    import json

    logger.info("Processing geolocation address lookup request")
    tracer.put_annotation(key="request_id", value=context.aws_request_id)

    try:
        # Extract address from query parameters
        query_params = event.get("queryStringParameters") or {}
        address = query_params.get("address")

        logger.info(f"Looking up representatives for address using geolocation flow")
        tracer.put_annotation(key="flow_type", value="geolocation")

        # Initialize handler and process request
        handler = AddressLookupHandler()
        result = handler.handle(address)

        # Success response (200)
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # CORS
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps(result),
        }

        total_representatives = result.get("metadata", {}).get("total_count", 0)
        logger.info(f"Successfully returned {total_representatives} representatives")
        tracer.put_annotation(key="success", value=True)

        return response

    except ApiException as e:
        # Format error responses with single error object
        logger.error(f"API exception: {e.code} - {e.message}")
        tracer.put_annotation(key="error_code", value=e.code.value)

        error_response = {
            "statusCode": e.status_code,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": {"code": e.code.value, "message": e.message}}),
        }

        return error_response

    except Exception as e:
        # Unexpected errors return 500
        logger.exception(f"Unexpected error in lambda handler: {str(e)}")
        tracer.put_annotation(key="error", value="unexpected")

        error_response = {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps(
                {
                    "error": {
                        "code": ErrorCode.INTERNAL_ERROR.value,
                        "message": "An unexpected error occurred",
                    }
                }
            ),
        }
        return error_response
