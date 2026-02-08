# Phase 0: Research & Technology Decisions

**Feature**: 003-address-lookup  
**Date**: February 8, 2026  
**Status**: Complete (leveraging research from feature 001)

## Executive Summary

This feature builds on comprehensive API research completed in feature [001-api-integration-research](../001-api-integration-research/RESEARCH-COMPLETE.md). Key decisions have been finalized based on that analysis:

- **Primary API**: OpenStates.org API v3 (free tier, 5k req/day)
- **Address Resolution**: Google Civic Information API `/divisions` endpoint (OCD-ID mapping)
- **No Caching**: Direct API calls in MVP (caching deferred to post-MVP)
- **No Retry Logic**: Simplified error handling for MVP (retry logic deferred to post-MVP)

## API Selection Rationale

### Decision 1: OpenStates.org API v3 as Primary Data Source

**Chosen**: OpenStates.org API v3

**Rationale**:
- **Coverage**: 50 US states + federal Congress (meets MVP requirements)
- **Cost**: Free tier with 5,000 requests/day (MVP estimated ~250 req/day = 5% utilization)
- **Reliability**: 10+ years operational history, non-profit stewardship
- **Data Quality**: 1-2 week lag acceptable for MVP (not real-time but current)
- **Federal + State**: Provides both federal representatives AND state legislators

**Alternatives Considered**:
- **Google Civic API Representatives endpoint**: DEPRECATED April 2025 (all tests returned 404)
- **ProPublica Congress API**: Federal only (missing state legislators)
- **State-specific APIs**: Single-state coverage, inconsistent formats

