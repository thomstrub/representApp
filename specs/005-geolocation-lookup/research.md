# Research: Geolocation-Based Representative Lookup

**Feature**: 005-geolocation-lookup  
**Date**: 2026-02-10  
**Status**: Complete

## Overview

This document consolidates research findings for replacing the deprecated Google Civic Information API with a geolocation-based flow using Google Maps Geocoding API and OpenStates `/people.geo` endpoint.

## Research Findings

### 1. Google Maps Python Library Integration

**Decision**: Use the official `googlemaps` Python library (https://github.com/googlemaps/google-maps-services-python)

**Rationale**:
- Official Google-maintained library with production-grade reliability
- Provides `geocode()` method that returns latitude/longitude coordinates
- Built-in rate limiting and retry logic
- Comprehensive error handling with specific exception types
- Well-documented with extensive examples
- Active maintenance (last updated 2025)
- Compatible with Python 3.9+ runtime

**Implementation Pattern**:
```python
import googlemaps

# Initialize client with API key
gmaps = googlemaps.Client(key='YOUR_API_KEY')

# Geocode an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Extract coordinates
location = geocode_result[0]['geometry']['location']
lat = location['lat']  # e.g., 37.4224764
lng = location['lng']  # e.g., -122.0842499
```

**Error Handling**:
- `googlemaps.exceptions.ApiError` - API errors (invalid key, billing issues)
- `googlemaps.exceptions.HTTPError` - Network errors
- `googlemaps.exceptions.Timeout` - Timeout errors
- Empty result list - Invalid/unfound address

**Alternatives Considered**:
- Direct REST API calls with `requests` library - Rejected because the googlemaps library provides better error handling, retry logic, and rate limiting out of the box
- `geopy` library - Rejected because it's a generic geocoding library that supports multiple providers, adding unnecessary complexity when we only need Google Maps

**Dependencies**:
- Add to `backend/requirements.txt`: `googlemaps>=4.10.0`

---

### 2. OpenStates Geo Endpoint Usage

**Decision**: Use the `/people.geo` endpoint with latitude and longitude parameters

**Rationale**:
- Direct representative lookup by coordinates (no OCD-ID intermediate step required)
- Returns all representatives (federal, state, local) for a location in one call
- More reliable than Google Civic API (still actively maintained)
- Consistent response structure with existing OpenStates integration

**API Specification**:
- **Endpoint**: `GET https://v3.openstates.org/people.geo`
- **Query Parameters**:
  - `lat` (required): Latitude in WGS84 format (e.g., 47.6105)
  - `lng` (required): Longitude in WGS84 format (e.g., -122.3115)
  - `apikey` (required): OpenStates API key
- **Response**: JSON with `results` array containing representative objects

**Response Structure** (from openstates_endpoint_info.md):
```json
{
  "results": [
    {
      "id": "ocd-person/...",
      "name": "Full Name",
      "party": "Democratic",
      "current_role": {
        "title": "Senator",
        "org_classification": "upper|lower",
        "district": "37",
        "division_id": "ocd-division/..."
      },
      "jurisdiction": {
        "id": "ocd-jurisdiction/...",
        "name": "Washington",
        "classification": "state|country"
      },
      "email": "email@example.com",
      "image": "https://...",
      "given_name": "First",
      "family_name": "Last",
      "birth_date": "1965-06-15"
    }
  ],
  "pagination": {
    "per_page": 10,
    "page": 1,
    "max_page": 1,
    "total_items": 6
  }
}
```

**Implementation Pattern**:
```python
# Add method to OpenStatesClient class
def get_representatives_by_coordinates(self, latitude: float, longitude: float) -> List[Dict[str, Any]]:
    url = f"{self.base_url}/people.geo"
    params = {
        'lat': latitude,
        'lng': longitude,
        'apikey': self.api_key
    }
    response = requests.get(url, params=params, timeout=10)
    # ... error handling ...
    return response.json()['results']
```

**Error Handling**:
- HTTP 401 - Invalid API key → `ApiException(ErrorCode.EXTERNAL_SERVICE_ERROR)`
- HTTP 429 - Rate limit exceeded → `ApiException(ErrorCode.RATE_LIMIT_EXCEEDED)`
- HTTP 500/502/503 - Server errors → `ApiException(ErrorCode.EXTERNAL_SERVICE_ERROR)`
- Timeout - Request timeout → `ApiException(ErrorCode.EXTERNAL_SERVICE_ERROR)`
- Empty `results` array - No representatives found (not an error, return empty list)

**Government Level Detection**:
- Use `jurisdiction.classification` field:
  - `"country"` → federal level
  - `"state"` → state level
  - `"county"` or `"municipality"` → local level

**Alternatives Considered**:
- Continue using OCD-ID based lookup - Rejected because Google Civic API (which provides OCD-IDs) is deprecated, and geo endpoint is more direct
- Use multiple API calls per government level - Rejected because geo endpoint returns all levels in one call, reducing latency and complexity

---

### 3. Error Handling Patterns

**Decision**: Maintain existing `ApiException` and `ErrorCode` patterns with immediate failure (no automatic retries)

**Rationale**:
- Consistent with existing codebase error handling (see `src/utils/errors.py`)
- Frontend already handles these error codes
- Clear user feedback without retry ambiguity
- Aligns with Constitution Principle IV (fail fast, clear error messages)

**Error Code Mapping**:

| Scenario | ErrorCode | HTTP Status | User Message |
|----------|-----------|-------------|--------------|
| Invalid address (geocoding empty result) | `INVALID_REQUEST` | 400 | "Address could not be geocoded. Please verify the address." |
| Geocoding API key invalid | `EXTERNAL_SERVICE_ERROR` | 503 | "Address lookup service temporarily unavailable. Please try again later." |
| Geocoding timeout | `EXTERNAL_SERVICE_ERROR` | 503 | "Address lookup timed out. Please try again." |
| OpenStates rate limit | `RATE_LIMIT_EXCEEDED` | 503 | "Too many requests. Please try again in a few moments." |
| OpenStates timeout | `EXTERNAL_SERVICE_ERROR` | 503 | "Representative lookup timed out. Please try again." |
| OpenStates no data | (no error) | 200 | Return empty results with metadata |

**Implementation Pattern** (consistent with existing code):
```python
from src.utils.errors import ApiException, ErrorCode

try:
    geocode_result = gmaps.geocode(address, timeout=5)
    if not geocode_result:
        raise ApiException(
            code=ErrorCode.INVALID_REQUEST,
            message="Address could not be geocoded. Please verify the address.",
            status_code=400
        )
except googlemaps.exceptions.Timeout:
    raise ApiException(
        code=ErrorCode.EXTERNAL_SERVICE_ERROR,
        message="Address lookup timed out. Please try again.",
        status_code=503
    )
except googlemaps.exceptions.ApiError as e:
    logger.error(f"Google Maps API error: {e}")
    raise ApiException(
        code=ErrorCode.EXTERNAL_SERVICE_ERROR,
        message="Address lookup service temporarily unavailable.",
        status_code=503
    )
```

**Alternatives Considered**:
- Automatic retry logic - Rejected per clarifications session (fail immediately with retry guidance)
- Different error codes - Rejected to maintain frontend compatibility

---

### 4. Parameter Store API Key Management

**Decision**: Store Google Maps API key in AWS Systems Manager Parameter Store at path `/represent-app/google-maps-api-key` (SecureString type)

**Rationale**:
- Consistent with existing pattern (OpenStates API key already in Parameter Store)
- Secure storage with encryption at rest
- IAM-based access control
- Easy key rotation without code changes
- CloudWatch integration for access auditing

**Implementation Pattern** (extend existing `src/utils/parameter_store.py`):
```python
from src.utils.parameter_store import get_parameter

# In handler initialization
GOOGLE_MAPS_API_KEY = get_parameter('/represent-app/google-maps-api-key')
gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
```

**IAM Permissions Required** (add to Lambda execution role):
```json
{
  "Effect": "Allow",
  "Action": [
    "ssm:GetParameter"
  ],
  "Resource": "arn:aws:ssm:*:*:parameter/represent-app/google-maps-api-key"
}
```

**Parameter Creation** (CDK):
```python
# In infrastructure stack
google_maps_api_key = ssm.StringParameter(
    self, "GoogleMapsApiKey",
    parameter_name="/represent-app/google-maps-api-key",
    string_value="<PLACEHOLDER>",  # Replace manually via AWS Console
    type=ssm.ParameterType.SECURE_STRING,
    description="Google Maps Geocoding API key for address lookup"
)
```

**Alternatives Considered**:
- Environment variables - Rejected because Lambda environment variables are not encrypted by default and harder to rotate
- AWS Secrets Manager - Rejected because Parameter Store is sufficient for API keys and cheaper (no rotation automation needed)
- Hardcoded in code - Rejected for obvious security reasons

---

### 5. Data Model Transformation

**Decision**: Transform OpenStates geo response to existing `Representative` model format to maintain frontend contract compatibility

**Rationale**:
- Frontend expects specific field names and structure (no changes allowed per requirements)
- Existing `Representative` model already tested and validated
- Transform layer isolates external API format changes from internal model

**Field Mapping**:

| Representative Model Field | OpenStates Geo Field | Transformation |
|---------------------------|----------------------|----------------|
| `id` | (generate new UUID) | `str(uuid4())` - fresh ID for each API call (no persistence) |
| `name` | `name` | Direct mapping |
| `position` | `current_role.title` | Direct mapping (e.g., "Senator", "Representative") |
| `district` | `current_role.district` | Direct mapping (e.g., "37", "WA-9") |
| `state` | `jurisdiction.name` | Direct mapping (e.g., "Washington", "United States") |
| `party` | `party` | Direct mapping (e.g., "Democratic", "Republican") |
| `contact_info` | (composite) | Build dict: `{"email": email, "phone": None, "image": image}` |
| `created_at` | (current time) | `datetime.utcnow()` |
| `updated_at` | (current time) | `datetime.utcnow()` |

**Implementation Pattern**:
```python
from src.models.domain import Representative
from uuid import uuid4
from datetime import datetime

def transform_openstates_person_to_representative(person: Dict[str, Any]) -> Representative:
    """Transform OpenStates person object to Representative model"""
    return Representative(
        id=str(uuid4()),  # Fresh ID (no persistence)
        name=person['name'],
        position=person['current_role']['title'],
        district=person['current_role'].get('district'),
        state=person['jurisdiction']['name'],
        party=person.get('party'),
        contact_info={
            'email': person.get('email'),
            'phone': None,  # OpenStates geo doesn't include phone
            'image': person.get('image')
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
```

**Government Level Grouping**:
- Use `jurisdiction.classification` to determine level:
  - `"country"` → Federal
  - `"state"` → State
  - `"county"` or `"municipality"` → Local
- Frontend expects representatives grouped by this level

**Alternatives Considered**:
- Create new response model - Rejected to maintain frontend compatibility
- Return raw OpenStates format - Rejected because frontend expects current structure
- Persist IDs to DynamoDB - Rejected per MVP requirements (no persistence, direct API calls)

---

### 6. Timeout Configuration

**Decision**: 
- Geocoding API: 5 second timeout
- OpenStates geo API: 10 second timeout
- Total end-to-end: <3 seconds target (per requirements)

**Rationale**:
- Google Maps typically responds in <1 second for valid addresses
- OpenStates typically responds in <2 seconds
- Conservative timeouts prevent hanging requests
- Lambda timeout should be set to 15 seconds (cushion for cold starts)

**Implementation**:
```python
# Geocoding with timeout
geocode_result = gmaps.geocode(address, timeout=5)

# OpenStates with timeout
response = requests.get(url, params=params, timeout=10)
```

**Alternatives Considered**:
- Shorter timeouts (2s/5s) - Rejected because occasional cold starts or network latency could cause false failures
- Longer timeouts (10s/20s) - Rejected because user experience degrades significantly after 3 seconds
- No timeouts - Rejected because Lambda has 15s max execution time and we need predictable failures

---

## Technology Decisions Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Geocoding | googlemaps Python library | >=4.10.0 | Official library, production-ready |
| Representatives | OpenStates geo endpoint | v3 | Direct coordinate lookup, all levels |
| API Keys | AWS Parameter Store | N/A | Secure, auditable, rotatable |
| Error Handling | ApiException + ErrorCode | Current | Maintains frontend compatibility |
| Timeouts | 5s geocoding, 10s OpenStates | N/A | Balance reliability and UX |

---

## Implementation Sequence

1. **User Story 1 (P1)**: Google Maps geocoding integration
   - Add googlemaps library dependency
   - Create `GoogleMapsClient` service class
   - Implement geocoding with error handling
   - Unit tests for geocoding scenarios

2. **User Story 2 (P2)**: OpenStates geo endpoint integration
   - Add `get_representatives_by_coordinates()` method to `OpenStatesClient`
   - Implement data transformation to Representative model
   - Unit tests for geo endpoint and transformation

3. **User Story 3 (P3)**: End-to-end flow integration
   - Update `AddressLookupHandler` to use new flow
   - Integration tests for complete address → representatives flow
   - Performance validation (<3 seconds)

4. **User Story 4 (P4)**: Cleanup legacy code
   - Remove `GoogleCivicClient` service
   - Remove Google Civic API tests
   - Update documentation
   - Clean up Parameter Store (deprecate old keys)

---

## Open Questions

**Resolved**:
- ✅ Caching strategy → No caching (direct API calls per MVP)
- ✅ Retry logic → Fail immediately with clear error message
- ✅ Ambiguous addresses → Use first (most confident) result from Google

**None remaining**

---

## References

- Google Maps Geocoding API: https://developers.google.com/maps/documentation/geocoding
- googlemaps Python library: https://github.com/googlemaps/google-maps-services-python
- OpenStates API v3: https://docs.openstates.org/api-v3/
- OpenStates geo endpoint: https://v3.openstates.org/people.geo (documented in openstates_endpoint_info.md)
- Existing error handling: `backend/src/utils/errors.py`
- Parameter Store utils: `backend/src/utils/parameter_store.py`
- Representative model: `backend/src/models/domain.py`
