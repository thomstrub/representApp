# Tasks: Address-Based Representative Lookup API

**Feature**: 003-address-lookup  
**Input**: Design documents from `/specs/003-address-lookup/`  
**Prerequisites**: ✅ plan.md, ✅ spec.md, ✅ research.md, ✅ data-model.md, ✅ contracts/openapi.yaml

**Tests**: ✅ Tests ARE included (TDD approach specified in project guidelines)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `backend/tests/`, `infrastructure/stacks/`
- Paths use absolute references from repository root
- All code follows TDD: Write failing tests FIRST, then implement

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [ ] T001 [P] Add requests library to backend/requirements.txt for HTTP client
- [ ] T002 [P] Add pytest-mock to backend/requirements.txt for mocking external APIs
- [ ] T003 Verify all dependencies install successfully with pip install -r backend/requirements.txt

**Checkpoint**: Dependencies ready - foundational work can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create base error handling framework in backend/src/utils/errors.py with ErrorCode enum and ApiException class
- [ ] T005 Add AWS Parameter Store parameter placeholders to infrastructure/stacks/backend_stack.py (IDs only, no values)
- [ ] T006 [P] Create ErrorResponse model in backend/src/models/base.py with code, message, details fields
- [ ] T007 [P] Create Division model in backend/src/models/base.py with ocd_id, name, government_level, has_data fields
- [ ] T008 [P] Create Representative model in backend/src/models/base.py with 11 fields per data-model.md
- [ ] T009 [P] Create Office model in backend/src/models/base.py with title, government_level, division fields

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Google Civic API Integration (Priority: P1) 🎯 MVP

**Goal**: Convert user-provided street addresses into OCD identifiers using Google Civic Information API

**Independent Test**: Can call Google Civic API with test address (e.g., "1600 Pennsylvania Ave NW, Washington, DC 20500") and receive valid OCD-IDs for all political divisions

### Tests for User Story 1

> **TDD: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Unit test for Parameter Store key retrieval in backend/tests/unit/test_parameter_store.py
- [ ] T011 [P] [US1] Unit test for Google Civic client initialization in backend/tests/unit/test_google_civic.py
- [ ] T012 [P] [US1] Unit test for Google Civic address lookup success case in backend/tests/unit/test_google_civic.py
- [ ] T013 [P] [US1] Unit test for Google Civic invalid address (404) in backend/tests/unit/test_google_civic.py
- [ ] T014 [P] [US1] Unit test for Google Civic rate limit (429) in backend/tests/unit/test_google_civic.py
- [ ] T015 [US1] Integration test for Google Civic full flow in backend/tests/integration/test_google_civic_integration.py

### Implementation for User Story 1

- [ ] T016 [US1] Create Parameter Store service in backend/src/services/parameter_store.py with get_api_key() and @lru_cache
- [ ] T017 [US1] Create GoogleCivicClient class in backend/src/services/google_civic.py with __init__(api_key) method
- [ ] T018 [US1] Implement lookup_divisions(address) method in backend/src/services/google_civic.py
- [ ] T019 [US1] Add error handling for 404 (address not found) in backend/src/services/google_civic.py
- [ ] T020 [US1] Add error handling for 429 (rate limit exceeded) in backend/src/services/google_civic.py
- [ ] T021 [US1] Add logging with Lambda Powertools in backend/src/services/google_civic.py
- [ ] T022 [US1] Add X-Ray tracing annotations for Google Civic API calls in backend/src/services/google_civic.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (can convert addresses to OCD-IDs)

---

## Phase 4: User Story 2 - OpenStates API Integration (Priority: P2)

**Goal**: Retrieve comprehensive representative information (names, contact details, offices, party affiliations) for federal and state officials using OCD-IDs

**Independent Test**: Can call OpenStates API with known OCD-ID (e.g., "ocd-division/country:us/state:ca") and receive complete representative data with all required fields

### Tests for User Story 2

