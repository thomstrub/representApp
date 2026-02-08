# Quickstart Guide: API Integration for Representative Lookup

**Feature**: API Integration Research  
**Last Updated**: 2026-02-07  
**Status**: Phase 5 Complete - Patterns Documented

## ⚠️ CRITICAL UPDATE: Google Civic API Deprecated

**Discovery Date**: February 7, 2026  
**Impact**: High - affects MVP architecture

The **Google Civic Information API Representatives endpoint** was shut down in **April 2025**. All address-to-representative lookups via this endpoint return 404 errors. 

**Revised MVP Architecture**: OpenStates-first approach (see [ocd-id-analysis.md](ocd-id-analysis.md) for detailed options)

**Recommended Solution**: 
- Use state selection dropdown → OpenStates query for MVP
- Alternative: Geocoding + OCD-ID construction for better UX
- See implementation patterns below for production-ready code

---

## Overview

This guide provides quick reference for integrating OpenStates.org API to retrieve representative information. It combines findings from research of 3 production repositories and documents 5+ proven implementation patterns.

**Research Sources**:
- openstates/people (YAML data structure)
- openstates/openstates-core (Python backend)
- datamade/my-reps (JavaScript frontend)

**Key Deliverables**:
- [implementation-patterns.md](implementation-patterns.md) - 5+ production-ready patterns
- [ocd-id-analysis.md](ocd-id-analysis.md) - OCD-ID parsing and revised architecture
- [patterns-discovered.md](../.github/memory/patterns-discovered.md) - Repository analysis findings

## Prerequisites

- Python 3.9+
- API keys:
  - ~~Google Civic Information API key~~ (Representatives endpoint deprecated April 2025)
  - **OpenStates.org API key** (free tier, 5,000 req/day) - PRIMARY DATA SOURCE
- AWS Lambda environment (for deployment)
- DynamoDB table (for caching)
- AWS Systems Manager Parameter Store (for API key storage)

## Quick Integration Steps

### 1. Register for API Keys
~~Google Civic Information API~~** (DEPRECATED):
- Representatives endpoint shut down April 2025
- Do not use for MVP implementation
- See [ocd-id-analysis.md](ocd-id-analysis.md) for alternatives

