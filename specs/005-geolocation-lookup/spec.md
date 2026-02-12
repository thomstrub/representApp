# Feature Specification: Geolocation-Based Representative Lookup

**Feature Branch**: `005-geolocation-lookup`  
**Created**: February 10, 2026  
**Status**: Draft  
**Input**: User description: "I want to change the API endpoints this service uses to get representatives. I want to use the endpoint described in #file:openstates_endpoint_info.md and the google geolocation API - you can use - https://github.com/googlemaps/google-maps-services-python - these should be used instead of the current queries. We want to take an address, query geolocation api, and use the latitude and longitude coordinates to query openstates."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Replace Google Civic with Google Geolocation API (Priority: P1)

When users enter a street address, the system converts it to geographic coordinates (latitude/longitude) using the Google Maps Geocoding API instead of the Google Civic Information API. This change provides more reliable address resolution since the Google Civic API representatives endpoint was deprecated in April 2025.

**Why this priority**: This is the foundation for the entire feature - without accurate address-to-coordinates conversion, no representative lookup can occur. This is the first step in the new data flow.

**Independent Test**: Can be fully tested by entering a known address and verifying that valid latitude/longitude coordinates are returned. Delivers independent value by proving the geocoding service works correctly.

**Acceptance Scenarios**:

1. **Given** a valid US street address, **When** submitted to the geocoding service, **Then** the service returns valid latitude and longitude coordinates for that address
2. **Given** an ambiguous address (e.g., "123 Main St"), **When** submitted, **Then** the service returns the most relevant match based on Google's confidence scoring (first result from geocoding API)
3. **Given** an invalid or malformed address, **When** submitted, **Then** the service returns a clear error message indicating the address could not be geocoded
4. **Given** a geocoding API error (timeout, rate limit), **When** the error occurs, **Then** the service returns appropriate error code and user-friendly message

---

### User Story 2 - Replace OCD-ID Lookup with OpenStates Geo Endpoint (Priority: P2)

After obtaining geographic coordinates, the system queries the OpenStates geo endpoint (`/people.geo`) to retrieve representatives based on latitude and longitude. This replaces the previous two-step process of getting OCD-IDs from Google Civic and then querying OpenStates by jurisdiction.

**Why this priority**: Once geocoding works (P1), this is the critical next step to actually retrieve representative data. The geo endpoint is more direct than the previous OCD-ID approach.

**Independent Test**: Can be fully tested using known lat/lng coordinates (e.g., Seattle: 47.6105, -122.3115) and verifying that the correct representatives are returned. Delivers value by proving the representative lookup works.

**Acceptance Scenarios**:

1. **Given** valid latitude and longitude coordinates for a US location, **When** queried against OpenStates geo endpoint, **Then** the service returns all representatives (federal, state, local) for that location
2. **Given** coordinates outside the US or in a location without representative data, **When** queried, **Then** the service returns appropriate "no data" response
3. **Given** OpenStates API rate limit or timeout, **When** the error occurs, **Then** the service returns appropriate error code and retry guidance
4. **Given** coordinates for a location with multiple overlapping jurisdictions, **When** queried, **Then** the service returns all applicable representatives grouped by government level

---

### User Story 3 - End-to-End Address to Representatives Flow (Priority: P3)

Users enter a street address and receive a complete list of their representatives, with the system internally handling the two-step process: address → coordinates → representatives. This story integrates the previous two stories into a seamless user experience.

**Why this priority**: This represents the complete feature working together. While critical for production use, it depends on P1 and P2 being complete first.

**Independent Test**: Can be fully tested by entering various addresses (urban, rural, edge cases) and verifying correct representatives are returned. Deliverable is a working end-to-end lookup.

**Acceptance Scenarios**:

1. **Given** a user enters a complete street address, **When** submitted, **Then** the system returns all representatives (federal, state, local) for that address within 3 seconds
2. **Given** a user enters a zip code only, **When** submitted, **Then** the system geocodes the zip code centroid and returns representatives for that general area
3. **Given** the geocoding step succeeds but OpenStates returns no data, **When** this occurs, **Then** the user receives a message indicating no representative data is available for their location
4. **Given** any step in the pipeline fails, **When** the error occurs, **Then** the user receives a clear, actionable error message without exposing technical implementation details

---

### User Story 4 - Remove Google Civic API Dependencies (Priority: P4)

Clean up all code, configurations, and infrastructure related to the deprecated Google Civic Information API. This includes removing the `GoogleCivicClient` service, related tests, and API key management from Parameter Store.

**Why this priority**: Cleanup work that should happen after the new system is proven to work. Important for code maintenance but not critical for feature functionality.

**Independent Test**: Can be verified by searching the codebase for Google Civic references and confirming none remain except in historical documentation. Delivers value by reducing technical debt.

**Acceptance Scenarios**:

1. **Given** the new geolocation flow is fully tested and working, **When** Google Civic code is removed, **Then** all existing tests pass and no functionality is broken
2. **Given** Google Civic API keys in Parameter Store, **When** cleanup is performed, **Then** these parameters are removed or marked as deprecated
3. **Given** documentation referencing Google Civic API, **When** updated, **Then** references are replaced with geolocation approach or marked as historical
4. **Given** Lambda function IAM permissions, **When** audited, **Then** unnecessary Google Civic API permissions are removed

---

### Edge Cases

