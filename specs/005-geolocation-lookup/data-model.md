# Data Model: Geolocation-Based Representative Lookup

**Feature**: 005-geolocation-lookup  
**Date**: 2026-02-10  
**Status**: Complete

## Overview

This document defines all data models and entities used in the geolocation-based representative lookup flow. The system transforms user addresses into geographic coordinates, queries representative data, and returns structured results matching the existing frontend contract.

---

## Entity Diagrams

### High-Level Data Flow

```
┌─────────────────┐
│ User Address    │ (Input)
│ - address: str  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Geocoding Req   │ (Google Maps API)
│ - address: str  │
│ - timeout: int  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Geocoding Resp  │ (Google Maps API)
│ - lat: float    │
│ - lng: float    │
│ - formatted: str│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OpenStates Req  │ (OpenStates Geo API)
│ - lat: float    │
│ - lng: float    │
│ - apikey: str   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OpenStates Resp │ (OpenStates Geo API)
│ - results: List │
│ - pagination    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Representative  │ (Output - existing model)
│ - id: str       │
│ - name: str     │
│ - position: str │
│ - district: str │
│ - state: str    │
│ - party: str    │
│ - contact_info  │
└─────────────────┘
```

---

## Core Entities

### 1. Geocoding Request

**Purpose**: Input parameters for Google Maps Geocoding API

**Structure**:
```python
{
    "address": str,      # Required: User-provided address (e.g., "1600 Amphitheatre Pkwy, Mountain View, CA")
    "timeout": int       # Required: Request timeout in seconds (default: 5)
}
```

**Validation Rules**:
- `address` must be non-empty string
- `address` should be US address (system focuses on US representatives)
- `timeout` must be positive integer (recommended: 5 seconds)

**Example**:
```python
{
    "address": "1600 Pennsylvania Avenue NW, Washington, DC",
    "timeout": 5
}
```

---

### 2. Geocoding Response

**Purpose**: Google Maps API response containing geographic coordinates

**Structure** (from googlemaps library):
```python
[
    {
        "address_components": [
            {
                "long_name": str,
                "short_name": str,
                "types": List[str]
            }
        ],
        "formatted_address": str,  # e.g., "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA"
        "geometry": {
            "location": {
                "lat": float,      # e.g., 38.8976763
                "lng": float       # e.g., -77.0365298
            },
            "location_type": str,  # e.g., "ROOFTOP", "RANGE_INTERPOLATED", "GEOMETRIC_CENTER"
            "viewport": {
                "northeast": {"lat": float, "lng": float},
                "southwest": {"lat": float, "lng": float}
            }
        },
        "place_id": str,
        "types": List[str]
    }
]
```

**Key Fields Used**:
- `geometry.location.lat` - Latitude for representative lookup
- `geometry.location.lng` - Longitude for representative lookup
- `formatted_address` - Formatted address for user confirmation
- `location_type` - Precision indicator (used for logging/debugging)

**Empty Response**:
- Returns empty list `[]` when address cannot be geocoded
- Indicates invalid or unfound address

**Example**:
```python
[{
    "formatted_address": "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA",
    "geometry": {
        "location": {
            "lat": 38.8976763,
            "lng": -77.0365298
        },
        "location_type": "ROOFTOP"
    },
    "place_id": "ChIJGVtI4by3t4kRr51d_Qm_x58",
    "types": ["street_address"]
}]
```

---

### 3. OpenStates Geo Request

**Purpose**: Query parameters for OpenStates `/people.geo` endpoint

**Structure**:
```python
{
    "lat": float,        # Required: Latitude in WGS84 format (e.g., 47.6105)
    "lng": float,        # Required: Longitude in WGS84 format (e.g., -122.3115)
    "apikey": str,       # Required: OpenStates API key
    "timeout": int       # Required: Request timeout in seconds (default: 10)
}
```

**Validation Rules**:
- `lat` must be valid latitude (-90 to 90)
- `lng` must be valid longitude (-180 to 180)
- `apikey` must be valid OpenStates API key
- `timeout` must be positive integer (recommended: 10 seconds)