**Source**: [001-api-integration-research/implementation-plan.md](../001-api-integration-research/implementation-plan.md#primary-api-recommendation-openstatesorg-api-v3-)

### Decision 2: Google Civic API for Address-to-OCD-ID Conversion

**Chosen**: Google Civic Information API `/divisions` endpoint

**Rationale**:
- **Only Remaining Google Civic Feature**: Representatives endpoint deprecated, but `/divisions` still functional
- **OCD-ID Standard**: Returns Open Civic Data identifiers compatible with OpenStates
- **High Rate Limit**: 25,000 requests/day (5x OpenStates limit)
- **Address Parsing**: Handles complex US address formats (street, city, state, ZIP)

**Flow**:
```
User Address → Google Civic /divisions → OCD-IDs → OpenStates people endpoint → Representatives
```

**Alternatives Considered**:
- **Direct state selection UI**: Simpler but limits UX flexibility (no address input)
- **Manual geocoding**: Complex, requires additional services (Mapbox, HERE)

**Source**: [001-api-integration-research/ocd-id-analysis.md](../001-api-integration-research/ocd-id-analysis.md)

### Decision 3: No Persistent Caching in MVP

**Chosen**: Direct API calls to Google Civic + OpenStates for every request

**Rationale**:
- **Simplicity**: Avoids DynamoDB schema design, TTL management, cache invalidation logic
- **Data Freshness**: Always returns current data from authoritative sources
- **MVP Velocity**: Faster implementation without caching layer
- **Performance Acceptable**: Combined API latency ~2-3 seconds fits <3s target

**Deferred to Post-MVP**:
- Lambda memory caching (`@lru_cache`)
- DynamoDB persistent cache layer
- Multi-layer caching strategy (research complete, implementation Phase 4)

**Source**: User clarification (scope decision: no caching in MVP)

### Decision 4: No Retry Logic in MVP

**Chosen**: Fail fast on API errors; return 503 Service Unavailable immediately

**Rationale**:
- **Simplicity**: Avoid exponential backoff implementation, rate limit state management
- **Clear Errors**: Users get immediate feedback instead of waiting for retries
- **MVP Focus**: Core functionality first; resilience enhancements in post-MVP

**Deferred to Post-MVP**:
- Exponential backoff retry with tenacity library
- Circuit breaker pattern for API failures
- Rate limit handling with backoff

**Source**: User clarification (retry logic deferred to post-MVP)

## Integration Patterns

### Pattern 1: API Key Management via AWS Parameter Store

**Implementation**:
```python
import boto3
from functools import lru_cache

@lru_cache(maxsize=1)
def get_api_key(parameter_name: str) -> str:
    """Retrieve API key from Parameter Store with memory caching"""
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']
```

**Security**:
- Keys stored as SecureString type (encrypted with KMS)
- IAM permissions: `ssm:GetParameter` on `/represent-app/*` paths
- Memory caching prevents repeated Parameter Store API calls within Lambda execution context
- Never commit keys to version control

**Parameter Paths**:
- `/represent-app/google-civic-api-key`
- `/represent-app/openstates-api-key`

**Source**: [001-api-integration-research/implementation-patterns.md#authentication-strategy](../001-api-integration-research/implementation-patterns.md#authentication-strategy)

### Pattern 2: Representative Deduplication by OpenStates ID

**Problem**: Multiple OCD-IDs may return the same representative (e.g., state-level AND congressional district-level queries)

**Solution**: Use OpenStates representative ID as uniqueness key

**Implementation**:
```python
seen_ids = set()
unique_reps = []
for rep in all_representatives:
    if rep['id'] not in seen_ids:
        seen_ids.add(rep['id'])
        unique_reps.append(rep)
```

**Rationale**:
- Prevents false duplicates (two people with identical names)
- Catches true duplicates even with name formatting variations ("John Smith" vs "John A. Smith")
- OpenStates IDs are stable, unique identifiers

**Source**: User clarification (deduplication strategy)

### Pattern 3: Partial Results with Warnings

**Problem**: OpenStates may not have data for all divisions returned by Google Civic (especially local/county officials)

**Solution**: Return partial results (HTTP 200) with warnings array indicating missing divisions

**Implementation**:
```json
{
  "representatives": [/* available reps */],
  "metadata": {
    "address": "123 Main St...",
    "government_levels": ["federal", "state"]
  },
  "warnings": [
    "No data available for: ocd-division/country:us/state:ca/county:alameda"
  ]
}
```

**Rationale**:
- User-friendly: Users get federal/state data even when local is missing
- Transparent: Clear indication of coverage gaps
- Aligns with constitution principle VI (accessible information)

**Source**: User clarification (partial failure handling)

### Pattern 4: Error Response Structure

**Format**: Single error object on failure (not array)

**Implementation**:
```json
{
  "error": {
    "code": "INVALID_ADDRESS",
    "message": "Unable to find political divisions for the provided address",
    "details": "The address '123 Fake St' could not be resolved by Google Civic API"
  }
}
```

**HTTP Status Codes**:
- 400: Bad request (missing/invalid address parameter)
- 404: Address not found (Google Civic couldn't resolve)
- 500: Internal error (uncaught exceptions)
- 503: Service unavailable (external API down or rate limited)

**Rationale**:
- Simple, consistent format for all errors
- Parseable by frontend for user-friendly display
- Returns first critical error (no multiple error accumulation)

**Source**: User clarification (error response format)

### Pattern 5: Photo URL Pass-Through

**Problem**: OpenStates returns photo URLs but they may be broken/inaccessible

**Solution**: Pass through photo URLs without validation

**Implementation**:
```python
rep_data = {
    "photo_url": openstates_response.get("image")  # No validation
}
```

**Rationale**:
- Avoids additional HTTP requests to verify photos
- Frontend can handle broken images gracefully (default avatar)
- Simplifies MVP implementation

**Source**: User clarification (photo URL handling)

## Best Practices from Research

### From openstates/people Repository Analysis

**Data Modeling**:
- Normalize phone numbers to XXX-XXX-XXXX format
- Use semicolon-separated strings for email arrays (e.g., "email1@example.com; email2@example.com")
- Include OCD-ID as `jurisdiction` field for representative context

**Temporal Data**: Not relevant for MVP (current officials only)

### From datamade/my-reps Repository Analysis

**OCD-ID Parsing**:
- Use regex patterns to extract government levels from OCD-ID structure:
  - Federal: `/country:us$` (US Senators, President)
  - State: `/state:[a-z]{2}$` (State-level)
  - Congressional: `/cd:\d+` (US House districts)
  - State Legislative: `/sldl:\d+|sldu:\d+` (State house/senate districts)
- Map extracted patterns to human-readable government level categories

**Source**: [001-api-integration-research/comparison-matrix.md](../001-api-integration-research/comparison-matrix.md)

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.9 | AWS Lambda compatibility |
| HTTP Client | requests | ^2.31.0 | External API calls (Google Civic, OpenStates) |
| AWS SDK | boto3 | ^1.26.0 | Parameter Store access |
| Validation | AWS Lambda Powertools | ^2.x | Request parsing, input validation |
| Logging | AWS Lambda Powertools Logger | ^2.x | Structured logging to CloudWatch |
| Tracing | AWS Lambda Powertools Tracer | ^2.x | X-Ray distributed tracing |
| Testing | pytest | ^7.4.0 | Unit test framework |
| Mocking | moto | ^4.2.0 | AWS service mocks (Parameter Store, Lambda) |
| Coverage | pytest-cov | ^4.1.0 | Test coverage reporting (>80% target) |

## Research Gaps: None

All unknowns from Technical Context have been resolved:
- ✅ API selection: OpenStates + Google Civic
- ✅ Authentication: AWS Parameter Store with IAM
- ✅ Caching strategy: None in MVP (deferred to post-MVP)
- ✅ Retry logic: None in MVP (deferred to post-MVP)
- ✅ Deduplication: OpenStates representative ID
- ✅ Error handling: Single error object with code/message/details
- ✅ Partial failures: Return available data with warnings array
- ✅ Photo URLs: Pass through without validation

## Next Phase

Proceed to **Phase 1: Design & Contracts** to define:
- Data models (Representative, Division, Office entities)
- API contract (OpenAPI schema for `/representatives` endpoint)
- Quickstart guide for local development and testing
