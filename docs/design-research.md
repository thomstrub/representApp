# Design Research: Implementation Instructions from Repository Analysis

## Purpose

This document contains implementation instructions derived from analysis of three civic tech repositories (datamade/my-reps, elisabethvirak/Know_Your_Congress, and nrenner0211/elect.io). These action items should be implemented by an agent or developer at a later time to enhance the Represent App.

## Context

The following patterns were identified as valuable implementations from production civic tech applications. They have been validated in real-world deployments and should be adapted to Represent App's serverless AWS architecture.

---

## Action Item 1: Implement Google Civic Information API Integration

### Priority: High (MVP)

### Objective
Integrate Google Civic Information API as the primary data source for representative lookups based on user location (zip code or address).

### Implementation Steps

1. **API Configuration**
   - Register for Google Civic Information API key
   - Store API key securely in AWS Systems Manager Parameter Store or Secrets Manager
   - Configure API endpoint: `https://www.googleapis.com/civicinfo/v2/representatives`

2. **Lambda Function Integration**
   - Create or update Lambda handler in `backend/src/handlers/api.py`
   - Add API request function using `requests` or `boto3` for HTTP calls
   - Implement caching layer in DynamoDB with 24-hour TTL
   - Add error handling for API failures (rate limits, timeouts, invalid responses)

3. **Request Parameters**
   - Accept address or zip code as input parameter
   - Validate input format before making API call
   - Format request: `GET /representatives?address={user_address}&key={api_key}`

4. **Response Handling**
   - Parse API response JSON structure
   - Extract `offices` and `officials` arrays
   - Map officials to offices using index references
   - Transform to internal Representative data model

5. **Error Scenarios**
   - Handle 400 errors (invalid address)
   - Handle 404 errors (no data for location)
   - Handle 429 errors (rate limit) with exponential backoff
   - Handle 503 errors (service unavailable) with graceful degradation

### Code Pattern Reference
```python
# Example based on datamade/my-reps
def fetch_representatives(address: str) -> dict:
    """Fetch representatives from Google Civic API"""
    url = "https://www.googleapis.com/civicinfo/v2/representatives"
    params = {
        "address": address,
        "key": get_api_key()  # From Parameter Store
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise APIError("Failed to fetch representative data")
```

### Testing Requirements
- Unit tests with mocked API responses
- Integration tests with real API calls (rate-limited)
- Test edge cases: invalid zip codes, missing data fields, API failures
- Performance tests to ensure <3 second response time

### Dependencies
- Add to `backend/requirements.txt`: `requests>=2.31.0`
- AWS Systems Manager for API key storage
- DynamoDB table for caching

---

## Action Item 2: Implement OCD Division ID Parsing for Government Level Categorization

### Priority: High (MVP)

### Objective
Parse Open Civic Data (OCD) division IDs returned by Google Civic API to categorize representatives by government level (federal, state, county, local).

### Implementation Steps

1. **Create Utility Module**
   - Add new file: `backend/src/utils/ocd_parser.py`
   - Implement regex patterns for each government level
   - Create categorization function

2. **Regex Patterns to Implement**
   ```python
   import re
   
   # Pattern definitions from datamade/my-reps
   FEDERAL_PATTERN = "ocd-division/country:us"
   STATE_PATTERN = re.compile(r"ocd-division/country:us/state:(\D{2})$")
   CD_PATTERN = re.compile(r"ocd-division/country:us/state:\D{2}/cd:\d+$")
   COUNTY_PATTERN = re.compile(r"ocd-division/country:us/state:\D{2}/county:[\w_]+$")
   PLACE_PATTERN = re.compile(r"ocd-division/country:us/state:\D{2}/place:[\w_]+$")
   LOCAL_PATTERN = re.compile(r"ocd-division/country:us/state:\D{2}/(.*?):(.*?)")
   ```

3. **Categorization Function**
   ```python
   def categorize_division(division_id: str) -> str:
       """Categorize a division ID into government level"""
       if division_id == FEDERAL_PATTERN:
           return "federal"
       elif STATE_PATTERN.match(division_id):
           return "state"
       elif CD_PATTERN.match(division_id):
           return "federal"  # Congressional districts are federal
       elif COUNTY_PATTERN.match(division_id):
           return "county"
       elif PLACE_PATTERN.match(division_id) or LOCAL_PATTERN.match(division_id):
           return "local"
       else:
           return "unknown"
   ```

4. **Integration with Representative Model**
   - Add `government_level` field to Representative model in `backend/src/models/domain.py`
   - Apply categorization during data transformation from API response
   - Store categorized data in DynamoDB

