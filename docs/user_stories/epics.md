# Represent App - Epics and User Stories

## Overview

This document outlines the epics and user stories for Represent App, organized by implementation phase. Each epic represents a major feature area or phase of development.

**Current Status**: Phase 1 Complete ✅ | Phase 2 In Progress 🔄

---

## MVP Epics

### Epic 1: Design Research Implementation (Phase 2) 🔄

**Goal**: Research and implement API integration using OpenStates.org or Washington state-specific APIs to build core MVP functionality for finding representatives by address or zip code.

**Status**: Current Phase

#### User Stories

**As a developer**, I want to research GitHub projects that leverage OpenStates.org API or Washington state-specific APIs so that I can identify the best approach for retrieving representative information by address and zip code.

**Acceptance Criteria**:
- Search GitHub for projects using OpenStates.org API
- Search GitHub for projects using Washington state-specific APIs (e.g., Washington State Legislature API)
- check this project and see how to integrate: https://github.com/openstates/people
- Identify ways to get OCD information to use for other APIs from Google's Civic Information API divisions endpoint
- Analyze at least 3 relevant projects for:
  - API authentication and key management patterns
  - Address/zip code to representative lookup implementation (can potentially use the google civic api for this step)
  - Data models and response parsing
  - Error handling and retry logic
  - Caching strategies
- Document findings in `.github/memory/patterns-discovered.md`
- Compare API capabilities (coverage, rate limits, data freshness)
- Recommend primary API for implementation with justification
- Create implementation plan based on research findings
- DO NOT suggest using the Google Civic Information API for representative lookups

**Technical Details**:
```
We will be turning down the Representatives API next year in April 2025. This API gives developers the ability to identify the elected representatives for a residential address or division. When we first launched the API 10 years ago, there was limited offering of political representation data in the civic information ecosystem. Today, there are alternate providers who are able to serve authoritative representation data directly to developers. 

Some key points:

Both representativeInfoByAddress and representativeInfoByDivision methods will be turned down next year in April 2025. 

Until the turndown date, the Representatives API will be functional and supported as usual.

After the turndown date, the Representatives API will not be available.

There is no impact on Elections or Divisions APIs, and they will continue to be supported. 

There are other providers who offer political representation data. The current Representatives API data comes from the Governance Project. 

To ease the transition to other providers of representation data, Google will launch a new method under the Divisions API which can be used to look up Open Civic Data Identifiers (OCD-IDs) for a given residential address. The OCD-ID can then be used to lookup representatives in other providers’ datasets. This launch is planned by Sep 2024 to give time for integration in your applications by the April 2025 turndown date. 

Please reach out to us if you have questions regarding this notice.


- Civic Information API team
```
---

**As a developer**, I want to design a multi-tenant DynamoDB schema so that representative data is efficiently stored and retrieved with state-level isolation.

**Acceptance Criteria**:
- DynamoDB table uses partition key `TENANT#{state_code}` and sort key `REP#{rep_id}`
- Global Secondary Index `LocationIndex` created for address and zip code lookups
- TTL attribute configured for automatic cache expiration (24 hours)
- Multi-tenant data isolation verified with tests
- RepresentativeStore class updated with new query methods
- CDK stack updated with new table configuration
- Query patterns tested and optimized

---

**As a developer**, I want to parse OCD Division IDs so that representatives can be categorized by government level.

**Acceptance Criteria**:
- `backend/src/utils/ocd_parser.py` utility module created
- Regex patterns implemented for federal, state, county, and local levels
- `government_level` field added to Representative model
- Categorization integrated with API response transformation
- API endpoint supports filtering by government level (`?level=federal`)
- Unit tests cover all OCD division ID patterns
- Documentation of OCD division ID format created

---

**As a developer**, I want to implement a multi-layer caching strategy so that API responses are fast and external API calls are minimized.

**Acceptance Criteria**:
- Lambda memory cache implemented using `functools.lru_cache`
- DynamoDB persistent cache layer implemented
- 24-hour TTL configured for cached representative data
- Cache hit/miss events logged to CloudWatch
- CloudWatch metrics track cache performance
- Cache hit rate exceeds 80% after warmup
- Performance targets met: <500ms cache hit, <3s cache miss
- Fallback logic handles service failures gracefully

