# Data Model: Representative Information

**Feature**: API Integration Research  
**Phase**: 1 - Design & Contracts  
**Date**: 2026-02-07

## Purpose

This document defines the entity models and data structures for representative information as it will be retrieved from government APIs and stored in the application. Models are based on analysis of OpenStates.org, Washington State Legislature API, and Google Civic Information API patterns.

## Core Entities

### 1. Representative

Represents an elected official at any government level (federal, state, or local).

**Entity**: `Representative`

**Fields**:
```python
class Representative:
    id: str                    # Unique identifier (source-specific format)
    name: str                  # Full legal name
    first_name: str            # Given name
    last_name: str             # Family name
    party: str                 # Political party abbreviation (D, R, I, etc.)
    office: str                # Office/title (e.g., "U.S. Senator", "Governor")
    government_level: str      # "federal" | "state" | "local"
    jurisdiction: str          # Jurisdiction name (e.g., "Washington", "King County")
    ocd_id: str               # Open Civic Data Division Identifier
    district: Optional[str]    # District number or name (if applicable)
    
    # Contact Information
    email: Optional[str]       # Official email address
    phone: Optional[str]       # Office phone number
    address: Optional[str]     # Physical office address
    website: Optional[str]     # Official website URL
    
    # Social Media
    twitter: Optional[str]     # Twitter handle
    facebook: Optional[str]    # Facebook profile URL
    instagram: Optional[str]   # Instagram handle
    
    # Media
    photo_url: Optional[str]   # Official photo URL
    
    # Metadata
    term_start: Optional[str]  # Term start date (ISO 8601 format)
    term_end: Optional[str]    # Term end date (ISO 8601 format)
    source_api: str            # Data source (e.g., "openstates", "wa_legislature")
    data_freshness: str        # Timestamp of last data update (ISO 8601)
```

**Validation Rules**:
- `id` must be non-empty string
- `name` must be non-empty string
- `party` must be valid abbreviation (D, R, I, L, G, or empty for non-partisan)
- `office` must be non-empty string
- `government_level` must be one of: "federal", "state", "local"
- `ocd_id` must follow OCD-ID format: `ocd-division/country:us/...`
- `email` must be valid email format or null
- `phone` must be valid phone format or null
- `term_start` and `term_end` must be ISO 8601 date strings or null
- `data_freshness` must be ISO 8601 timestamp

