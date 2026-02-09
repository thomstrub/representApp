# Product Requirements Document (PRD) - Represent App

## 1. Overview

Represent App is a serverless application designed to bridge the gap between political infrastructure and constituents' day-to-day lives. The app provides citizens with the same knowledge and access to their political representatives that lobbyists have, making political information easily digestible and actionable.

**Problem Statement**: Citizens lack easy access to comprehensive information about their political representatives. Finding contact information, understanding jurisdictions, and tracking representatives' actions requires navigating multiple government websites and dense legal language.

**Solution**: A location-based web application that allows users to enter their address or zip code and instantly view all their representatives (federal, state, and local) with clear contact information, voting records, and plain-language summaries of political activities.

**Target Users**: 
- Everyday citizens who want to engage with their representatives
- Civic activists organizing community action
- Researchers tracking political data
- Anyone needing to contact their representatives quickly

**Key Differentiators**:
- Serverless, scalable architecture (AWS Lambda, API Gateway)
- Simple, fast MVP with direct API integration
- Integration with authoritative government APIs (OpenStates.org or Washington state)
- Plain language presentation of political information
- Extensible architecture for future caching and multi-tenancy (Phase 4)
- Future map-based visualization of political boundaries

---

## 2. MVP Scope

### Core Features

**Location-Based Representative Lookup**
- Accept address input via REST API endpoint: `GET /api/representatives?address={address}`
- Accept zip code input via REST API endpoint: `GET /api/representatives?zip={zipcode}`
- Validate address format and completeness
- Validate zip code format (5-digit or 9-digit)
- Return all representatives for that location (federal, state, local)
- Categorize representatives by government level (federal, state, county, local)
- Response time under 3 seconds for all queries

**Representative Information Display**
- Name, office/title, and party affiliation
- Contact information (email, phone, office address)
- Official website and social media links
- Representative photo (when available)
- Government level and jurisdiction
- Data freshness timestamp

**Government API Integration**
- Primary data source for representative lookups (API selected after research)
- Candidates: OpenStates.org API or Washington state-specific APIs
- Error handling for API failures (rate limits, timeouts, invalid responses)
- Retry logic with exponential backoff
- Graceful degradation when API is unavailable

**Government Level Categorization**
- Parse division identifiers from API responses (format depends on selected API)
- Categorize into government levels:
  - Federal (President, Senators, House Representatives)
  - State (Governor, State Senators, State Representatives)
  - Local (Mayor, City Council, etc.)
- Support filtering by government level via query parameter

**Performance**
- Direct API calls to government sources
- Response time target: <3 seconds for API calls
- Simple, fast implementation without persistent storage
- Extensible architecture for future optimization

**API Design**
- RESTful HTTP API v2 (API Gateway)
- Structured JSON responses
- Appropriate HTTP status codes (200, 400, 404, 500, 503)
- CORS support for frontend integration
- Error messages with user-friendly descriptions

**Infrastructure as Code**
- AWS CDK for all infrastructure
- Python 3.9 Lambda runtime
- AWS Lambda Powertools integration:
  - Structured logging with CloudWatch
  - Event parsing and validation (Pydantic)
  - X-Ray distributed tracing
- HTTP API Gateway v2
- CloudWatch log aggregation

**Testing Requirements**
- Unit tests for all core components (>80% coverage)
- Integration tests for API → Government API flow
- Mocked tests for external API calls
- Test coverage for error scenarios

**Documentation**
- API endpoint documentation
- Setup and deployment guides
- Architecture documentation
- Division ID format reference (based on selected API)

### Technical Implementation (Phase 2)

**Execute in this order** (see [design-research.md](design-research.md) for details):

1. **Research and Select Government API** (✅ Feature 001 - Complete)
   - Analyzed GitHub projects using OpenStates.org API
   - Analyzed Google Civic Information API
   - Documented integration patterns, data models, and best practices
   - Selected: Google Civic Information API (address → OCD-IDs) + OpenStates.org API v3 (representative data)
   - See: [specs/001-api-integration-research/](../specs/001-api-integration-research/)

2. **Implement Selected API Integration** (🔄 Feature 003 - Planning Complete)
   - 🔄 Register API keys and store in AWS Systems Manager Parameter Store
   - 🔄 Add API request handling in Lambda (Google Civic + OpenStates clients)
   - 🔄 Implement error handling (fail-fast pattern, no retry logic in MVP)
   - 🔄 Transform API responses to internal data model (6 entities defined)
   - See: [specs/003-address-lookup/](../specs/003-address-lookup/)