---

**As a developer**, I want comprehensive testing and validation so that the API is reliable and performant.

**Acceptance Criteria**:
- Unit tests for all Phase 2 components
- Integration tests for complete address and zip code lookup flow
- Test coverage exceeds 80%
- Error handling scenarios tested (invalid zip, API failures)
- Performance tests validate caching effectiveness
- Multi-tenant isolation verified
- All tests pass in CI environment

---

**As a user**, I want to enter my address or zip code and receive a list of all my representatives so that I can easily find who represents me.

**Acceptance Criteria:**
- API endpoint `GET /api/representatives?address={address}` works
- API endpoint `GET /api/representatives?zip={zipcode}` works
- Address validation accepts standard US address formats
- Zip code validation accepts 5-digit and 9-digit formats
- Response includes all representatives for the address or zip code
- Representatives categorized by government level (federal, state, local)
- Response time under 3 seconds for cache miss
- Response time under 500ms for cache hit
- Error messages are clear and user-friendly

---

### Epic 2: Frontend Development (Phase 3)

**Goal**: Create a user-friendly React web interface for address and zip code lookup and representative display.

**Status**: Planned

#### User Stories

**As a user**, I want a clean web interface where I can enter my zip code so that I can easily look up my representatives.

**Acceptance Criteria**:
- React application initialized with Create React App or Vite
- Material UI (MUI) component library integrated
- Zip code input form with validation
- Submit button triggers API request
- Loading state displayed during API call
- Responsive design works on mobile, tablet, and desktop
- Application deployed and accessible via URL

---

**As a user**, I want to see my representatives organized by government level so that I understand who represents me at each level.

**Acceptance Criteria**:
- Representatives grouped into sections: Federal, State, Local
- Each representative displayed in a card with:
  - Name and photo (if available)
  - Office/title
  - Party affiliation
  - Contact information (email, phone, address)
  - Official website link
  - Social media links
- Cards have consistent styling using Material UI
- Information is easy to read and scan

---

**As a user**, I want the interface to be accessible so that I can use it regardless of disabilities.

**Acceptance Criteria**:
- WCAG AA compliance achieved
- Keyboard navigation works for all interactive elements
- Screen reader compatible with proper ARIA labels
- Sufficient color contrast for text and backgrounds
- Focus indicators visible on all focusable elements
- Form validation messages accessible

---

**As a developer**, I want to configure CORS on the API so that the frontend can make requests without cross-origin issues.

**Acceptance Criteria**:
- CORS headers configured in API Gateway
- Allowed origins include frontend domain
- Preflight requests handled correctly
- Frontend successfully makes API requests
- Error responses include CORS headers

---

### Epic 3: Documentation & Deployment (Phase 4)

**Goal**: Provide comprehensive documentation and production-ready deployment with monitoring.

**Status**: Planned

#### User Stories

**As a developer**, I want OpenAPI documentation so that I understand how to use the API endpoints.

**Acceptance Criteria**:
- OpenAPI 3.0 specification created for all endpoints
- Swagger UI available at `/api/docs` endpoint
- All request/response schemas documented
- Example requests and responses provided
- Authentication requirements documented (future)
- Error codes and messages documented

---

**As a developer**, I want CloudWatch alarms so that I'm notified when the API experiences issues.

**Acceptance Criteria**:
- Alarms created for:
  - API error rate exceeds 5%
  - API latency p95 exceeds 3 seconds
  - DynamoDB throttling events
  - Lambda errors or timeouts
- SNS topic created for alarm notifications
- Email notifications configured
- Alarm thresholds tuned based on production traffic
- Dashboard displays key metrics

---

**As a developer**, I want to deploy to production so that real users can access the application.

**Acceptance Criteria**:
- Production AWS environment created
- CDK stack deployed to production account
- Environment variables configured for production
- API Gateway custom domain configured
- SSL/TLS certificate provisioned
- DNS records updated
- Application tested with real addresses and zip codes
- Production deployment documented

---

**As a developer**, I want monitoring dashboards so that I can track system health and performance.

