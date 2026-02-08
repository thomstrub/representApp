# Feature Specification: Address-Based Representative Lookup API

**Feature Branch**: `003-address-lookup`  
**Created**: February 8, 2026  
**Status**: Draft  
**Input**: Build backend API for address-based representative lookup using Google Civic API for OCD-IDs and OpenStates API for representative data

## Clarifications

### Session 2026-02-08

- Q: How should the system identify duplicate representatives when aggregating data from multiple political divisions? → A: Match by unique representative ID from OpenStates API (most reliable, prevents false positives)
- Q: What structure should error responses follow when API failures or validation errors occur? → A: Single error object with code, message, and optional details (simple, returns first error)
- Q: How should retry logic be applied when dealing with both Google Civic API and OpenStates API in a single request? → A: Move retry logic to post MVP
- Q: How should the system handle photo URLs returned by OpenStates API? → A: Pass through photo URLs without validation (fastest, frontend handles broken links)
- Q: How should the system respond when some political divisions have representative data available while others don't? → A: Return partial results with warnings about missing divisions (user-friendly, maximizes data)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Google Civic API Integration for OCD-ID Resolution (Priority: P1)

As a backend developer, I want to integrate with Google Civic Information API's `/divisions` endpoint so that I can convert user-provided street addresses into OCD (Open Civic Data) identifiers that can be used to query representative data from OpenStates API.

**Why this priority**: This is the foundation of address-based lookup. Without the ability to convert addresses to OCD-IDs, the entire feature cannot function. The Google Civic API is the authoritative source for mapping street addresses to political divisions, and this integration must work before any other component can be built.

**Independent Test**: Can be fully tested by calling Google Civic API with a test address (e.g., "1600 Pennsylvania Ave NW, Washington, DC 20500") and receiving back valid OCD-IDs for all political divisions (country, state, congressional district, etc.). Delivers the critical address-to-identifier mapping needed for the MVP.

**Acceptance Scenarios**:

1. **Given** a valid residential street address, **When** the system calls Google Civic API `/divisions` endpoint, **Then** the system receives OCD-IDs for all relevant political divisions (federal, state, county, city, congressional district, state legislative districts)
2. **Given** a valid address in a rural area, **When** the system queries Google Civic API, **Then** the system receives OCD-IDs including at minimum country, state, and congressional district levels
3. **Given** an address that spans multiple political divisions, **When** the system calls Google Civic API, **Then** the system receives all applicable OCD-IDs for overlapping jurisdictions
4. **Given** an invalid or malformed address, **When** the system queries Google Civic API, **Then** the system receives a clear error response that can be handled gracefully
5. **Given** Google Civic API rate limits are reached, **When** the system makes another request, **Then** the system receives a 429 error and returns an appropriate error response to the user

---

### User Story 2 - OpenStates API Integration for Representative Data (Priority: P2)

As a backend developer, I want to integrate with OpenStates.org API v3 so that I can retrieve comprehensive representative information (names, contact details, offices, party affiliations) for federal and state officials using OCD-IDs obtained from Google Civic API.

**Why this priority**: This is the second critical component - retrieving actual representative data. While it depends on having OCD-IDs (from P1), it can be independently tested using hardcoded OCD-IDs. OpenStates provides the most comprehensive coverage of federal and state officials across all 50 states.

**Independent Test**: Can be fully tested by providing known OCD-IDs (e.g., "ocd-division/country:us/state:ca") directly to OpenStates API and receiving back complete representative data including names, titles, party affiliations, contact information, and office details. Delivers the core representative information that users need.

**Acceptance Scenarios**:

1. **Given** a valid OCD-ID for a US state (e.g., "ocd-division/country:us/state:wa"), **When** the system queries OpenStates API, **Then** the system receives data for all state legislators (upper and lower chamber), governor, and federal representatives (US Senators and House members)
2. **Given** multiple OCD-IDs from a single address query, **When** the system queries OpenStates for each division, **Then** the system aggregates all unique representatives across all divisions without duplicates (using OpenStates representative ID as the uniqueness key)
3. **Given** an OCD-ID for a local/county division, **When** the system queries OpenStates API, **Then** the system handles the expected gap (OpenStates does not provide local officials) and documents this limitation clearly
4. **Given** OpenStates API rate limits are exceeded, **When** the system makes another request, **Then** the system returns a user-friendly error message indicating the service is temporarily unavailable
5. **Given** a valid OCD-ID, **When** the system receives response from OpenStates, **Then** the system transforms the data into a consistent internal model with all required fields (name, office, party, contact info, photo URL if available, government level)

