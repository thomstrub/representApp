"""
Address-based representative lookup handler

Main Lambda handler for User Story 3: API Gateway endpoint that accepts addresses
and returns representatives from federal, state, and local government levels.

Feature: 003-address-lookup (User Story 3 - T056-T067)
"""
import time
from typing import Dict, Any, List, Set
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.services.parameter_store import get_api_key
from src.services.google_civic import GoogleCivicClient
from src.services.openstates import OpenStatesClient
from src.utils.validators import validate_address
from src.utils.errors import ApiException, ErrorCode

# T066: Lambda Powertools structured logging
logger = Logger(service="address_lookup")

# T067: X-Ray tracing for end-to-end request tracking
tracer = Tracer(service="address_lookup")


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for API Gateway HTTP API v2 events
    
    Handles GET /representatives?address={address} requests
    
    Args:
        event: API Gateway HTTP API v2 event
        context: Lambda context
    
    Returns:
        HTTP response with status code, headers, and JSON body
    """
    logger.info("Processing address lookup request")
    tracer.put_annotation(key="request_id", value=context.request_id)
    
    try:
        # Extract address from query parameters (T057)
        query_params = event.get('queryStringParameters') or {}
        address = query_params.get('address')
        
        logger.info(f"Looking up representatives for address: {address}")
        
        # T056: Core lookup logic (includes validation)
        result = lookup_representatives_by_address(address)
        
        # T064: Success response (200)
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # CORS
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': result
        }
        
        # Convert body to JSON string
        import json
        response['body'] = json.dumps(result)
        
        logger.info(f"Successfully returned {len(result.get('representatives', []))} representatives")
        return response
        
    except ApiException as e:
        # T063: Format error responses with single error object
        # T064: Map HTTP status codes (400, 404, 500, 503)
        logger.error(f"API exception: {e.code} - {e.message}")
        
        error_response = {
            'statusCode': e.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': {
                'error': {
                    'code': e.code.value,
                    'message': e.message,
                    'details': e.details
                }
            }
        }
        
        import json
        error_response['body'] = json.dumps(error_response['body'])
        return error_response
        
    except Exception as e:
        # T050, T064: Unexpected errors return 500
        logger.exception(f"Unexpected error in address lookup: {str(e)}")
        
        error_response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': {
                'error': {
                    'code': ErrorCode.INTERNAL_ERROR.value,
                    'message': 'An unexpected error occurred',
                    'details': str(e)
                }
            }
        }
        
        import json
        error_response['body'] = json.dumps(error_response['body'])
        return error_response


@tracer.capture_method
def lookup_representatives_by_address(address: str) -> Dict[str, Any]:
    """
    Core business logic for address lookup
    
    Args:
        address: Street address (will be validated)
    
    Returns:
        Dictionary with representatives, metadata, and warnings
    
    Raises:
        ApiException: For various error scenarios (400, 404, 503, etc.)
    """
    # T057: Validate address FIRST before any other operations
    validate_address(address)
    
    # T065: Track response time
    start_time = time.time()
    
    try:
        # T058: Get OCD-IDs from Google Civic API
        logger.info("Retrieving OCD divisions from Google Civic API")
        tracer.put_annotation(key="address", value=address[:50])  # First 50 chars
        
        google_api_key = get_api_key('/represent-app/google-civic-api-key')
        google_client = GoogleCivicClient(api_key=google_api_key)
        divisions = google_client.lookup_divisions(address)
        
        logger.info(f"Found {len(divisions)} divisions")
        tracer.put_metadata(key="division_count", value=len(divisions))
        
        # T059: Get representatives from OpenStates for each division
        logger.info("Retrieving representatives from OpenStates API")
        
        openstates_api_key = get_api_key('/represent-app/openstates-api-key')
        openstates_client = OpenStatesClient(api_key=openstates_api_key)
        
        # T060, T061, T062: Aggregate, deduplicate, and track warnings
        all_representatives: List[Dict[str, Any]] = []
        seen_ids: Set[str] = set()
        warnings: List[str] = []
        government_levels: Set[str] = set()
        
        for division in divisions:
            ocd_id = division['ocd_id']
            division_name = division['name']
            
            try:
                # Get representatives for this division
                reps = openstates_client.get_representatives_by_division(ocd_id)
                
                # T062: Track divisions with no data
                if not reps:
                    warning = f"No representative data available for {division_name} ({ocd_id})"
                    warnings.append(warning)
                    logger.warning(warning)
                    continue
                
                # T060: Deduplication - only add representatives we haven't seen
                for rep in reps:
                    rep_id = rep['id']
                    if rep_id not in seen_ids:
                        seen_ids.add(rep_id)
                        all_representatives.append(rep)
                        
                        # T061: Track government levels
                        gov_level = rep.get('government_level')
                        if gov_level:
                            government_levels.add(gov_level)
                
                logger.info(f"Added {len(reps)} representatives from {division_name}")
                
            except ApiException as e:
                # T062: External service errors become warnings for partial results
                if e.code == ErrorCode.RATE_LIMIT_EXCEEDED:
                    # Rate limit is critical - propagate up
                    raise
                
                # Other errors are warnings
                warning = f"Could not retrieve data for {division_name}: {e.message}"
                warnings.append(warning)
                logger.warning(warning)
                continue
        
        # Calculate response time (T065)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # T065: Build metadata
        metadata = {
            'address': address,
            'division_count': len(divisions),
            'representative_count': len(all_representatives),
            'government_levels': sorted(list(government_levels)),
            'response_time_ms': response_time_ms
        }
        
        logger.info(f"Lookup complete: {len(all_representatives)} unique representatives found")
        tracer.put_annotation(key="total_representatives", value=len(all_representatives))
        
        # Build response
        result = {
            'address': address,
            'representatives': all_representatives,
            'metadata': metadata,
            'warnings': warnings
        }
        
        return result
        
    except ApiException:
        # Re-raise ApiExceptions (they're already formatted)
        raise
        
    except Exception as e:
        # Wrap unexpected exceptions (T050)
        logger.exception(f"Unexpected error in lookup logic: {str(e)}")
        raise ApiException(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred during address lookup",
            status_code=500,
            details=str(e)
        )