**Acceptance Criteria**:
- CloudWatch dashboard created with:
  - API request volume
  - Response time (p50, p95, p99)
  - Error rate by type
  - Cache hit rate
  - DynamoDB metrics (reads, writes, throttles)
  - Lambda metrics (invocations, duration, errors)
- X-Ray trace map shows request flow
- Tenant-specific metrics visible
- Dashboard accessible to operations team

---

## Post-MVP Epics

### Epic 4: Voting Records Tracking

**Goal**: Enable users to view and track how their representatives vote on legislation.

**Status**: Future

#### User Stories

**As a user**, I want to see how my representatives voted on specific bills so that I can hold them accountable.

**Acceptance Criteria**:
- ProPublica Congress API integrated
- Vote history displayed for each representative
- Bill information includes:
  - Bill number and title
  - Plain language summary
  - Representative's vote (Yes/No/Abstain)
  - Vote date
  - Bill outcome (Passed/Failed)
- Votes filterable by date range
- Votes filterable by topic/category

---

**As a user**, I want to track specific issues so that I'm notified when votes occur on topics I care about.

**Acceptance Criteria**:
- User can select issues to follow (healthcare, education, environment, etc.)
- Issue categories defined and maintained
- Bills automatically tagged with relevant issues
- User receives notifications when tracked representatives vote on followed issues
- Notification preferences configurable (email, SMS)

---

**As a user**, I want to see voting patterns over time so that I can understand my representative's record.

**Acceptance Criteria**:
- Voting history chart shows votes over time
- Visualization uses D3.js or similar library
- Party-line vs. independent votes highlighted
- Co-sponsorship information displayed
- Voting pattern analytics (% with party, key votes, etc.)

---

### Epic 5: Map-Based Visualization

**Goal**: Provide interactive map interface for exploring political boundaries and representatives.

**Status**: Future

#### User Stories

**As a user**, I want to see my representatives on an interactive map so that I can visualize political boundaries.

**Acceptance Criteria**:
- Interactive map interface implemented (Mapbox or Leaflet)
- Political boundary overlays for federal, state, and local levels
- User's location highlighted on map
- Congressional district boundaries displayed
- State legislative district boundaries displayed
- Map layers toggleable by government level

---

**As a user**, I want to zoom and pan the map to explore different areas so that I can see representatives for any location.

**Acceptance Criteria**:
- Map supports zoom and pan gestures
- Zoom level adjusts detail (more local as you zoom in)
- Click on map updates representative list
- Address search integrated with map
- Geocoding converts addresses to coordinates
- Boundaries load dynamically based on viewport

---

**As a user**, I want to click on a representative's district to see their information so that I can learn more about them.

**Acceptance Criteria**:
- District boundaries clickable
- Click opens representative detail panel
- Panel shows full contact information
- Link to full profile page
- Voting record accessible from map
- Multiple representatives in area listed

---

### Epic 6: User Authentication & Profiles

**Goal**: Enable user accounts for saving preferences and tracking issues.

**Status**: Future

#### User Stories

**As a user**, I want to create an account so that I can save my address and preferences.

**Acceptance Criteria**:
- User registration flow with email/password
- AWS Cognito user pool configured
- Email verification implemented
- Password reset functionality
- User profile page created
- Account deletion option available

---

**As a user**, I want to save multiple addresses so that I can quickly look up representatives for different locations.

**Acceptance Criteria**:
- User can save multiple addresses with labels (Home, Work, etc.)
- Saved addresses appear in dropdown
- Quick lookup from saved address
- Edit and delete saved addresses
- Primary address set as default
- Address validation on save

---

**As a user**, I want to customize my notification preferences so that I receive alerts that matter to me.

**Acceptance Criteria**:
- Notification settings page
- Email notification toggle
- SMS notification toggle (optional)
- Issue category preferences
- Notification frequency settings (immediate, daily digest, weekly)
- Opt-out of all notifications option

---

### Epic 7: Enhanced Data & Features

**Goal**: Aggregate data from multiple sources and provide advanced features.

**Status**: Future

#### User Stories

**As a user**, I want to see representative photos so that I can recognize them.