3. **Government Level Categorization** (🔄 Feature 003 - Planning Complete)
   - 🔄 Create categorization utility module using OCD-ID parsing
   - 🔄 Add government level categorization (federal, state, local) - 7 regex patterns defined
   - 🔄 Support filtering by government level (documented in API contract)

4. **Comprehensive Testing & Validation** (🔄 Feature 003 - Planning Complete)
   - 🔄 Unit tests for all new components (pytest + moto)
   - 🔄 Integration tests for API Gateway → Lambda → External APIs flow
   - 🔄 Validate response times (<3s end-to-end target)
   - 🔄 Test error handling scenarios (6 error codes defined)

---

## 3. Post-MVP Scope

### Extended Features

**DynamoDB Caching Layer (Phase 4)**
- Multi-layer caching strategy (Lambda memory + DynamoDB persistent cache)
- DynamoDB table with multi-tenant structure
- Primary key: `TENANT#{state_code}` (PK), `REP#{rep_id}` (SK)
- Global Secondary Index: `LocationIndex` for address and zip code lookups
- TTL configuration for automatic cache expiration (24-hour for representatives, 7-day for districts)
- Cache hit rate target: >80% after warmup
- Performance targets: <500ms response time for cache hits
- Lambda memory cache with `functools.lru_cache`
- Lambda tenant isolation mode for state-level tenant isolation
- Tenant ID = State code (CA, NY, TX, etc.)
- Tenant-aware logging and tracing

**Frontend Application**
- React-based single-page application (SPA)
- Material UI component library
- Address and zip code input form with validation
- Representative cards grouped by government level
- Responsive design for mobile, tablet, desktop
- Accessible UI (WCAG AA compliance)

**Voting Records Tracking**
- Integration with ProPublica Congress API
- Display how representatives voted on specific bills
- Filter votes by topic, date, or issue
- Bill summaries in plain language
- Vote history over time
- Voting pattern analytics

**OpenStates API Integration**
- State legislature details
- State-level bill tracking
- State representative voting records
- Enhanced state government data

**Representative Photos**
- Integration with unitedstates/images GitHub repository
- Fallback to official website photos
- Photo caching in S3

**Issue Tracking & Alerts**
- User accounts with saved preferences
- Follow specific issues (healthcare, education, environment, etc.)
- Email/SMS notifications for upcoming votes
- Alerts when representatives vote on tracked issues
- Issue categorization and tagging

**Map-Based Visualization**
- Interactive map interface
- Political boundary overlays (federal, state, local)
- Zoom-based navigation
- Highlight user's location and districts
- Click representatives on map to view details
- Multiple map layers for different government levels

**User Authentication & Profiles**
- AWS Cognito user pools
- User registration and login
- Profile management
- Saved addresses for quick lookup
- Notification preferences
- Issue tracking lists

**Advanced Search & Filtering**
- Search by representative name
- Filter by party affiliation
- Filter by office/title
- Filter by voting record
- Filter by issue stance
- Multiple simultaneous filters

**Administrative Features**
- Manual cache refresh endpoint
- Data quality monitoring
- API usage metrics
- Admin dashboard for system health

**GraphQL API** (See [graphQL_implementation.md](graphQL_implementation.md))
- Apollo Server implementation
- Flexible queries for frontend
- Mutations for user features
- Real-time subscriptions (optional)
- Migrate from REST incrementally

**Enhanced Data Aggregation**
- Merge data from multiple authoritative sources
- Cross-reference ProPublica, OpenStates, Google Civic
- Conflict resolution with prioritized sources
- Data quality validation

**Analytics & Insights**
- D3.js visualizations for voting patterns
- Representative comparison tools
- Demographic data integration
- Engagement metrics

---

## 4. Out of Scope

**Not Planned for Any Version**
- Direct messaging to representatives via the app
- User-generated content or comments
- Social network features or user-to-user interaction
- Campaign finance tracking (use existing specialized tools)
- Endorsements or political recommendations
- Voter registration services
- Election results or polling data
- Legislative text search or bill drafting tools
- Representative scheduling or appointment booking
- Fundraising or donation processing
- Mobile native apps (iOS/Android) - web-first approach
- International representatives (US-only for MVP)
- Historical representative data (pre-current term)
- Predictive analytics or AI recommendations

**Explicitly Deferred (Future Consideration)**
- White-label or multi-tenant SaaS offering
- API access for third-party developers
- Embedded widgets for other websites
- Browser extensions
- Offline mode or PWA functionality
- Multi-language support (English-only MVP)
- Custom data exports or reporting
- Integration with CRM systems
- Webhooks for external systems

---

## Success Metrics