5. **Frontend Filtering Support**
   - Add query parameter support: `GET /api/representatives?zip={zip}&level={federal|state|county|local}`
   - Filter representatives by level in Lambda handler
   - Return categorized groups in response

### Testing Requirements
- Unit tests for each regex pattern with valid division IDs
- Test edge cases: unknown formats, malformed IDs
- Test filtering endpoint with various level parameters

### Documentation
- Document OCD division ID format in API documentation
- Add examples of division IDs for each level
- Reference: https://github.com/opencivicdata/ocd-division-ids

---

## Action Item 3: Design and Implement DynamoDB Schema Based on Representative Data Structure

### Priority: High (MVP)

### Objective
Create an optimized DynamoDB schema to store representative data with support for multi-tenant architecture and efficient querying by location.

### Implementation Steps

1. **Table Design**
   - Table name: `RepresentativesTable`
   - Primary key: Partition key (PK): `TENANT#{state_code}`, Sort key (SK): `REP#{representative_id}`
   - GSI for zip code lookups: `ZipCodeIndex` with PK: `ZIP#{zipcode}`, SK: `LEVEL#{level}`

2. **Data Model Structure**
   ```python
   # Based on Google Civic API structure and Know_Your_Congress patterns
   {
       "PK": "TENANT#CA",
       "SK": "REP#gov_gavin_newsom",
       "representativeId": "gov_gavin_newsom",
       "name": "Gavin Newsom",
       "office": "Governor",
       "party": "Democratic",
       "divisionId": "ocd-division/country:us/state:ca",
       "governmentLevel": "state",  # federal, state, county, local
       
       # Contact information (optional fields)
       "phones": ["(916) 445-2841"],
       "emails": ["governor@gov.ca.gov"],
       "urls": ["https://www.gov.ca.gov/"],
       "address": {
           "line1": "1303 10th Street, Suite 1173",
           "city": "Sacramento",
           "state": "CA",
           "zip": "95814"
       },
       
       # Social media (optional)
       "channels": [
           {"type": "Twitter", "id": "GavinNewsom"},
           {"type": "Facebook", "id": "GavinNewsom"}
       ],
       
       # Photo
       "photoUrl": "https://example.com/photo.jpg",
       
       # Metadata
       "zipCodes": ["95814", "94102", ...],  # For GSI
       "lastUpdated": "2026-02-07T12:00:00Z",
       "dataSource": "google_civic_api",
       "ttl": 1738951200  # Unix timestamp for 24-hour cache
   }
   ```

3. **Multi-Tenancy Support**
   - Tenant ID = State code (e.g., "CA", "NY", "TX")
   - Use Lambda tenant isolation mode with `X-Amz-Tenant-Id` header
   - Partition data by state for efficient isolation

4. **Index Strategy**
   - **Primary Access Pattern**: Get representatives by state and ID
     - Query: PK = "TENANT#{state}", SK begins_with "REP#"
   
   - **Zip Code Lookup** (GSI: ZipCodeIndex):
     - Query: PK = "ZIP#{zipcode}", optional filter on SK = "LEVEL#{level}"
     - Duplicate items across zip codes in same representative's jurisdiction
   
   - **Level Filtering**:
     - Add `governmentLevel` attribute for client-side filtering
     - Or use sparse GSI if needed for backend filtering

5. **Cache Strategy**
   - Set TTL attribute for automatic expiration after 24 hours
   - Enable DynamoDB TTL on the table
   - Implement cache refresh logic in Lambda when TTL expires

6. **Update `backend/src/models/store.py`**
   - Add methods: `get_by_zip_code()`, `get_by_tenant_and_level()`
   - Implement batch write for populating multiple representatives
   - Add cache hit/miss logging