> **TDD: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US2] Unit test for OpenStates client initialization in backend/tests/unit/test_openstates.py
- [ ] T024 [P] [US2] Unit test for OpenStates get_representatives_by_division() success case in backend/tests/unit/test_openstates.py
- [ ] T025 [P] [US2] Unit test for OpenStates empty results (no data for division) in backend/tests/unit/test_openstates.py
- [ ] T026 [P] [US2] Unit test for OpenStates rate limit (429) in backend/tests/unit/test_openstates.py
- [ ] T027 [P] [US2] Unit test for OCD-ID government level parsing (federal) in backend/tests/unit/test_ocd_parser.py
- [ ] T028 [P] [US2] Unit test for OCD-ID government level parsing (state) in backend/tests/unit/test_ocd_parser.py
- [ ] T029 [P] [US2] Unit test for OCD-ID government level parsing (local) in backend/tests/unit/test_ocd_parser.py
- [ ] T030 [P] [US2] Unit test for deduplication by OpenStates ID in backend/tests/unit/test_openstates.py
- [ ] T031 [US2] Integration test for OpenStates full flow in backend/tests/integration/test_openstates_integration.py

### Implementation for User Story 2

- [ ] T032 [US2] Create OpenStatesClient class in backend/src/services/openstates.py with __init__(api_key) method
- [ ] T033 [US2] Implement get_representatives_by_division(ocd_id) method in backend/src/services/openstates.py
- [ ] T034 [US2] Add data transformation from OpenStates response to Representative model in backend/src/services/openstates.py
- [ ] T035 [US2] Implement deduplication logic by representative ID in backend/src/services/openstates.py
- [ ] T036 [US2] Add error handling for empty results (no data for division) in backend/src/services/openstates.py
- [ ] T037 [US2] Add error handling for rate limits (429) in backend/src/services/openstates.py
- [ ] T038 [US2] Create OCD-ID parser utility in backend/src/utils/ocd_parser.py with parse_government_level(ocd_id) function
- [ ] T039 [US2] Implement 7 regex patterns for government level categorization in backend/src/utils/ocd_parser.py
- [ ] T040 [US2] Add logging with Lambda Powertools in backend/src/services/openstates.py
- [ ] T041 [US2] Add X-Ray tracing annotations for OpenStates API calls in backend/src/services/openstates.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (can get OCD-IDs and retrieve representatives)

---

## Phase 5: User Story 3 - API Gateway Endpoint (Priority: P3)

**Goal**: Expose REST API endpoint that accepts addresses and returns JSON with all representatives, properly categorized by government level

**Independent Test**: Can send GET /representatives?address=1600+Pennsylvania+Ave+NW,+Washington+DC+20500 via curl and receive 200 status with JSON containing federal and state representatives

### Tests for User Story 3

> **TDD: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T042 [P] [US3] Unit test for address validation (valid address) in backend/tests/unit/test_validators.py
- [ ] T043 [P] [US3] Unit test for address validation (missing address) in backend/tests/unit/test_validators.py
- [ ] T044 [P] [US3] Unit test for address validation (empty address) in backend/tests/unit/test_validators.py
- [ ] T045 [P] [US3] Unit test for address validation (exceeds 500 chars) in backend/tests/unit/test_validators.py
- [ ] T046 [P] [US3] Unit test for API handler success case (200) in backend/tests/unit/test_api_handler.py
- [ ] T047 [P] [US3] Unit test for API handler missing parameter (400) in backend/tests/unit/test_api_handler.py
- [ ] T048 [P] [US3] Unit test for API handler address not found (404) in backend/tests/unit/test_api_handler.py
- [ ] T049 [P] [US3] Unit test for API handler external service error (503) in backend/tests/unit/test_api_handler.py
- [ ] T050 [P] [US3] Unit test for API handler internal error (500) in backend/tests/unit/test_api_handler.py
- [ ] T051 [P] [US3] Unit test for partial results with warnings in backend/tests/unit/test_api_handler.py
- [ ] T052 [US3] Integration test for full address lookup flow (API Gateway → Lambda → External APIs) in backend/tests/integration/test_address_lookup.py