**Acceptance Criteria**:
- Integration with unitedstates/images GitHub repository
- Fallback to official website photos
- Photos cached in S3 for performance
- Default avatar for missing photos
- Photo attribution/credit displayed

---

**As a user**, I want to see state legislature information so that I understand state-level politics.

**Acceptance Criteria**:
- OpenStates API integrated
- State legislative information displayed
- State bill tracking available
- State representative voting records shown
- State committee membership displayed

---

**As a developer**, I want to migrate to GraphQL so that the frontend has flexible data querying.

**Acceptance Criteria**:
- Apollo Server implemented
- GraphQL schema defined for all data types
- Queries support flexible field selection
- Mutations for user actions (save address, track issue)
- REST endpoints maintained for backward compatibility
- GraphQL playground available for testing
- Frontend gradually migrated to GraphQL queries

---

**As a user**, I want to compare my representatives so that I can understand their differences.

**Acceptance Criteria**:
- Comparison view for 2-4 representatives
- Side-by-side display of:
  - Voting records on same bills
  - Party affiliation
  - Committee memberships
  - Contact information
- Highlight differences in voting patterns
- Export comparison as PDF

---

**As a user**, I want to search for representatives by name so that I can find specific officials.

**Acceptance Criteria**:
- Search box accepts representative names
- Autocomplete suggestions as user types
- Search works across all government levels
- Results include representative's jurisdiction
- Click result to view full profile
- Recent searches saved (if authenticated)

---

## Implementation Order

### Phase 1: Foundation ✅ (Complete)
- Python Lambda backend structure
- AWS CDK infrastructure
- Basic CRUD API endpoints
- DynamoDB persistence layer
- Unit testing framework

### Phase 2: Design Research Implementation 🔄 (Current)
1. Research and Select API (OpenStates.org or Washington State)
2. Implement Selected API Integration
3. DynamoDB Schema Design & Implementation
4. Government Level Categorization (OCD or equivalent)
5. Multi-Layer Caching Strategy
6. Comprehensive Testing & Validation

### Phase 3: Frontend Development (Next)
- React application setup
- Address and zip code input and validation
- Representative display components
- Responsive design
- CORS configuration

### Phase 4: Documentation & Deployment
- OpenAPI documentation
- CloudWatch alarms and monitoring
- Production deployment
- Performance optimization

### Phase 5: Post-MVP Features (Future)
- User authentication
- Voting records tracking
- Map-based visualization
- Advanced search and filtering
- Multiple data source integration

---

## Success Metrics by Epic

### Epic 1 (Phase 2) Success Criteria
- ✅ Research completed and API selected (OpenStates.org or Washington state API)
- ✅ API integration works for address and zip code lookups
- ✅ Multi-tenant DynamoDB schema performs well
- ✅ Representative categorization by government level works correctly
- ✅ Cache hit rate exceeds 80%
- ✅ Response times meet targets (<500ms hit, <3s miss)
- ✅ Test coverage exceeds 80%

### Epic 2 (Phase 3) Success Criteria
- ✅ Users can successfully look up representatives by address or zip code
- ✅ UI is responsive and accessible (WCAG AA)
- ✅ Frontend works on mobile, tablet, and desktop
- ✅ API integration from frontend works smoothly

### Epic 3 (Phase 4) Success Criteria
- ✅ OpenAPI documentation complete and accurate
- ✅ CloudWatch alarms notify team of issues
- ✅ Production deployment stable
- ✅ 99.9% uptime achieved

### Epic 4+ (Post-MVP) Success Criteria
- ✅ Users can view voting records
- ✅ Map visualization provides intuitive navigation
- ✅ User accounts support preferences and tracking
- ✅ Data from multiple sources aggregated correctly

---

## Notes

- **Epic 1** is the current focus and must be completed before Epic 2
- **Epics 2-3** constitute the complete MVP
- **Epics 4-7** are post-MVP enhancements to be prioritized based on user feedback
- Each epic should be broken down into smaller tasks/issues for sprint planning
- User stories should be estimated and prioritized within each epic
- Success criteria should be validated with stakeholders before implementation

---

**Document Version**: 1.0  
**Last Updated**: February 7, 2026  
**Status**: Living document - update as implementation progresses