---

### User Story 3 - API Gateway Endpoint for Address-Based Lookup (Priority: P3)

As an API consumer, I want to send a GET request to `/representatives?address={address}` and receive a JSON response containing all representatives for that address so that I can display representative information to end users.

**Why this priority**: This is the user-facing API endpoint that ties together the Google Civic and OpenStates integrations. While critical for the complete feature, it depends on both P1 and P2 working correctly. This story focuses on the API contract, input validation, error handling, and response formatting.

**Independent Test**: Can be fully tested by sending various address formats to the API endpoint via curl or Postman and validating the JSON response structure, status codes, error messages, and data completeness. Delivers a production-ready REST API that external clients can consume.

**Acceptance Scenarios**:

1. **Given** a user sends `GET /representatives?address=1600 Pennsylvania Ave NW, Washington DC 20500`, **When** the API processes the request, **Then** the system returns a 200 status code with JSON containing all federal and DC representatives (President, US Senators, US House member, DC Mayor, DC Council members if available)
2. **Given** a user sends a request without the `address` query parameter, **When** the API validates the input, **Then** the system returns a 400 Bad Request with clear error message "Missing required parameter: address"
3. **Given** a user sends a request with an invalid address that Google Civic API cannot resolve, **When** the API processes the request, **Then** the system returns a 404 Not Found with error message "Unable to find political divisions for the provided address"
4. **Given** either Google Civic API or OpenStates API is unavailable, **When** the API attempts to process a request, **Then** the system returns a 503 Service Unavailable with error message indicating which external service is down
5. **Given** a valid address request, **When** the API returns representative data, **Then** the response includes representatives categorized by government level (federal, state, local) with clear indication when local data is unavailable
6. **Given** multiple concurrent requests to the API, **When** the system processes them, **Then** each request completes within 3 seconds as per MVP performance target

---

### User Story 4 - Secure API Key Management with AWS Parameter Store (Priority: P4)

As a DevOps engineer, I want API keys for Google Civic and OpenStates to be stored securely in AWS Systems Manager Parameter Store and retrieved at Lambda runtime so that sensitive credentials are never committed to version control or exposed in logs.

**Why this priority**: Security is critical, but this story is independent of the core API functionality. It can be implemented in parallel with other stories or retrofitted after initial development. This ensures production-readiness and follows AWS security best practices.

**Independent Test**: Can be fully tested by storing test API keys in Parameter Store, deploying Lambda function with IAM permissions, and verifying that the Lambda can retrieve keys at runtime without hardcoding. Delivers secure credential management for production deployment.

**Acceptance Scenarios**:

1. **Given** Google Civic API key is stored at `/represent-app/google-civic-api-key` in Parameter Store, **When** the Lambda function initializes, **Then** the system retrieves the key using boto3 with proper IAM permissions
2. **Given** OpenStates API key is stored at `/represent-app/openstates-api-key` in Parameter Store, **When** the Lambda function initializes, **Then** the system retrieves the key and uses it in API request headers
3. **Given** API keys are stored as SecureString type in Parameter Store, **When** the Lambda retrieves them, **Then** the keys are automatically decrypted using AWS KMS
4. **Given** Lambda function initialization, **When** keys are retrieved from Parameter Store, **Then** the system caches the keys in memory for the duration of the Lambda execution context to avoid repeated API calls
5. **Given** Parameter Store is unavailable or keys are missing, **When** the Lambda attempts to initialize, **Then** the system fails fast with clear error message and does not proceed with API requests

---

### Edge Cases

- **What happens when an address spans multiple congressional districts?**  
  Return all applicable representatives from all overlapping jurisdictions. The Google Civic API may return multiple OCD-IDs for the same address in redistricting edge cases. The system should query OpenStates for each unique division and merge results, clearly labeling which district each representative serves.

- **How does the system handle addresses with no local government data?**  
  Return federal and state representatives with a clear note in the response: `"local_coverage": "limited"` or `"note": "Local officials not available for this address"`. Document that OpenStates does not provide county/city officials, which is an expected gap.

- **What happens when Google Civic API returns OCD-IDs but OpenStates has no data for those divisions?**  
  Log the missing divisions for monitoring, return the representatives that ARE available as partial results (HTTP 200), and include a warnings array like: `"warnings": ["No data available for: ocd-division/country:us/state:ca/county:alameda"]` to indicate which divisions had no data. This ensures users get federal/state representatives even when local data is missing.