### Implementation for User Story 3

- [ ] T053 [US3] Create AddressLookupRequest model in backend/src/models/base.py with address field and 500 char validation
- [ ] T054 [US3] Create AddressLookupResponse model in backend/src/models/base.py with representatives, metadata, warnings fields
- [ ] T055 [US3] Create address validator in backend/src/utils/validators.py with validate_address(address) function
- [ ] T056 [US3] Add /representatives route handler to backend/src/handlers/api.py
- [ ] T057 [US3] Implement address parameter validation in backend/src/handlers/api.py (return 400 if missing/invalid)
- [ ] T058 [US3] Integrate GoogleCivicClient in backend/src/handlers/api.py to get OCD-IDs
- [ ] T059 [US3] Integrate OpenStatesClient in backend/src/handlers/api.py to get representatives for each division
- [ ] T060 [US3] Implement representative aggregation and deduplication logic in backend/src/handlers/api.py
- [ ] T061 [US3] Implement government level categorization (federal, state, local) in backend/src/handlers/api.py
- [ ] T062 [US3] Add partial results logic with warnings array for missing divisions in backend/src/handlers/api.py
- [ ] T063 [US3] Implement error response formatting with single error object in backend/src/handlers/api.py
- [ ] T064 [US3] Add HTTP status code mapping (400, 404, 500, 503) in backend/src/handlers/api.py
- [ ] T065 [US3] Add metadata to response (address, government_levels, response_time_ms) in backend/src/handlers/api.py
- [ ] T066 [US3] Add Lambda Powertools structured logging for all requests in backend/src/handlers/api.py
- [ ] T067 [US3] Add X-Ray tracing for end-to-end request tracking in backend/src/handlers/api.py

**Checkpoint**: All core user stories should now be complete and API endpoint functional end-to-end

---

## Phase 6: User Story 4 - Secure API Key Management (Priority: P4)

**Goal**: Store Google Civic and OpenStates API keys securely in AWS Parameter Store and retrieve at Lambda runtime without hardcoding

**Independent Test**: Can deploy Lambda with IAM permissions, verify it retrieves keys from Parameter Store without errors, and uses them in API requests

### Tests for User Story 4

> **TDD: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T068 [P] [US4] Unit test for Parameter Store SecureString decryption in backend/tests/unit/test_parameter_store.py
- [ ] T069 [P] [US4] Unit test for key caching with @lru_cache in backend/tests/unit/test_parameter_store.py
- [ ] T070 [P] [US4] Unit test for Parameter Store unavailable scenario in backend/tests/unit/test_parameter_store.py
- [ ] T071 [US4] Integration test for Lambda retrieving keys from Parameter Store in backend/tests/integration/test_parameter_store_integration.py

### Implementation for User Story 4

- [ ] T072 [US4] Create SSM Parameter for Google Civic API key in infrastructure/stacks/backend_stack.py with path /represent-app/google-civic-api-key
- [ ] T073 [US4] Create SSM Parameter for OpenStates API key in infrastructure/stacks/backend_stack.py with path /represent-app/openstates-api-key
- [ ] T074 [US4] Add ssm:GetParameter IAM permission to Lambda execution role in infrastructure/stacks/backend_stack.py
- [ ] T075 [US4] Add ssm:DescribeParameters IAM permission to Lambda execution role in infrastructure/stacks/backend_stack.py
- [ ] T076 [US4] Update GoogleCivicClient to retrieve key from Parameter Store in backend/src/services/google_civic.py
- [ ] T077 [US4] Update OpenStatesClient to retrieve key from Parameter Store in backend/src/services/openstates.py
- [ ] T078 [US4] Add fail-fast error handling if Parameter Store keys missing in backend/src/services/parameter_store.py
- [ ] T079 [US4] Add logging for key retrieval (without logging actual key values) in backend/src/services/parameter_store.py