**Example**:
```python
{
    "lat": 47.6105,
    "lng": -122.3115,
    "apikey": "your-api-key-here",
    "timeout": 10
}
```

---

### 4. OpenStates Geo Response

**Purpose**: OpenStates API response containing representative data

**Full Structure** (from openstates_endpoint_info.md):
```python
{
    "results": [
        {
            "id": str,                    # OCD person ID (e.g., "ocd-person/55a28978-7661-5a33-a2be-a505a07e2a8e")
            "name": str,                  # Full name (e.g., "Adam Smith")
            "party": str | None,          # Party affiliation (e.g., "Democratic", "Republican", "Independent")
            "current_role": {
                "title": str,             # Position (e.g., "Senator", "Representative")
                "org_classification": str, # "upper" (Senate), "lower" (House/Representatives)
                "district": str,          # District identifier (e.g., "WA-9", "37")
                "division_id": str        # OCD division ID
            },
            "jurisdiction": {
                "id": str,                # OCD jurisdiction ID
                "name": str,              # Jurisdiction name (e.g., "Washington", "United States")
                "classification": str     # "country" (federal), "state", "county", "municipality"
            },
            "given_name": str,            # First name
            "family_name": str,           # Last name
            "image": str | None,          # Photo URL
            "email": str | None,          # Email address or contact form URL
            "gender": str | None,         # Gender
            "birth_date": str | None,     # ISO date format
            "death_date": str | None,     # ISO date format (if deceased)
            "extras": dict,               # Additional metadata (e.g., {"title": "Majority Whip"})
            "created_at": str,            # ISO timestamp
            "updated_at": str,            # ISO timestamp
            "openstates_url": str         # Profile URL
        }
    ],
    "pagination": {
        "per_page": int,                  # Results per page (default: 10)
        "page": int,                      # Current page number
        "max_page": int,                  # Total pages available
        "total_items": int                # Total representatives found
    }
}
```

**Key Fields for Transformation**:
- `name` → Representative.name
- `current_role.title` → Representative.position
- `current_role.district` → Representative.district
- `jurisdiction.name` → Representative.state
- `party` → Representative.party
- `email` → Representative.contact_info['email']
- `image` → Representative.contact_info['image']
- `jurisdiction.classification` → Used for government level grouping

**Empty Response**:
- Returns `{"results": [], "pagination": {...}}` when no representatives found
- Not an error condition (valid coordinates with no data)

**Example**:
```python
{
    "results": [
        {
            "id": "ocd-person/55a28978-7661-5a33-a2be-a505a07e2a8e",
            "name": "Adam Smith",
            "party": "Democratic",
            "current_role": {
                "title": "Representative",
                "org_classification": "lower",
                "district": "WA-9",
                "division_id": "ocd-division/country:us/state:wa/cd:9"
            },
            "jurisdiction": {
                "id": "ocd-jurisdiction/country:us/government",
                "name": "United States",
                "classification": "country"
            },
            "email": "https://adamsmith.house.gov/contact/email-me",
            "image": "https://unitedstates.github.io/images/congress/450x550/S000510.jpg"
        }
    ],
    "pagination": {
        "per_page": 10,
        "page": 1,
        "max_page": 1,
        "total_items": 1
    }
}
```

---

### 5. Representative Model (EXISTING)

**Purpose**: Internal representation of a political representative (maintains frontend contract)

**Structure** (from `backend/src/models/domain.py`):
```python
class Representative(BaseModel):
    """Model for a political representative"""
    id: str                           # UUID v4 (generated fresh, not persisted)
    name: str                         # Full name (e.g., "Adam Smith")
    position: str                     # Position/title (e.g., "Senator", "Representative")
    district: Optional[str] = None    # District (e.g., "WA-9", "37")
    state: str                        # State or jurisdiction (e.g., "Washington", "United States")
    party: Optional[str] = None       # Party affiliation (e.g., "Democratic", "Republican")
    contact_info: Optional[dict] = None  # Contact details: {"email": str, "phone": str, "image": str}
    created_at: datetime              # Timestamp (current time)
    updated_at: datetime              # Timestamp (current time)
```