- What happens when address is valid but geocoding returns multiple possible matches (e.g., "123 Main Street" exists in multiple cities)? System automatically uses the first (most confident) result from Google's geocoding response
- How does system handle addresses on jurisdiction boundaries where representatives differ by a few feet?
- What happens when OpenStates geo endpoint returns partial data (e.g., federal reps but no state reps)?
- How does system handle addresses in US territories (Puerto Rico, Guam) where representative structures differ?
- What happens if Google Maps API changes its response format or deprecates the geocoding endpoint?
- How does system handle very old addresses or buildings that have been renumbered?
- What happens with rural addresses that use general delivery or PO Box instead of street addresses?
- How does system handle coordinate precision - does rounding affect which jurisdiction is detected?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept US street addresses as input and convert them to WGS84 latitude/longitude coordinates using Google Maps Geocoding API
- **FR-002**: System MUST use the `googlemaps` Python library (https://github.com/googlemaps/google-maps-services-python) for all Google Maps API interactions
- **FR-003**: System MUST query the OpenStates `/people.geo` endpoint using latitude and longitude coordinates to retrieve representative data
- **FR-004**: System MUST preserve existing error handling patterns (ApiException, ErrorCode) when integrating new API clients
- **FR-005**: System MUST maintain Lambda Powertools logging and X-Ray tracing throughout the new geolocation flow
- **FR-006**: System MUST validate addresses before attempting geocoding to prevent unnecessary API calls
- **FR-007**: System MUST handle geocoding API errors (invalid address, rate limits, timeouts) with appropriate error codes and user-friendly messages (fail immediately, no automatic retries)
- **FR-008**: System MUST handle OpenStates geo endpoint errors (no data, rate limits, timeouts) with appropriate error codes and retry guidance (fail immediately, no automatic retries)
- **FR-009**: System MUST transform OpenStates geo response format to match the existing `Representative` data model used by the frontend
- **FR-010**: System MUST return representatives grouped by government level (federal, state, local) as expected by the frontend contract
- **FR-011**: System MUST maintain response time under 3 seconds for the complete address-to-representatives flow
- **FR-012**: System MUST store Google Maps API key securely in AWS Systems Manager Parameter Store at path `/represent-app/google-maps-api-key`
- **FR-013**: System MUST update Lambda IAM role to include permissions for retrieving the Google Maps API key from Parameter Store
- **FR-014**: System MUST remove all references to `GoogleCivicClient` from the codebase after the new flow is verified working
- **FR-015**: System MUST update all integration tests to use the new geolocation-based flow instead of Google Civic API mocks
- **FR-016**: System MUST preserve backwards compatibility with the frontend API contract (same endpoint, same response structure)
- **FR-017**: System MUST handle addresses with apartment/unit numbers by geocoding the primary address location
- **FR-018**: System MUST return metadata including the geocoded address and coordinates for troubleshooting purposes
- **FR-019**: System MUST implement timeout limits for both geocoding (5 seconds) and representative lookup (10 seconds) API calls
- **FR-020**: System MUST log all API interactions with timing metrics for monitoring and debugging
- **FR-021**: System MUST make direct API calls without caching layer (maintain current implementation approach)
- **FR-022**: System MUST use the first (most confident) geocoding result when Google Maps API returns multiple matches for an ambiguous address

### Key Entities *(include if feature involves data)*

- **Geocoding Request**: User-provided address string, optional formatting parameters, timeout configuration
- **Geocoding Response**: Latitude and longitude coordinates (WGS84), formatted address, place ID, address components (street, city, state, zip), location type (ROOFTOP, RANGE_INTERPOLATED, GEOMETRIC_CENTER)
- **OpenStates Geo Request**: Latitude and longitude coordinates, API key, optional filters (government level, district type)
- **OpenStates Geo Response**: List of people/representatives, each with: OCD person ID, name, party affiliation, current role (title, organization classification, district, division ID), jurisdiction (ID, name, classification), contact information (email, phone, image URL), biographical data (given name, family name, birth date)
- **Representative Model (existing)**: Internal representation used by frontend - must map from OpenStates response fields to maintain compatibility
- **API Client Configuration**: Base URLs, API keys, timeout values, retry policies, rate limit handling

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System successfully geocodes 95% of valid US street addresses to accurate coordinates (verified against known address dataset)
- **SC-002**: Representative lookup requests complete within 3 seconds end-to-end for 90% of requests
- **SC-003**: System maintains 99.5% uptime excluding external API outages (Google Maps and OpenStates)
- **SC-004**: Zero production errors related to Google Civic API after migration is complete
- **SC-005**: All existing frontend address lookup functionality works without modification after backend migration
- **SC-006**: System handles geocoding errors gracefully with 100% of invalid addresses returning appropriate error messages (not 500 errors)
- **SC-007**: Test coverage remains at or above current levels (100% for unit tests) after migration
- **SC-008**: Representative data accuracy matches or exceeds current implementation (verified by comparing results for 100 sample addresses)
- **SC-009**: API key rotation (Google Maps) can be performed without code changes (key stored in Parameter Store only)
- **SC-010**: System successfully retrieves representatives for addresses in all 50 US states and DC (verified by test suite)

## Clarifications

### Session 2026-02-10

- Q: What caching strategy should be used for the new geolocation flow (DynamoDB, in-memory, or none)? → A: No caching (maintain current direct API call approach)
- Q: When the system hits API rate limits (Google Maps or OpenStates), should it retry automatically or fail immediately? → A: Fail immediately with clear error message and retry-after guidance (no automatic retries)
- Q: When geocoding returns multiple possible matches for an ambiguous address, how should the system handle this? → A: Return the single most relevant result automatically based on Google's confidence scoring (first result)