### MVP Success Criteria (Phase 2)
1. ✅ Python 3.9 Lambda backend with AWS Lambda Powertools is deployed
2. ✅ CDK infrastructure with HTTP API Gateway v2 and Lambda is operational
3. � Government API selected and integrated
   - ✅ API research completed (feature 001)
   - ✅ API selection: Google Civic Information API + OpenStates.org API v3
   - ✅ Implementation planning complete (feature 003)
   - 🔲 Code implementation pending
4. 🔲 Users can find representatives by entering an address or zip code
   - ✅ API contract defined (OpenAPI 3.0.3 schema)
   - ✅ Data models specified (6 entities)
   - 🔲 Implementation pending
5. 🔲 Users can view contact information for all their representatives (name, office, party, contact info)
   - ✅ Response schema defined
   - 🔲 Implementation pending
6. 🔲 Representatives are categorized by government level (federal, state, local)
   - ✅ OCD-ID categorization patterns defined (7 regex patterns)
   - 🔲 Implementation pending
7. 🔲 API responses return within 3 seconds for government API calls
   - ✅ Performance target documented (<3s end-to-end)
   - 🔲 Implementation and validation pending
8. 🔲 System handles errors gracefully (invalid addresses/zip codes, API failures)
   - ✅ Error handling patterns defined (6 error codes, single error object format)
   - 🔲 Implementation pending
9. 🔲 All core features have test coverage above 80%
   - ✅ Testing strategy documented (pytest, moto, TDD workflow)
   - 🔲 Implementation pending
10. ✅ Application is deployed and accessible via AWS infrastructure

### Post-MVP Success Criteria (Phase 3+)
1. React frontend with Material UI components deployed
2. DynamoDB caching layer implemented (<500ms cache hits)
3. Multi-tenant architecture operational with Lambda tenant isolation mode
4. Users can interact with map-based visualizations
5. Users can view voting records for representatives
6. Users can track issues and receive alerts
7. System aggregates data from multiple sources (ProPublica, OpenStates)
8. User accounts support saved preferences and addresses
9. Frontend achieves WCAG AA accessibility compliance
10. Users report political information is easier to understand than traditional sources

### Key Performance Indicators (KPIs)
- API response time (p50, p95, p99) - MVP target: <3s
- Error rate by error type
- API availability (target: 99.9% uptime)
- User engagement (lookups per user session)
- Post-MVP: Cache hit rate percentage (target: >80%)
- Post-MVP: Data freshness (average age of cached data)

---

## Technical Requirements Summary

### Backend Stack
- **Runtime**: Python 3.9
- **Framework**: AWS Lambda with Powertools (structured logging, Pydantic validation, X-Ray tracing)
- **API**: API Gateway HTTP API v2
- **Government APIs**: OpenStates.org or Washington state API integration
- **Infrastructure**: AWS CDK (Python)
- **Testing**: pytest, moto, pytest-cov
- **Observability**: CloudWatch Logs, X-Ray tracing
- **Post-MVP**: DynamoDB with on-demand billing for caching

### Frontend Stack (Post-MVP)
- **Framework**: React
- **UI Library**: Material UI (MUI)
- **State Management**: React hooks (useState, useEffect)
- **HTTP Client**: Axios or fetch API
- **Testing**: Jest, React Testing Library
- **Deployment**: S3 + CloudFront

### External APIs
- **OpenStates.org API** (MVP candidate - primary data source)
- **Washington State Legislature API** (MVP candidate - primary data source)
- **ProPublica Congress API** (Post-MVP - voting records)
- **unitedstates/images GitHub** (Post-MVP - photos)

### AWS Services
- AWS Lambda (compute)
- API Gateway (HTTP API v2)
- Systems Manager Parameter Store (API keys)
- CloudWatch (logging and monitoring)
- X-Ray (tracing)
- Post-MVP: DynamoDB (caching)
- Post-MVP: Cognito (authentication)
- Post-MVP: S3 + CloudFront (frontend hosting)

---

## Implementation Phases

### Phase 1: Foundation (✅ Complete)
- Python Lambda backend structure with AWS Lambda Powertools
- AWS CDK infrastructure (Lambda + API Gateway)
- Basic health check endpoint
- Unit testing framework (pytest, moto, pytest-cov)
- Documentation structure

### Phase 2: Design Research Implementation (� In Progress - MVP)

**Feature 001: API Integration Research** (✅ Complete)
- Research and comparison of government APIs completed
- Selected Google Civic Information API + OpenStates.org API v3 combination
- Reference: [specs/001-api-integration-research/](../specs/001-api-integration-research/)