**Validation**:
- `id` must be valid UUID format (auto-generated if invalid)
- `name` must be non-empty string
- `position` must be non-empty string
- `state` must be non-empty string
- Timestamps auto-generated with current UTC time

**JSON Serialization**:
```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Adam Smith",
    "position": "Representative",
    "district": "WA-9",
    "state": "United States",
    "party": "Democratic",
    "contact_info": {
        "email": "https://adamsmith.house.gov/contact/email-me",
        "phone": null,
        "image": "https://unitedstates.github.io/images/congress/450x550/S000510.jpg"
    },
    "created_at": "2026-02-10T18:30:00Z",
    "updated_at": "2026-02-10T18:30:00Z"
}
```

**Transformation Function** (to be implemented):
```python
def transform_openstates_person_to_representative(person: Dict[str, Any]) -> Representative:
    """Transform OpenStates person object to Representative model"""
    return Representative(
        id=str(uuid4()),  # Fresh UUID (no persistence in MVP)
        name=person['name'],
        position=person['current_role']['title'],
        district=person['current_role'].get('district'),
        state=person['jurisdiction']['name'],
        party=person.get('party'),
        contact_info={
            'email': person.get('email'),
            'phone': None,  # OpenStates geo doesn't include phone numbers
            'image': person.get('image')
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
```

---

### 6. API Response Model

**Purpose**: Final response sent to frontend with grouped representatives

**Structure**:
```python
{
    "representatives": {
        "federal": List[Representative],  # Jurisdiction classification = "country"
        "state": List[Representative],    # Jurisdiction classification = "state"
        "local": List[Representative]     # Jurisdiction classification = "county" or "municipality"
    },
    "metadata": {
        "address": str,          # Geocoded address (formatted_address from Google Maps)
        "coordinates": {
            "latitude": float,
            "longitude": float
        },
        "total_count": int       # Total representatives found across all levels
    }
}
```

**Government Level Grouping Logic**:
```python
def group_by_government_level(representatives: List[Representative], 
                              openstates_data: List[Dict]) -> Dict[str, List[Representative]]:
    """Group representatives by government level based on jurisdiction classification"""
    grouped = {
        "federal": [],
        "state": [],
        "local": []
    }
    
    for rep, data in zip(representatives, openstates_data):
        classification = data['jurisdiction']['classification']
        if classification == 'country':
            grouped['federal'].append(rep)
        elif classification == 'state':
            grouped['state'].append(rep)
        else:  # county, municipality, etc.
            grouped['local'].append(rep)
    
    return grouped
```

**Example Response**:
```python
{
    "representatives": {
        "federal": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Adam Smith",
                "position": "Representative",
                "district": "WA-9",
                "state": "United States",
                "party": "Democratic",
                "contact_info": {
                    "email": "https://adamsmith.house.gov/contact/email-me",
                    "image": "https://unitedstates.github.io/images/congress/450x550/S000510.jpg"
                }
            }
        ],
        "state": [
            {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "Rebecca Saldaña",
                "position": "Senator",
                "district": "37",
                "state": "Washington",
                "party": "Democratic",
                "contact_info": {
                    "email": "rebecca.saldana@leg.wa.gov",
                    "image": "https://leg.wa.gov/memberphoto/27290.jpg"
                }
            }
        ],
        "local": []
    },
    "metadata": {
        "address": "1600 Pennsylvania Avenue NW, Washington, DC 20500, USA",
        "coordinates": {
            "latitude": 38.8976763,
            "longitude": -77.0365298
        },
        "total_count": 2
    }
}
```

---

## Client Configuration

### GoogleMapsClient Configuration

```python
class GoogleMapsClientConfig:
    """Configuration for Google Maps API client"""
    api_key: str              # From Parameter Store: /represent-app/google-maps-api-key
    timeout: int = 5          # Request timeout in seconds
    base_url: str = "https://maps.googleapis.com/maps/api/geocode/json"
```

### OpenStatesClient Configuration (Extended)