**Relationships**:
- One-to-many with `District` (a representative may serve multiple districts over time)
- Many-to-many with `Issue` (post-MVP: representatives' stances on issues)

**State Transitions**: N/A (data is mostly static, updated periodically)

### 2. District

Represents a political district (congressional, state legislative, local).

**Entity**: `District`

**Fields**:
```python
class District:
    ocd_id: str               # Primary key: OCD Division Identifier
    name: str                 # Human-readable district name
    government_level: str     # "federal" | "state" | "local"
    district_type: str        # "congressional" | "state_senate" | "state_house" | "county" | "city"
    district_number: Optional[str]  # District number (if applicable)
    parent_ocd_id: Optional[str]    # Parent jurisdiction OCD-ID (hierarchical)
    
    # Geographic
    state: str                # State abbreviation (e.g., "WA")
    county: Optional[str]     # County name (if local)
    municipality: Optional[str]  # City/town name (if local)
    
    # Metadata
    source_api: str           # Data source
    data_freshness: str       # Timestamp of last data update
```

**Validation Rules**:
- `ocd_id` must follow OCD-ID format and be unique
- `name` must be non-empty string
- `government_level` must be one of: "federal", "state", "local"
- `district_type` must be valid type for the government level
- `state` must be valid 2-letter state code
- `data_freshness` must be ISO 8601 timestamp

**Relationships**:
- One-to-many with `Representative` (a district may have multiple representatives over time)
- Hierarchical self-relationship via `parent_ocd_id` (e.g., congressional district within state)

**State Transitions**: N/A (districts change only after redistricting, rare updates)

### 3. Location

Represents a user's address or zip code for representative lookup.

**Entity**: `Location`

**Fields**:
```python
class Location:
    id: str                   # Generated UUID for caching
    input_type: str           # "address" | "zipcode"
    
    # Address components (if input_type == "address")
    street: Optional[str]     # Street address
    city: Optional[str]       # City name
    state: Optional[str]      # State abbreviation
    zipcode: Optional[str]    # Zip code (5 or 9 digit)
    
    # Resolved data
    ocd_ids: List[str]        # OCD-IDs for all overlapping jurisdictions
    districts: List[str]      # Human-readable district names
    
    # Metadata
    geocoded: bool            # Whether address was successfully geocoded
    cache_timestamp: str      # Timestamp of cache entry (ISO 8601)
    cache_ttl: int            # Time-to-live in seconds (e.g., 86400 for 24 hours)
```

**Validation Rules**:
- `input_type` must be either "address" or "zipcode"
- If `input_type == "address"`: `street`, `city`, `state`, `zipcode` must all be non-empty
- If `input_type == "zipcode"`: only `zipcode` must be non-empty
- `zipcode` must be 5-digit or 9-digit format (XXXXX or XXXXX-XXXX)
- `ocd_ids` must be array of valid OCD-ID format strings
- `cache_timestamp` must be ISO 8601 timestamp
- `cache_ttl` must be positive integer

**Relationships**:
- Many-to-many with `District` via `ocd_ids` (a location maps to multiple jurisdictions)

**State Transitions**: N/A (locations are cached lookup keys, not stateful entities)

### 4. APIResponse (Meta-entity for caching)

Represents a cached API response for performance optimization.

**Entity**: `APIResponse`

**Fields**:
```python
class APIResponse:
    cache_key: str            # Unique key (e.g., "location:{ocd_id}", "representative:{id}")
    response_data: dict       # JSON serialized API response
    source_api: str           # API provider (e.g., "openstates", "google_civic")
    timestamp: str            # Cache creation timestamp (ISO 8601)
    ttl: int                  # Time-to-live in seconds
    http_status: int          # Original HTTP status code (200, 404, etc.)
```

**Validation Rules**:
- `cache_key` must be unique and non-empty
- `response_data` must be valid JSON-serializable dictionary
- `timestamp` must be ISO 8601 timestamp
- `ttl` must be positive integer
- `http_status` must be valid HTTP status code (200-599)

**Relationships**: N/A (caching meta-entity)

**State Transitions**: 
- `created` → `expired` (after `timestamp + ttl` seconds)
- `expired` → `refreshed` (when cache is re-populated)

## Entity Relationships

```text
Location (1) ----< (M) District (M) >---- (1) Representative
   |                     |
   |                     +--- parent_ocd_id (self-referential hierarchy)
   |
   +--- cached in APIResponse

Representative (1) ---- cached in ----< APIResponse
```

## Data Flow

**Address/Zip Code Lookup Flow**:
1. User provides address or zip code → `Location` entity created
2. Call Google Civic Information API divisions endpoint → resolve to `ocd_ids`
3. For each `ocd_id` → lookup or create `District` entity
4. For each `District` → query primary API (OpenStates/WA State) for `Representative` entities
5. Return all `Representative` entities for the location
6. Cache responses in `APIResponse` entities (24-hour TTL)

**Cache Strategy**:
- Cache key format: `"location:{normalized_address}"` or `"representative:{ocd_id}"`
- Cache TTL: 24 hours for representative data, 7 days for district mappings
- Cache invalidation: Automatic expiration, manual refresh endpoint (post-MVP)

## Field Mapping from API Sources

### OpenStates.org API → Representative

```text
API Field                  → Representative Field
-------------------------------------------------
id                         → id
name                       → name
given_name                 → first_name
family_name                → last_name
party[0].name              → party (abbreviation)
current_role.title         → office
current_role.district      → district
current_role.division_id   → ocd_id
email                      → email
capitol_office.voice       → phone
capitol_office.address     → address
links[0].url               → website
image                      → photo_url
extras.twitter             → twitter
```

### Washington State Legislature API → Representative

```text
API Field                  → Representative Field
-------------------------------------------------
Id                         → id
Name                       → name
FirstName                  → first_name
LastName                   → last_name
Party                      → party
Position                   → office
District                   → district
Email                      → email
Phone                      → phone
Address                    → address
Website                    → website
PhotoUrl                   → photo_url
```

### Google Civic Information API (divisions) → District

```text
API Field                  → District Field
-------------------------------------------------
divisions.{ocd_id}.name    → name
divisions.{ocd_id}.ocd_id  → ocd_id
(parsed from ocd_id)       → government_level
(parsed from ocd_id)       → district_type
(parsed from ocd_id)       → state, county, municipality
```

## DynamoDB Table Design (Future Implementation)

**Table Name**: `RepresentativesTable`

**Partition Key**: `PK` (string)
**Sort Key**: `SK` (string)

**Access Patterns**:
1. Lookup representative by ID: `PK=REP#{id}`, `SK=METADATA`
2. Lookup representatives by OCD-ID: `PK=DISTRICT#{ocd_id}`, `SK=REP#{id}`
3. Lookup cached location: `PK=LOC#{normalized_address}`, `SK=CACHE`
4. Lookup cached API response: `PK=API#{cache_key}`, `SK=RESPONSE`

**Global Secondary Index (GSI)**: `GSI1`
- `GSI1PK`: `government_level` (for filtering by federal/state/local)
- `GSI1SK`: `state#district` (for state-specific queries)

**TTL Attribute**: `ttl` (Unix timestamp for automatic cache expiration)

## Notes

- OCD-ID parsing utility required to extract government level, state, district from OCD-ID format
- Multi-tenant isolation: Use `X-Amz-Tenant-Id` header with state/county as tenant ID
- Data normalization: Handle variations in party names (e.g., "Democrat" → "D", "Republican" → "R")
- Missing data handling: All optional fields default to `null`, frontend displays "Not Available"
- Data freshness: Include `data_freshness` timestamp in all API responses to inform users