**OpenStates.org API** (PRIMARY)
**OpenStates.org API**:
1. Go to [OpenStates Signup](https://openstates.org/accounts/signup/)
2. Create free account
3. Generate API key from dashboard
4. Note: Free tier = 5,000 requests/day, 10 requests/second

### 2. Store API Keys Securely

**AWS Systems Manager Parameter Store** (✅ Verified - T003):
```bash
# Store Google API key
aws ssm OpenStates API key (PRIMARY)
  --name "/represent-app/api-keys/openstates" \
  --value "YOUR_OPENSTATES_API_KEY" \
  --type "SecureString" \
  --description "OpenStates.org API key"
```

**Access in Lambda** (✅ Documented - T007):
```python
import boto3
from functools import lru_cache

ssm = boto3.client('ssm')

@lru_cache(maxsize=2)
def get_api_key(parameter_name: str) -> str:
    """Retrieve API key from Parameter Store with caching"""
    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

# Cache keys in Lambda global scope (reused across invocations)
GOOGLE_API_KEY = get_api_key('/represent-app/api-keys/google-civic')
OPENSTATES_API_KEY = get_api_key('/represent-app/api-keys/openstates')
```

**Authentication Patterns** (✅ Verified - T005, T006):

| API | Method | Example |
|-----|--------|---------|
| **OpenStates** | Header `X-API-Key` | `X-API-Key: {OPENSTATES_API_KEY}` |

```python
# Google Civic API - Query param authentication (T005 verified)
import requests
6):

| API | Method | Status |
|-----|--------|--------|
| ~~Google Civic~~ | ~~Query parameter `key`~~ | ❌ DEPRECATED |
| **OpenStates** | Header `X-API-Key` | ✅ ACTIVE |

```python
# OpenStates API - Header authentication (T006 verified)
import requests
### 3. Implement OCD-ID Resolution

**Purpose**: Convert address/zip code to OCD Division IDs

```python
import requests
from typing import List, Dict

def resolve_address_to_ocd_ids(address: str, api_key: str) -> List[str]:
    """
    Call Google Civic divisions endpoint to get OCD-IDs for address.
    
    Args:
        address: Full address or zip code string
        api_key: Google Civic API key
    
    Returns:
        List of OCD-ID strings (e.g., ["ocd-division/country:us/state:wa/sldu:43"])
    """
    url = "https://www.googleapis.com/civicinfo/v2/divisions"
    params = {
        "query": addressConstruction (MVP Approach)

**Purpose**: Build OCD-IDs from state selection for OpenStates query

**⚠️ Note**: Google Civic address-to-OCD-ID endpoint deprecated. MVP uses state selection dropdown instead.

```python
from typing import Optional

def construct_state_ocd_id(state_abbr: str) -> str:
    """
    Construct OCD jurisdiction ID for state-level query.
    
    Args:
        state_abbr: 2-letter state code (e.g., 'wa')
    
    Returns:
        OCD jurisdiction ID for OpenStates query
    
    Example:
        >>> construct_state_ocd_id('wa')
        'ocd-jurisdiction/country:us/state:wa/government'
    """
    return f"ocd-jurisdiction/country:us/state:{state_abbr.lower()}/government"

def construct_division_ocd_id(
    state_abbr: str,
    division_type: str,
    district: str
) -> str:
    """
    Construct OCD division ID for specific district.
    
    Args:
        state_abbr: 2-letter state code (e.g., 'wa')
        division_type: 'cd', 'sldu', 'sldl', 'county', 'place'
        district: District number or name
    
    Returns:
        OCD division ID
    
    Examples:
        >>> construct_division_ocd_id('wa', 'cd', '7')
        'ocd-division/country:us/state:wa/cd:7'
        
        >>> construct_division_ocd_id('wa', 'sldu', '43')
        'ocd-division/country:us/state:wa/sldu:43'
    """
    return f"ocd-division/country:us/state:{state_abbr.lower()}/{division_type}:{district}"

# Example usage (MVP approach)
jurisdiction_id = construct_state_ocd_id('wa')
# Query all WA legislators, then filter/group on frontend
```

**For address-based lookup**: See [ocd-id-analysis.md](ocd-id-analysis.md) Option B (geocoding + construction) or Option C (pre-built database) Returns:
        Dictionary with parsed components
    """
    parts = ocd_id.split("/")
    
    result = {
        "ocd_id": ocd_id,
        "country": None,
        "state": None,
        "district_type": None,
        "district_number": None,
        "government_level": None
    }
    
    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            
            if key == "country":
                result["country"] = value
            elif key == "state":
                result["state"] = value
                result["government_level"] = GovernmentLevel.STATE.value
            elif key == "cd":  # Congressional District
                result["district_type"] = "congressional"
                result["district_number"] = value
                result["government_level"] = GovernmentLevel.FEDERAL.value
            elif key == "sldu":  # State Senate (upper)
                result["district_type"] = "state_senate"
                result["district_number"] = value
                result["government_level"] = GovernmentLevel.STATE.value
            elif key == "sldl":  # State House (lower)
                result["district_type"] = "state_house"
                result["district_number"] = value
                result["government_level"] = GovernmentLevel.STATE.value
            elif key in ["county", "place"]:
                result["district_type"] = key
                result["government_level"] = GovernmentLevel.LOCAL.value
    
    return result

# Example usage
parsed = parse_ocd_id("ocd-division/country:us/state:wa/sldu:43")
# Returns: {
#   "ocd_id": "ocd-division/country:us/state:wa/sldu:43",
#   "country": "us",
#   "state": "wa",
#   "district_type": "state_senate",
#   "district_number": "43",
#   "government_level": "state"
# }
```

### 5. Query Representatives (OpenStates-First Approach)

**Purpose**: Fetch all representatives for a state jurisdiction

```python
def get_all_state_legislators(
    state_abbr: str,
    api_key: str
) -> List[Dict]:
    """
    Query OpenStates API for all legislators in a state.
    
    This is the MVP approach - get all state legislators,
    then filter/display on frontend based on user selections.
    
    Args:
        state_abbr: 2-letter state code (e.g., "wa")
        api_key: OpenStates API key
    
    Returns:
        List of legislator dictionaries with full details
    
    Rate Limits:
        - Free tier: 5,000 requests/day
        - 10 requests/second
        - Caching recommended (24-hour TTL)
    """
    jurisdiction_id = f"ocd-jurisdiction/country:us/state:{state_abbr.lower()}/government"
    
    url = "https://v3.openstates.org/people"
    headers = {
        "X-API-Key": api_key
    }
    params = {
        "jurisdiction": jurisdiction_id,
        "per_page": 100
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    return data.get("results", [])

# Example usage - MVP approach
legislators = get_all_state_legislators("wa", OPENSTATES_API_KEY)

# Frontend filters by:
# - Chamber (upper/lower)
# - Party
# - District (if user enters district number)
# - Search by name
```

### 6. Implement Multi-Layer Caching

**Purpose**: Reduce API calls and improve performance

```python
import json
from datetime import datetime, timedelta
**Pattern**: See [implementation-patterns.md](implementation-patterns.md) Pattern 2 for full implementation

**Summary**:
- **Layer 1 (Hot)**: Lambda memory with `@lru_cache` - Zero latency
- **Layer 2 (Warm)**: DynamoDB cache table - 1-hour TTL
- **Layer 3 (Cold)**: DynamoDB data table - 24-hour refresh

```python
from functools import lru_cacheto3

dynamodb = boto3.resource('dynamodb')
cache_table = dynamodb.Table('RepresentativesCache')

# Layer 1: Lambda memory cache (warm environment)
memory_cache = {}

def get_cached_or_fetch(cache_key: str, fetch_function, ttl_seconds: int = 86400):
    """
    Multi-layer cache: Lambda memory → DynamoDB → API fetch
    
    Args:
        cache_key: Unique cache identifier
        fetch_function: Function to call if cache miss
        ttl_seconds: Time-to-live in seconds (default 24 hours)
    
    Returns:
        Cached or freshly fetched data
    """
    # Layer 1: Check memory cache
    if cache_key in memory_cache:
        cached_data, expiry = memory_cache[cache_key]
        if datetime.now() < expiry:
            return cached_data
    
    # Layer 2: Check DynamoDB cache
    try:
        response = cache_table.get_item(Key={'cache_key': cache_key})
        if 'Item' in response:
            item = response['Item']
            expiry = datetime.fromisoformat(item['expiry'])
            if datetime.now() < expiry:
                data = json.loads(item['data'])
                # Populate memory cache
                memory_cache[cache_key] = (data, expiry)
                return data
    except Exception as e:
        print(f"DynamoDB cache error: {e}")
    
    # Layer 3: Fetch from API
    data = fetch_function()
    
    # Store in both caches
    expiry = datetime.now() + timedelta(seconds=ttl_seconds)
    memory_cache[cache_key] = (data, expiry)
    
    try:
        cache_table.put_item(Item={
            'cache_key': cache_key,
            'data': json.dumps(data),
            'expiry': expiry.isoformat(),
            'ttl': int(expiry.timestamp())  # DynamoDB TTL attribute
        })
    except Exception as e:
        print(f"DynamoDB cache write error: {e}")
    
    return data
MVP Flow (State Selection Approach)

**Purpose**: OpenStates-first architecture for MVP simplicity

```python
@lru_cache(maxsize=50)
def get_legislators_cached(state_abbr: str) -> List[Dict]:
    """
    Get all legislators for a state with multi-layer caching.
    
    MVP Flow:
    1. User selects state from dropdown
    2. Lambda queries OpenStates (with cache)
    3. Lambda returns all legislators
    4. Frontend filters/displays based on user preferences
    
    Cache Strategy:
    - Lambda memory: Automatic via @lru_cache
    - DynamoDB: 24-hour TTL for legislator data
    - Refresh: Background job or user-triggered
    
    Args:
        state_abbr: 2-letter state code (e.g., 'wa')
    
    Returns:
        List of legislator dictionaries
    """
    # Check DynamoDB cache first
    cache_key = f"legislators:{state_abbr}"
    cached_data = get_from_dynamodb_cache(cache_key, ttl_seconds=86400)
    
    if cached_data:
        return cached_data
    
    # Cache miss - fetch from API
    legislators = get_all_state_legislators(state_abbr, OPENSTATES_API_KEY)
    
    # Store in DynamoDB for next request
    put_to_dynamodb_cache(cache_key, legislators, ttl_seconds=86400)
    
    return legislators

# Lambda handler for MVP
def lambda_handler(event, context):
    """
    GET /legislators?state=wa
    
    Returns all legislators for selected state.
    Frontend handles filtering and display.
    """
    state = event['queryStringParameters']['state']
    
    try:
        legislators = get_legislators_cached(state)
        
        return {
            'statusCode': 

**See**: [implementation-patterns.md](implementation-patterns.md) Pattern 4 for complete implementation

### Quick Reference200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'state': state,
                'count': len(legislators),
                'legislators': legislators
            })
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
```

**Frontend Implementation** (simplified):
```javascript
// User selects state
const state = 'WA';

// Call Lambda API
const response = await fetch(`/api/legislators?state=${state}`);
const data = await response.json();

// Filter by chamber (optional)
const senators = data.legislators.filter(
  leg => leg.current_role?.type === 'upper'
);

const representatives = data.legislators.filter(
  leg => leg.current_role?.type === 'lower'
);

// Display in UI with grouping, search, etc.
```

---

## Implementation Patterns (Phase 5 Complete)

---

## Next Steps

### Immediate (MVP Implementation):
1. ✅ **Phase 1-4 Complete**: API setup, verification, GitHub analysis, OCD-ID testing
2. ✅ **Phase 5 Complete**: Pattern documentation (5+ patterns extracted)
3. **Phase 6** (Next): API comparison and selection rationale (T032-T039)
4. **Phase 7** (Final research): Implementation plan synthesis (T040-T052)
5. **Implementation Phase**: Begin MVP development using documented patterns

### Future Enhancements:
- Address-based lookup (requires geocoding service)
- Congressional district mapping
- County and local official lookup
- Real-time data updates

---

### Phase 4: Error Handling
- [ ] Implement circuit breaker pattern (Pattern 4)
- [ ] Add graceful degradation (return stale cache on errors)
- [ ] Configure CloudWatch alarms for errors
- [ ] Test rate limit handling (429 responses)
- [ ] Test server error scenarios (5xx responses)

### Phase 5: Testing & Validation
- [ ] Unit tests for OCD-ID construction
- [ ] Integration tests for OpenStates API calls
- [ ] Load testing (simulate rate limit approach)
- [ ] Cache performance testing
- [ ] Error scenario testing

### Phase 6: Frontend Integration
- [ ] Create state selection dropdown (50 states)
- [ ] Implement API call to Lambda
- [ ] Add filtering by chamber, party, district
- [ ] Display legislator cards with contact info
- [ ] Handle loading and error states

---

## Integration Flow Diagram (T031)

```
┌─────────────────────────────────────────────────────────────┐
│                         MVP FLOW                            │
│                  (OpenStates-First Approach)                │
└─────────────────────────────────────────────────────────────┘

Frontend                Lambda                  OpenStates API
   │                       │                          │
   │  1. User selects     │                          │
   │     state (WA)       │                          │
   ├──────────────────────>                          │
   │  GET /legislators    │                          │
   │  ?state=wa           │                          │
   │                      │                          │
   │                      │  2. Check Lambda         │
   │                      │     memory cache         │
   │                      │     (@lru_cache)         │
   │                      │                          │
   │                      │  3. Check DynamoDB       │
   │                      │     cache (24h TTL)      │
   │                      │     [MISS]               │
   │                      │                          │
   │                      ├─────────────────────────>│
   │                      │  4. GET /people          │
   │                      │     ?jurisdiction=       │
   │                      │     ocd-jurisdiction/... │
   │                      │                          │
   │                      │<─────────────────────────┤
   │                      │  5. Return legislators   │
   │                      │     (JSON)               │
   │                      │                          │
   │                      │  6. Parse & validate     │
   │                      │     (Pydantic models)    │
   │                      │                          │
   │                      │  7. Store in caches      │
   │                      │     - Lambda memory      │
   │                      │     - DynamoDB (24h)     │
   │                      │                          │
   │<──────────────────────────────────────────────  │
   │  8. Return JSON      │                          │
   │     {legislators:[]} │                          │
   │                      │                          │
   │  9. Filter & display │                          │
   │     - By chamber     │                          │
   │     - By party       │                          │
   │     - By district    │                          │
   │     - Search name    │                          │
   │                      │                          │


CACHE HIT Flow (subsequent requests):
   │                      │                          │
   ├──────────────────────>                          │
   │  GET /legislators    │  Lambda memory hit       │
   │  ?state=wa           │  (Instant return)        │
   │<─────────────────────┤                          │
   │  Return cached data  │                          │
   │  < 100ms             │                          │
   │                      │                          │


ERROR HANDLING Flow:
   │                      │                          │
   ├──────────────────────>                          │
   │                      ├─────────────────────────>│
   │                      │  API call fails (5xx)    │
   │                      │<─────────────────────────┤
   │                      │  Retry with backoff      │
   │                      │  (3 attempts)            │
   │                      │                          │
   │                      │  All retries failed      │
   │                      │  → Check DynamoDB        │
   │                      │  → Return stale cache    │
   │                      │     (if available)       │
   │<─────────────────────┤                          │
   │  Return cached data  │                          │
   │  (may be stale)      │                          │
   │                      │                          │
```

### Flow Notes:

1. **State Selection** (MVP): User chooses state from dropdown - simplest UX
2. **Caching Layers**: Three-tier approach minimizes API calls
3. **Lambda Memory**: Fastest cache, survives container reuse
4. **DynamoDB Cache**: Shared across Lambda instances, 24-hour TTL
5. **Retry Logic**: Exponential backoff for transient failures
6. **Graceful Degradation**: Return stale cache on API errors
7. **Frontend Filtering**: Client-side for responsive UX

### Future Enhancements:

- **Address Input** (Phase 2): Geocoding service + OCD-ID construction
- **Auto-detection** (Phase 3): IP geolocation for default state
- **District Lookup** (Phase 3): Map address to specific districts

---

## Performance Targets

- **Cache Hit**: < 100ms response time (Lambda memory)
- **Cache Miss**: < 3 seconds response time (API call + processing)
- **Cache TTL**: 24 hours for legislators
- **Error Rate**: < 1% of requests
- **Rate Limit Buffer**: Stay under 80% of daily quota (4,000/5,000 req/day)

---

## Test Coverage (Phase 4 Complete)

**Test Addresses Used** (see [ocd-id-test-results.json](ocd-id-test-results.json)):
- Urban (Seattle, WA)
- Rural (Spokane, WA)
- Zip code only
- Military address (APO)
- PO Box
- Multi-state coverage (CA, NY, TX, FL, MA)

**Results**: All address tests failed (404) → Google Civic API deprecated → Pivot to state selection approach

---append(rep)
    
    return filtered_reps

# Example usage
representatives = lookup_representatives("123 Main St, Seattle, WA 98101")
```

## Error Handling Patterns

### Retry with Exponential Backoff

```python
import time
from requests.exceptions import HTTPError

def api_call_with_retry(func, max_retries=3, base_delay=1):
    """Retry API calls with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                delay = base_delay * (2 ** attempt)
                print(f"Rate limited. Retrying in {delay}s...")
                time.sleep(delay)
            elif e.response.status_code >= 500:  # Server error
                delay = base_delay * (2 ** attempt)
                print(f"Server error. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise
    
    raise Exception(f"Max retries ({max_retries}) exceeded")
```

### Graceful Degradation

```python
def safe_api_call(func, fallback_value=None):
    """Call API with fallback on failure"""
    try:
        return func()
    except Exception as e:
        print(f"API call failed: {e}")
        return fallback_value

# Example usage
reps = safe_api_call(
    lambda: get_representatives_by_jurisdiction("wa", OPENSTATES_API_KEY),
    fallback_value=[]
)
```

## Testing

### Test Addresses for Coverage Validation

Use these diverse addresses to test OCD-ID resolution and representative lookup:

1. **Urban (Seattle, WA)**: `1301 4th Ave, Seattle, WA 98101`
2. **Rural (Eastern WA)**: `123 Main St, Spokane, WA 99201`
3. **Zip Code Only**: `98101`
4. **Military (APO)**: `PSC 1234, Box 5678, APO AP 96350`
5. **PO Box**: `PO Box 123, Olympia, WA 98504`
6. **Washington DC**: `1600 Pennsylvania Ave NW, Washington, DC 20500`
7. **California**: `1 Dr Carlton B Goodlett Pl, San Francisco, CA 94102`
8. **New York**: `1 City Hall Plaza, Boston, MA 02201`
9. **Texas**: `1100 Congress Ave, Austin, TX 78701`
10. **Florida**: `400 S Orange Ave, Orlando, FL 32801`

## Performance Targets

- **Cache Hit**: < 500ms response time
- **Cache Miss**: < 3 seconds response time
- **Cache TTL**: 24 hours for representatives, 7 days for divisions
- **Error Rate**: < 1% of requests

## Next Steps

1. Implement Lambda handler using patterns above
2. Create DynamoDB table with TTL enabled
3. Set up CloudWatch alarms for API errors and latency
4. Test with 6-10 diverse addresses
5. Monitor rate limits and quota usage
6. Document any API limitations discovered during testing

## Additional Resources

- [OpenStates API Documentation](https://docs.openstates.org/api-v3/)
- [Google Civic Information API](https://developers.google.com/civic-information/docs/v2)
- [OCD-ID Format Specification](https://opencivicdata.readthedocs.io/en/latest/proposals/0002.html)
- [AWS Lambda Powertools Python](https://awslabs.github.io/aws-lambda-powertools-python/)
