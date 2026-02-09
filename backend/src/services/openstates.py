"""
OpenStates API client for representative information retrieval

This service retrieves comprehensive representative information (names, contact details,
offices, party affiliations) for federal and state officials using OCD identifiers.

Feature: 003-address-lookup (User Story 2 - T032-T037, T040-T041)
API Documentation: https://docs.openstates.org/api-v3/
"""
import requests
from typing import List, Dict, Any
from aws_lambda_powertools import Logger, Tracer

from src.utils.errors import ApiException, ErrorCode
from src.utils.ocd_parser import parse_government_level, parse_ocd_id

logger = Logger(service="openstates_client")
tracer = Tracer(service="openstates_client")


class OpenStatesClient:
    """
    Client for OpenStates API v3
    
    Provides representative lookup functionality by OCD division identifier.
    Handles data transformation from OpenStates format to Representative model.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize OpenStates API client
        
        Args:
            api_key: OpenStates API key for authentication
        """
        self.api_key = api_key
        self.base_url = "https://v3.openstates.org"
        logger.info("OpenStatesClient initialized")
    
    @tracer.capture_method
    def get_representatives_by_division(self, ocd_id: str) -> List[Dict[str, Any]]:
        """
        Get representatives for a specific OCD division
        
        Args:
            ocd_id: OCD division identifier (e.g., "ocd-division/country:us/state:wa")
        
        Returns:
            List of representatives with standardized fields matching Representative model:
            - id: OpenStates person ID (for deduplication)
            - name: Full legal name
            - office: Position title
            - party: Party affiliation (or None)
            - email: Email address (or None)
            - phone: Phone number in XXX-XXX-XXXX format (or None)
            - address: Office mailing address (or None)
            - website: Official website URL (or None)
            - photo_url: Photo URL (or None)
            - government_level: federal, state, or local
            - jurisdiction: Which district/state they represent
        
        Raises:
            ApiException:
                - RATE_LIMIT_EXCEEDED (503) if API rate limit exceeded
                - EXTERNAL_SERVICE_ERROR (503) for network/timeout errors or auth issues
        
        Notes:
            - Empty results (no representatives for division) return empty list, not exception
            - Duplicates are automatically removed by ID (T035)
        """
        logger.info(f"Looking up representatives for division: {ocd_id}")
        tracer.put_annotation(key="ocd_id", value=ocd_id)
        
        # OpenStates only tracks state legislators, not federal or local
        # We need to extract the state code and only query for state-level divisions
        try:
            parsed = parse_ocd_id(ocd_id)
            state_code = parsed.get('state')
            govt_level = parsed.get('government_level')
            
            # OpenStates only has state legislators
            if govt_level != 'state':
                logger.info(f"Skipping non-state division for OpenStates: {ocd_id} (level: {govt_level})")
                tracer.put_annotation(key="representative_count", value=0)
                return []
            
            if not state_code:
                logger.warning(f"Could not extract state code from OCD-ID: {ocd_id}")
                tracer.put_annotation(key="representative_count", value=0)
                return []
            
            jurisdiction = state_code  # Use state abbreviation (e.g., 'wa')
            logger.info(f"Querying OpenStates with jurisdiction: {jurisdiction}")
            
        except ValueError as e:
            logger.warning(f"Invalid OCD-ID format: {ocd_id} - {str(e)}")
            tracer.put_annotation(key="representative_count", value=0)
            return []
        
        # T033: Make API request
        endpoint = f"{self.base_url}/people"
        headers = {
            'X-API-Key': self.api_key,
            'Accept': 'application/json'
        }
        params = {
            'jurisdiction': jurisdiction,
            'per_page': 50  # OpenStates API max is 50
        }
        
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            tracer.put_metadata(key="response_status", value=response.status_code)
            
            # T037: Handle 429 - Rate limit exceeded
            if response.status_code == 429:
                logger.error("Rate limit exceeded for OpenStates API")
                error_data = response.json() if response.text else {}
                error_message = error_data.get("error", "Rate limit exceeded")
                raise ApiException(
                    code=ErrorCode.RATE_LIMIT_EXCEEDED,
                    message="OpenStates API rate limit exceeded. Please try again later.",
                    status_code=503,
                    details=error_message
                )
            
            # Handle 401 - Invalid API key
            if response.status_code == 401:
                logger.error("Invalid API key for OpenStates API")
                raise ApiException(
                    code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                    message="OpenStates API authentication failed",
                    status_code=503,
                    details="Invalid API key"
                )
            
            # Handle other non-200 status codes
            if response.status_code != 200:
                logger.error(f"Unexpected status code from OpenStates API: {response.status_code}")
                raise ApiException(
                    code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                    message=f"OpenStates API returned error: {response.status_code}",
                    status_code=503
                )
            
            # T033, T034: Parse response and transform data
            data = response.json()
            results = data.get("results", [])
            
            # T036: Handle empty results (no data for division)
            if not results:
                logger.info(f"No representatives found for division: {ocd_id}")
                tracer.put_annotation(key="representative_count", value=0)
                return []
            
            # T034: Transform OpenStates response to Representative model format
            representatives = []
            seen_ids = set()  # T035: Track IDs for deduplication
            
            for person_data in results:
                person_id = person_data.get("id")
                
                # T035: Skip duplicates
                if person_id in seen_ids:
                    logger.debug(f"Skipping duplicate representative: {person_id}")
                    continue
                
                seen_ids.add(person_id)
                
                # Extract current role information
                current_role = person_data.get("current_role", {})
                
                # Extract party (handle list format or single value)
                party_data = person_data.get("party", [])
                party = None
                if isinstance(party_data, list) and len(party_data) > 0:
                    party = party_data[0].get("name")
                elif isinstance(party_data, str):
                    party = party_data
                
                # Extract capitol office contact information
                capitol_office = person_data.get("capitol_office", {})
                phone = capitol_office.get("voice")
                address = capitol_office.get("address")
                
                # Extract website from links array
                website = None
                links = person_data.get("links", [])
                for link in links:
                    if link.get("url"):
                        website = link["url"]
                        break
                
                # Get jurisdiction name
                jurisdiction_data = person_data.get("jurisdiction", {})
                jurisdiction = jurisdiction_data.get("name", "Unknown")
                
                # Determine government level from division ID
                division_id = current_role.get("division_id", ocd_id)
                try:
                    government_level = parse_government_level(division_id)
                except ValueError:
                    # Fallback to parsing from OCD-ID if available
                    government_level = parse_government_level(ocd_id)
                
                # Build Representative dictionary
                representative = {
                    "id": person_id,
                    "name": person_data.get("name", ""),
                    "office": current_role.get("title", ""),
                    "party": party,
                    "email": person_data.get("email"),
                    "phone": phone,
                    "address": address,
                    "website": website,
                    "photo_url": person_data.get("image"),
                    "government_level": government_level,
                    "jurisdiction": jurisdiction
                }
                
                representatives.append(representative)
            
            logger.info(f"Successfully retrieved {len(representatives)} representatives")
            tracer.put_annotation(key="representative_count", value=len(representatives))
            
            return representatives
        
        # Handle network timeouts
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout calling OpenStates API: {str(e)}")
            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="OpenStates API request timed out. Service may be unavailable.",
                status_code=503,
                details=str(e)
            )
        
        # Handle connection errors
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error calling OpenStates API: {str(e)}")
            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="Unable to connect to OpenStates API. Service may be unavailable.",
                status_code=503,
                details=str(e)
            )
        
        except ApiException:
            # Re-raise our own exceptions
            raise
        
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error calling OpenStates API: {str(e)}")
            raise ApiException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="An unexpected error occurred while calling OpenStates API",
                status_code=503,
                details=str(e)
            )