**Checkpoint**: Secure credential management complete - ready for production deployment

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T080 [P] Add CORS configuration to API Gateway for frontend consumption in infrastructure/stacks/backend_stack.py
- [ ] T081 [P] Update docs/api-research-openstates-and-wa-state.md with implementation findings
- [ ] T082 [P] Create API usage documentation in specs/003-address-lookup/API-USAGE.md with curl examples
- [ ] T083 Run full test suite with pytest --cov=backend/src --cov-report=html and verify >80% coverage
- [ ] T084 Run pylint on backend/src/ and backend/tests/ and fix all errors/warnings
- [ ] T085 Run black formatter on backend/src/ and backend/tests/
- [ ] T086 Validate all tasks against specs/003-address-lookup/quickstart.md workflow
- [ ] T087 Deploy infrastructure with cdk deploy from infrastructure/ directory
- [ ] T088 Manually test API endpoint with curl using 5 test addresses from different states
- [ ] T089 Verify CloudWatch logs contain structured logging for all requests
- [ ] T090 Verify X-Ray traces show end-to-end request flow with external API calls

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - MVP starts here
- **User Story 2 (Phase 4)**: Depends on Foundational completion - Can run parallel with US1 or after US1
- **User Story 3 (Phase 5)**: Depends on US1 + US2 completion (integrates both)
- **User Story 4 (Phase 6)**: Depends on US1 + US2 completion (retrofits security) - Can run parallel with US3
- **Polish (Phase 7)**: Depends on all user stories desired for release

### User Story Dependencies

**Critical Path for MVP**:
```
Setup (Phase 1) → Foundational (Phase 2) → US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5)
```

**User Story Independence**:
- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories (independently testable with hardcoded test addresses)
- **User Story 2 (P2)**: Can start after Foundational - No dependencies on US1 (independently testable with hardcoded OCD-IDs)
- **User Story 3 (P3)**: Depends on US1 + US2 (integrates both into single endpoint)
- **User Story 4 (P4)**: Depends on US1 + US2 (adds security to existing services) - Can run parallel with US3 or after

### Within Each User Story

**TDD Workflow** (Red-Green-Refactor):
1. Write tests FIRST (all tests for story marked [P] can be written in parallel)
2. Run tests → Verify they FAIL (Red phase)
3. Implement code to pass tests one by one (Green phase)
4. Refactor while keeping tests passing (Refactor phase)
5. Story complete when all tests pass

**Implementation Order**:
- Tests before implementation
- Models before services
- Services before API handlers
- Core logic before error handling
- Error handling before logging/tracing
- Story complete before next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- All 3 tasks can run in parallel (all marked [P])

**Foundational Phase (Phase 2)**:
- T006, T007, T008, T009 (models) can run in parallel (all marked [P])
- T004 and T005 must complete before model tasks

**User Story 1 Tests** (if team capacity allows):
- T010, T011, T012, T013, T014 can be written in parallel (all marked [P])
- T015 depends on understanding of integration points

**User Story 2 Tests** (if team capacity allows):
- T023-T030 can be written in parallel (all marked [P])
- T031 depends on understanding of integration points

**User Story 3 Tests** (if team capacity allows):
- T042-T051 can be written in parallel (all marked [P])
- T052 depends on understanding of full flow

**User Story 4 Tests** (if team capacity allows):
- T068, T069, T070 can be written in parallel (all marked [P])
- T071 depends on CDK infrastructure

**Polish Phase** (Phase 7):
- T080, T081, T082 can run in parallel (documentation tasks)
- T083-T085 (quality checks) can run in parallel
- T087-T090 (deployment validation) must be sequential

**Team Parallelization**:
- After Foundational phase: US1 and US2 can be built in parallel by different developers
- US3 and US4 can be built in parallel once US1+US2 are complete

---

## Parallel Example: User Story 1