### Testing Requirements
- Test multi-tenant isolation (different states don't interfere)
- Test zip code queries return correct representatives
- Test TTL expiration and refresh logic
- Performance test query latency (<100ms)

### Migration Path
- Create migration script to populate table from Google Civic API
- Support backfill for all US zip codes (phased approach by state)

---

## Action Item 5: Implement Representative Data Caching Strategy

### Priority: High (MVP)

### Objective
Implement a multi-layer caching strategy to minimize external API calls, reduce latency, and improve cost efficiency.

### Implementation Steps

1. **Cache Layer Design**
   ```
   Request Flow:
   User Request → Lambda → Memory Cache (check) → DynamoDB Cache (check) → Google Civic API → Store in caches → Return
   ```

2. **Lambda Memory Cache (Warm Execution Environment)**
   - Use Python dictionary or `functools.lru_cache`
   - Cache representative data for current Lambda invocation
   - Automatically cleared when Lambda cold starts
   - Per-tenant isolation via Lambda tenant mode
   
   ```python
   from functools import lru_cache
   
   # Cache API responses in Lambda memory
   @lru_cache(maxsize=100)
   def get_representatives_cached(zip_code: str, tenant_id: str) -> dict:
       """Memory-cached representative lookup"""
       # Check DynamoDB first, then API
       pass
   ```

3. **DynamoDB Persistent Cache**
   - Store API responses with 24-hour TTL
   - Schema includes `lastUpdated` and `ttl` attributes
   - Enable DynamoDB TTL for automatic expiration
   
   **TTL Strategy:**
   - Representative information: 24 hours (86400 seconds)
   - Reason: Representative contact info changes infrequently
   - Voting records (post-MVP): 1 hour (3600 seconds)
   - Reason: Vote data updates frequently during congressional sessions

4. **Cache Logic Implementation**
   ```python
   def get_representatives_by_zip(zip_code: str, tenant_id: str) -> List[Representative]:
       """Multi-layer cache lookup"""
       
       # Layer 1: Check Lambda memory cache
       cached = _memory_cache.get(f"{tenant_id}:{zip_code}")
       if cached and not _is_expired(cached):
           logger.info("Cache hit: memory")
           return cached
       
       # Layer 2: Check DynamoDB cache
       cached_items = store.query_by_zip(zip_code, tenant_id)
       if cached_items:
           # Check if cache is fresh (within TTL)
           if all(_is_fresh(item) for item in cached_items):
               logger.info("Cache hit: DynamoDB")
               _memory_cache[f"{tenant_id}:{zip_code}"] = cached_items
               return cached_items
       
       # Layer 3: Fetch from Google Civic API
       logger.info("Cache miss: fetching from API")
       api_data = fetch_from_google_civic_api(zip_code)
       representatives = transform_api_response(api_data, tenant_id)
       
       # Store in DynamoDB with TTL
       store.batch_write(representatives, ttl_hours=24)
       
       # Store in memory cache
       _memory_cache[f"{tenant_id}:{zip_code}"] = representatives
       
       return representatives
   ```

5. **Cache Invalidation Strategy**
   - Automatic: DynamoDB TTL expires records after 24 hours
   - Manual: Admin endpoint to force refresh (post-MVP)
   - Event-driven: Listen to data update events (future enhancement)

6. **Monitoring and Metrics**
   - CloudWatch metrics:
     - Cache hit rate (memory + DynamoDB)
     - API call count
     - Cache miss count
     - Average response latency
   - Set alarms for low cache hit rate (<80%)

7. **Error Handling**
   - If DynamoDB is unavailable, fall back to API directly
   - If API is unavailable, return stale cache data with warning
   - Implement circuit breaker pattern for API failures

### Testing Requirements
- Test cache hit scenarios (memory and DynamoDB)
- Test cache miss and population logic
- Test TTL expiration and refresh
- Test fallback scenarios when services unavailable
- Load test to verify cache improves performance

### Performance Goals
- Cache hit response time: <500ms
- Cache miss response time: <3 seconds
- Cache hit rate: >80% after warmup period

---

## Implementation Order

Execute these action items in the following sequence:

1. **Action Item 1** (Google Civic API Integration) - Foundation for data access
2. **Action Item 3** (DynamoDB Schema) - Required before caching can work
3. **Action Item 2** (OCD Division Parsing) - Enhances data categorization
4. **Action Item 5** (Caching Strategy) - Optimizes performance and costs

## Success Criteria

Implementation is complete when:
- ✅ Users can query representatives by zip code
- ✅ API responses return within 3 seconds (cache miss)
- ✅ API responses return within 500ms (cache hit)
- ✅ Data is categorized by government level (federal/state/county/local)
- ✅ Cache hit rate exceeds 80% under normal load
- ✅ Multi-tenant isolation functions correctly (state-level tenants)
- ✅ All error scenarios are handled gracefully
- ✅ Test coverage exceeds 80% for new code

## References

- **datamade/my-reps**: OCD division parsing patterns, Google Civic API integration
- **elisabethvirak/Know_Your_Congress**: Caching strategy, data refresh patterns
- **nrenner0211/elect.io**: React components, error handling patterns
- **Google Civic Information API**: https://developers.google.com/civic-information
- **OCD Division IDs**: https://github.com/opencivicdata/ocd-division-ids

## Notes

- All patterns should be adapted to serverless architecture (Lambda + DynamoDB)
- Security: Store API keys in AWS Systems Manager Parameter Store
- Cost optimization: Caching reduces API calls and AWS costs
- Monitoring: Use CloudWatch for observability and X-Ray for tracing
- Documentation: Update API docs as features are implemented