- **How does the system handle extremely long addresses or special characters?**  
  Validate address input length (max 500 characters) and sanitize special characters before passing to Google Civic API. Return 400 Bad Request for addresses exceeding limits.

- **What happens when API rate limits are reached mid-request?**  
  Return 503 Service Unavailable with message: "Representative lookup service temporarily unavailable due to rate limits. Please try again later." Retry logic with exponential backoff is deferred to post-MVP.

- **How does the system handle concurrent Lambda cold starts?**  
  Each Lambda initialization independently retrieves API keys from Parameter Store using cached IAM credentials. Multiple cold starts may briefly increase Parameter Store API calls, but AWS SDK built-in retry and caching handles this gracefully.

- **What happens when an address is in a territory (Puerto Rico, Guam) vs. a state?**  
  Google Civic API will return appropriate OCD-IDs for territories. OpenStates coverage varies by territory - system should attempt lookup and document any gaps in the response. Return whatever data is available with coverage notes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an HTTP API endpoint `GET /representatives?address={address}` that accepts US street addresses as query parameters
- **FR-002**: System MUST validate that the `address` query parameter is present and non-empty; return HTTP 400 with error message if missing or invalid
- **FR-003**: System MUST integrate with Google Civic Information API `/divisions` endpoint to convert street addresses into OCD (Open Civic Data) identifiers
- **FR-004**: System MUST parse OCD-IDs returned by Google Civic API to identify all political divisions (federal, state, county, city, congressional, state legislative)
- **FR-005**: System MUST integrate with OpenStates.org API v3 to retrieve representative data using OCD-IDs as jurisdiction identifiers
- **FR-006**: System MUST aggregate representative data from OpenStates for all divisions returned by Google Civic, removing duplicate representatives (uniqueness determined by OpenStates representative ID); system MUST return partial results when some divisions have data and others don't, including warnings array to indicate missing divisions
- **FR-007**: System MUST return representatives categorized by government level: `federal` (President, US Senate, US House), `state` (Governor, State Senate, State House), and `local` (county/city officials when available)
- **FR-008**: System MUST clearly document in API responses when local/county representative data is unavailable (known OpenStates limitation)
- **FR-009**: System MUST retrieve API keys from AWS Systems Manager Parameter Store at Lambda initialization time, never from environment variables or hardcoded values
- **FR-010**: System MUST store Google Civic API key at `/represent-app/google-civic-api-key` and OpenStates API key at `/represent-app/openstates-api-key` in Parameter Store as SecureString type
- **FR-011**: System MUST cache API keys in Lambda memory for the duration of execution context to minimize Parameter Store API calls
- **FR-012**: System MUST implement error handling for API failures with appropriate HTTP status codes: 400 (bad input), 404 (address not found), 503 (external API unavailable), 500 (internal error); error responses MUST include a single error object with code, message, and optional details fields
- **FR-013**: System MUST respond to address lookup requests within 3 seconds (end-to-end from API Gateway to client) as per MVP performance target
- **FR-015**: System MUST log all requests, responses, errors, and API interactions using AWS Lambda Powertools structured logging for CloudWatch
- **FR-016**: System MUST include X-Ray tracing for distributed request tracking across Lambda, API Gateway, and external API calls
- **FR-017**: System MUST return JSON responses with consistent structure including `representatives` array on success, or `error` object (with code, message, details fields) on failure; `metadata` and `warnings` arrays included when applicable
- **FR-018**: System MUST handle CORS headers to allow frontend consumption from any origin (configurable in API Gateway)

### Key Entities

- **Representative**: An elected official holding public office. Attributes include full name, office/title, party affiliation, contact information (email, phone, office address), official website, social media links, photo URL (if provided by OpenStates, passed through without validation), government level (federal/state/local), and jurisdiction (which district they represent).

- **Division**: A political or administrative boundary defined by an OCD-ID (Open Civic Data identifier). Represents hierarchical jurisdictions like country, state, county, city, congressional district, state legislative district. Each division may have multiple representatives (e.g., a state has 2 US Senators).

- **Office**: A position of elected authority within government. Examples include "President of the United States", "US Senator", "State Senator - District 12", "Governor". Each office is associated with a government level and jurisdiction.