```bash
# TDD Phase 1: Launch all test creation tasks in parallel
Task T010: "Unit test for Parameter Store key retrieval in backend/tests/unit/test_parameter_store.py"
Task T011: "Unit test for Google Civic client initialization in backend/tests/unit/test_google_civic.py"
Task T012: "Unit test for Google Civic address lookup success case in backend/tests/unit/test_google_civic.py"
Task T013: "Unit test for Google Civic invalid address (404) in backend/tests/unit/test_google_civic.py"
Task T014: "Unit test for Google Civic rate limit (429) in backend/tests/unit/test_google_civic.py"

# TDD Phase 2: Run all tests → Verify they FAIL (Red phase)
pytest backend/tests/unit/test_parameter_store.py -v
pytest backend/tests/unit/test_google_civic.py -v

# TDD Phase 3: Implement sequentially (Green phase)
Task T016 → T017 → T018 → T019 → T020 → T021 → T022

# TDD Phase 4: Verify all tests PASS
pytest backend/tests/unit/test_parameter_store.py backend/tests/unit/test_google_civic.py -v
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only)

**Goal**: Minimal viable product with address lookup capability

1. **Setup + Foundational** (T001-T009) → Foundation ready
2. **User Story 1** (T010-T022) → Address-to-OCD-ID conversion works
3. **User Story 2** (T023-T041) → OCD-ID-to-representatives works
4. **User Story 3** (T042-T067) → API endpoint exposes functionality
5. **STOP and VALIDATE**: Test API endpoint with real addresses
6. **Deploy/Demo**: MVP feature complete (defer US4 security to next iteration)

**MVP Scope**: 67 tasks (T001-T067)  
**Deferred**: US4 (secure keys) can use environment variables temporarily in MVP

### Incremental Delivery

**Iteration 1: Foundation** (T001-T009)
- Setup dependencies
- Core models and error handling
- **Deliverable**: Project structure ready

**Iteration 2: MVP Core** (T010-T067)
- US1: Google Civic integration
- US2: OpenStates integration
- US3: API endpoint
- **Deliverable**: Functional address lookup API (using env vars for keys)

**Iteration 3: Production Ready** (T068-T090)
- US4: Secure API keys
- Polish and documentation
- **Deliverable**: Production-ready with secure credential management

### Parallel Team Strategy

With 3 developers:

**Week 1**:
- All devs: Phase 1 + Phase 2 (T001-T009) → Foundation ready

**Week 2**:
- Developer A: User Story 1 (T010-T022) → Google Civic integration
- Developer B: User Story 2 (T023-T041) → OpenStates integration
- Developer C: User Story 4 tests (T068-T071) + CDK changes (T072-T075)

**Week 3**:
- Developer A: User Story 3 tests (T042-T052)
- Developer B: User Story 3 implementation (T053-T067)
- Developer C: User Story 4 implementation (T076-T079)

**Week 4**:
- All devs: Polish (T080-T090) + testing + deployment

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (User Story 1)**: 13 tasks (7 tests + 6 implementation)
- **Phase 4 (User Story 2)**: 19 tasks (9 tests + 10 implementation)
- **Phase 5 (User Story 3)**: 26 tasks (11 tests + 15 implementation)
- **Phase 6 (User Story 4)**: 12 tasks (4 tests + 8 implementation)
- **Phase 7 (Polish)**: 11 tasks

**Total**: 90 tasks

**Parallelizable**: 43 tasks marked [P] (48% can run concurrently with proper team coordination)

**MVP Scope** (Setup + Foundational + US1 + US2 + US3): 67 tasks  
**Production Ready** (MVP + US4 + Polish): 90 tasks

---

## Notes

- All tasks follow TDD: Write failing tests FIRST, then implement
- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable with appropriate test data
- Stop at any checkpoint to validate story independently
- Commit after each passing test or logical group of tasks
- Follow conventional commit format: `feat(api): implement Google Civic client`
- No API keys committed to version control (verified in T087)
- All paths are relative to repository root