**Feature 003: Address Lookup API** (🔄 Planning Complete, Implementation Pending)
- User stories defined (P1-P4): Google Civic integration, OpenStates integration, API endpoint, secure keys
- Functional requirements specified (FR-001 to FR-017)
- Clarifications completed (deduplication, error format, retry logic, partial results)
- Constitution check: All 6 principles validated
- Phase 1 design complete:
  - Research documented (API selection, integration patterns)
  - Data models defined (6 entities: Representative, Division, Office, Request/Response, Error)
  - API contract finalized (OpenAPI 3.0.3 schema for GET /representatives)
  - Quickstart guide created (developer setup, TDD workflow, troubleshooting)
- **Next**: Phase 2 implementation (code, tests, infrastructure)
- Reference: [specs/003-address-lookup/](../specs/003-address-lookup/)

**Remaining Phase 2 Tasks**:
1. ✅ Research and select government API (OpenStates.org + Google Civic)
2. 🔄 Implement selected API integration (feature 003 planning complete)
3. 🔲 Government level categorization (federal, state, local) implementation
4. 🔲 Comprehensive testing (unit + integration)

Reference: [design-research.md](design-research.md)

### Phase 3: Frontend Development (🔲 Future)
- React application setup
- Address and zip code input component
- Representative display components
- Responsive design implementation
- CORS configuration

### Phase 4: Caching & Multi-Tenancy (🔲 Future)
- Design and implement DynamoDB schema for caching
- Implement multi-layer caching strategy (Lambda + DynamoDB)
- Add Lambda tenant isolation mode for multi-tenant caching
- Performance testing (<500ms cache hits, <3s cache misses)

### Phase 5: Documentation & Production Deployment (🔲 Future)
- OpenAPI/Swagger documentation
- CloudWatch alarms and monitoring
- Production deployment
- Real-world testing

### Phase 6: Post-MVP Features (🔲 Future)
- User authentication (Cognito)
- Voting records (ProPublica API)
- Issue tracking
- Map-based visualization
- Advanced search and filtering

### Phase 7: GraphQL Migration (🔲 Future - Optional)
- GraphQL schema design
- Apollo Server implementation
- Frontend migration to Apollo Client
- Incremental rollout

Reference: [graphQL_implementation.md](graphQL_implementation.md)

---

## Dependencies & Risks

### External Dependencies
- **Government APIs**: Critical dependency on OpenStates.org or Washington state API; must maintain valid API key and handle rate limits
- **AWS Services**: Reliance on Lambda and API Gateway availability
- **OCD Division IDs**: Dependent on division identifier format from selected API (OCD or equivalent)

### Technical Risks
1. **API Rate Limits**: Government API may impose rate limits
   - **Mitigation**: MVP - Error handling and retry logic; Phase 4 - Add caching to reduce API calls
2. **Cold Start Latency**: Lambda cold starts may affect 3s target
   - **Mitigation**: AWS Lambda Powertools optimization, consider provisioned concurrency if needed
3. **API Response Times**: Direct API calls may be slower than cached responses
   - **Mitigation**: MVP - Optimize Lambda performance; Phase 4 - Add multi-layer caching
4. **Location Complexity**: Some addresses and zip codes span multiple districts
   - **Mitigation**: Return all relevant representatives, clearly indicate jurisdictions
5. **Data Source Changes**: Selected API may change format or availability
   - **Mitigation**: Robust error handling, monitoring, ability to switch providers

### Business Risks
1. **API Availability**: Selected government API may become unavailable or change pricing
   - **Mitigation**: Monitor API status, have backup API options (OpenStates.org and Washington state), research alternative data sources
2. **Data Accuracy**: Representative info may change without notification
   - **Mitigation**: MVP - Real-time API calls ensure fresh data; Phase 4 - Short cache TTL with user feedback mechanism
3. **Scalability Costs**: High traffic may increase AWS costs and API usage
   - **Mitigation**: MVP - Monitor costs, optimize Lambda performance; Phase 4 - Add caching to reduce API calls

---

## Appendix

### Reference Documentation
- [Project Overview](project-overview.md)
- [Functional Requirements](functional-requirements.md)
- [Design Research & Implementation](design-research.md)
- [GraphQL Implementation Plan](graphQL_implementation.md)
- [Phase 1 Summary](phase1-summary.md)

### Related Resources
- OpenStates.org API: https://docs.openstates.org/api-v3/
- Washington State Legislature API: https://leg.wa.gov/
- OCD Division IDs: https://github.com/opencivicdata/ocd-division-ids
- ProPublica Congress API: https://projects.propublica.org/api-docs/congress-api/
- AWS Lambda Powertools: https://docs.powertools.aws.dev/lambda/python/