- **APIKey**: Secure credential stored in AWS Parameter Store. Used to authenticate requests to external APIs (Google Civic, OpenStates). Retrieved at Lambda initialization and cached in memory for performance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully look up all federal and state representatives by providing a valid US residential street address
- **SC-002**: The system returns representative data within 3 seconds for 95% of requests (p95 latency target)
- **SC-003**: The system correctly handles and categorizes representatives at federal and state government levels for all 50 US states
- **SC-004**: The system provides clear, user-friendly error messages for invalid addresses with at least 90% of error cases having actionable guidance
- **SC-005**: API error rate is below 5% for valid address lookups (excluding invalid user input)
- **SC-006**: The system includes coverage documentation in responses, clearly indicating when local/county data is unavailable (expected gap)
- **SC-007**: No API keys or secrets are committed to version control; all credentials are retrieved from AWS Parameter Store at runtime
- **SC-008**: System successfully handles at least 100 concurrent address lookup requests without degradation (Lambda concurrency testing)
- **SC-009**: All critical code paths have comprehensive logging and distributed tracing enabled for debugging and monitoring
- **SC-010**: The API returns consistent JSON response structure across all success and error scenarios, enabling reliable frontend integration

## Dependencies & Assumptions

### External Dependencies

- **Google Civic Information API**: Critical dependency for address-to-OCD-ID conversion. API must remain available and `/divisions` endpoint must continue to function (note: `/representatives` endpoint was deprecated in April 2025).
- **OpenStates.org API v3**: Critical dependency for representative data. Requires valid API key with at least 5,000 requests/day (free tier).
- **AWS Systems Manager Parameter Store**: Required for secure API key storage and retrieval.
- **AWS Lambda Powertools**: Used for structured logging, event parsing, and X-Ray tracing.

### Assumptions

- **Address Format**: Users will provide standard US mailing addresses (street number, street name, city, state, ZIP). Non-standard formats (PO Boxes, military addresses) will be handled on a best-effort basis by Google Civic API.
- **Coverage Expectations**: Users understand that local/county official data may not be available for all addresses. The system will clearly document this limitation.
- **Performance**: Google Civic API and OpenStates API response times are typically under 1-2 seconds each, allowing the combined 3-second target to be achievable.
- **Data Freshness**: Representative data from OpenStates may have a 1-2 week lag for newly elected or appointed officials. This is acceptable for MVP as documented in the research phase.
- **API Rate Limits**: MVP usage will stay within free tier limits (Google Civic: 25,000 req/day, OpenStates: 5,000 req/day). No budget allocated for paid tiers in this phase.
- **State Focus**: Initial testing and validation will prioritize the 50 US states. Territories (Puerto Rico, Guam, etc.) are supported on a best-effort basis pending OpenStates coverage.

## Out of Scope

The following are explicitly NOT included in this feature:

- **Frontend UI**: No React components, forms, or user interface. This is backend API only. Frontend integration is a separate feature.
- **DynamoDB Caching**: No persistent caching layer. All requests make direct API calls to Google Civic and OpenStates. Caching is deferred to Phase 4 per PRD.
- **Address Autocomplete**: No integration with Google Places API or address validation services. Users must provide complete addresses.
- **Voting Records**: No integration with ProPublica Congress API for voting history. This is a post-MVP enhancement.
- **Representative Photos**: No photo retrieval or storage. Photo URLs from OpenStates will be included in responses if available, but no additional photo sourcing (e.g., unitedstates/images repo).
- **User Authentication**: No user accounts, login, or saved addresses. API is open access (CORS-enabled).
- **Retry Logic**: No automatic retry with exponential backoff for API failures. Failed requests return errors immediately. Deferred to post-MVP.
- **Rate Limiting**: No application-level rate limiting or throttling. Relying on AWS API Gateway default limits.
- **Analytics**: No user behavior tracking or analytics beyond CloudWatch metrics. No custom dashboards or reports in this feature.
- **Multi-Language Support**: English-only API responses and error messages.
- **Historical Data**: No retrieval of past representatives or term history. Current officials only.
- **District Mapping**: No geographic visualization or boundary files. Text-based data only.

## Expected Data Flow *(informational)*

At a high level, the address lookup follows this flow:

1. User provides a residential street address
2. System converts address to political division identifiers using authoritative government data source
3. System retrieves representative information for each political division
4. System aggregates and categorizes representatives by government level (federal, state, local)
5. System returns structured data to user with coverage notes

## Response Structure *(informational)*

The API should return data structured to support:

- Array of representatives with name, office title, party, contact information, and government level
- Metadata about the request (address queried, government levels included)
- Warnings or notes about data coverage gaps (e.g., local officials unavailable)