```python
class OpenStatesClientConfig:
    """Configuration for OpenStates API client"""
    api_key: str              # From Parameter Store: /represent-app/openstates-api-key
    base_url: str = "https://v3.openstates.org"
    timeout: int = 10         # Request timeout in seconds
    
    endpoints = {
        "geo": "/people.geo",           # NEW: Geo-based lookup
        "people": "/people",            # EXISTING: OCD-ID based lookup (deprecated)
        "jurisdiction": "/jurisdictions"  # EXISTING: Jurisdiction lookup
    }
```

---

## Error Models

### ApiException (EXISTING)

**Purpose**: Standard exception for API errors (maintains existing pattern)

**Structure** (from `backend/src/utils/errors.py`):
```python
class ApiException(Exception):
    """Custom exception for API errors"""
    def __init__(self, code: ErrorCode, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
```

**Error Codes**:
```python
class ErrorCode(str, Enum):
    INVALID_REQUEST = "INVALID_REQUEST"              # 400 - Invalid address
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"      # 503 - API rate limit hit
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR" # 503 - Google Maps or OpenStates error
```

**Example Error Response**:
```python
{
    "error": {
        "code": "INVALID_REQUEST",
        "message": "Address could not be geocoded. Please verify the address.",
        "status_code": 400
    }
}
```

---

## Data Relationships

### Entity Relationship Diagram

```
┌─────────────────────┐
│ AddressLookupHandler│
└──────────┬──────────┘
           │
           ├───► ┌──────────────────┐
           │     │ GoogleMapsClient │
           │     └────────┬─────────┘
           │              │
           │              ▼
           │     ┌──────────────────┐
           │     │ GeocodingResponse│
           │     └────────┬─────────┘
           │              │
           ▼              │
┌─────────────────────┐  │
│ OpenStatesClient    │◄─┘
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ OpenStatesGeoResp   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Representative      │ (List)
│ (Transformed        │
│  & Grouped)         │
└─────────────────────┘
```

---

## Validation Rules Summary

| Entity | Field | Validation |
|--------|-------|------------|
| Geocoding Request | address | Non-empty string |
| Geocoding Request | timeout | Positive integer (5s recommended) |
| Geocoding Response | lat | Float -90 to 90 |
| Geocoding Response | lng | Float -180 to 180 |
| OpenStates Geo Request | lat | Float -90 to 90 |
| OpenStates Geo Request | lng | Float -180 to 180 |
| OpenStates Geo Request | apikey | Non-empty string |
| Representative | id | Valid UUID format |
| Representative | name | Non-empty string |
| Representative | position | Non-empty string |
| Representative | state | Non-empty string |

---

## Persistence Strategy

**MVP (Current Implementation)**:
- **NO persistent storage** for geocoding results or representative data
- Direct API calls on every request
- Fresh UUIDs generated for Representative IDs (not stored)
- Aligns with MVP simplicity and serverless architecture

**Post-MVP (Future Phase 4)**:
- DynamoDB caching layer for frequently requested addresses
- Cache key: Geocoded address (formatted_address)
- TTL: 24 hours (representatives change infrequently)
- Multi-tenancy by state/county

---

## Performance Considerations

| Metric | Target | Notes |
|--------|--------|-------|
| Geocoding latency | <1s typical | Google Maps typically sub-second |
| OpenStates latency | <2s typical | OpenStates typically 1-2s response |
| End-to-end latency | <3s | Combined geocoding + lookup + transformation |
| Timeout thresholds | 5s geocoding, 10s OpenStates | Conservative to prevent hanging requests |
| Lambda timeout | 15s | Includes cold start overhead |

---

## References

- Representative Model: `backend/src/models/domain.py`
- Error Models: `backend/src/utils/errors.py`
- OpenStates Client: `backend/src/services/openstates.py`
- Google Maps Response: https://developers.google.com/maps/documentation/geocoding/overview
- OpenStates Geo Endpoint: `docs/artifacts/openstates_endpoint_info.md`

---

**Last Updated**: 2026-02-10  
**Status**: Complete - Ready for Phase 1 contract generation
