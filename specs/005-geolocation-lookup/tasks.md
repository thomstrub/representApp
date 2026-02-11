---
description: "Task list for geolocation-based representative lookup feature"
---

# Tasks: Geolocation-Based Representative Lookup

**Feature**: 005-geolocation-lookup  
**Branch**: `005-geolocation-lookup`  
**Input**: Design documents from `/specs/005-geolocation-lookup/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/address-lookup-api.yaml, quickstart.md

**Tests**: Following TDD approach as required by project constitution - tests written FIRST, see them FAIL, then implement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `backend/src/`, `backend/tests/`
- Paths shown below use actual project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management for geolocation integration

- [x] T001 Add googlemaps>=4.10.0 to backend/requirements.txt
- [x] T002 Install googlemaps library and verify import in backend environment
- [x] T003 [P] Create Google Maps API key in AWS Parameter Store at path /represent-app/google-maps-api-key
- [x] T004 [P] Update Lambda IAM role in infrastructure/stacks/ to include ssm:GetParameter permission for google-maps-api-key

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Review and verify existing Representative model in backend/src/models/domain.py supports all required fields
- [x] T006 [P] Review existing error handling patterns in backend/src/utils/errors.py for compatibility
- [x] T007 [P] Review existing parameter_store.py in backend/src/utils/parameter_store.py for API key retrieval pattern
- [x] T008 [P] Create test fixtures for geocoding responses in backend/tests/conftest.py
- [x] T009 [P] Create test fixtures for OpenStates geo responses in backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Google Maps Geocoding Integration (Priority: P1) 🎯 MVP

**Goal**: Enable address-to-coordinates conversion using Google Maps Geocoding API to replace deprecated Google Civic API

**Independent Test**: Can be fully tested by entering known addresses and verifying valid latitude/longitude coordinates are returned

### Tests for User Story 1 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Create test_google_maps.py in backend/tests/unit/services/ with test for successful geocoding
- [x] T011 [P] [US1] Add test case for invalid/unfound address returning empty result in backend/tests/unit/services/test_google_maps.py
- [x] T012 [P] [US1] Add test case for geocoding API timeout error in backend/tests/unit/services/test_google_maps.py
- [x] T013 [P] [US1] Add test case for geocoding API authentication error in backend/tests/unit/services/test_google_maps.py
- [x] T014 [P] [US1] Add test case for ambiguous address returning first result in backend/tests/unit/services/test_google_maps.py

### Implementation for User Story 1

- [x] T015 [US1] Create GoogleMapsClient class in backend/src/services/google_maps.py with __init__ method
- [x] T016 [US1] Implement geocode() method in GoogleMapsClient with timeout parameter (5 seconds default)
- [x] T017 [US1] Add error handling for googlemaps.exceptions in GoogleMapsClient.geocode()
- [x] T018 [US1] Add ApiException raising for empty geocoding results in GoogleMapsClient.geocode()
- [x] T019 [US1] Add logging with Lambda Powertools in GoogleMapsClient.geocode()
- [x] T020 [US1] Run all User Story 1 tests and verify they pass

**Checkpoint**: At this point, User Story 1 should be fully functional - addresses can be geocoded to coordinates

---

## Phase 4: User Story 2 - OpenStates Geo Endpoint Integration (Priority: P2)

**Goal**: Enable coordinate-to-representatives lookup using OpenStates /people.geo endpoint

**Independent Test**: Can be fully tested using known lat/lng coordinates (e.g., Seattle: 47.6105, -122.3115) and verifying correct representatives are returned

### Tests for User Story 2 (TDD - Write FIRST)

- [x] T021 [P] [US2] Create test_openstates_geo.py in backend/tests/unit/services/ with test for successful geo endpoint query
- [x] T022 [P] [US2] Add test case for empty results (valid coordinates, no data) in backend/tests/unit/services/test_openstates_geo.py
- [x] T023 [P] [US2] Add test case for OpenStates rate limit error in backend/tests/unit/services/test_openstates_geo.py
- [x] T024 [P] [US2] Add test case for OpenStates timeout error in backend/tests/unit/services/test_openstates_geo.py
- [x] T025 [P] [US2] Add test case for OpenStates transformation to Representative model in backend/tests/unit/services/test_openstates_geo.py
- [x] T026 [P] [US2] Add test case for government level grouping (federal/state/local) in backend/tests/unit/services/test_openstates_geo.py

### Implementation for User Story 2

- [x] T027 [US2] Add get_representatives_by_coordinates() method to OpenStatesClient in backend/src/services/openstates.py
- [x] T028 [US2] Implement coordinate validation (lat: -90 to 90, lng: -180 to 180) in get_representatives_by_coordinates()
- [x] T029 [US2] Add HTTP GET request with timeout (10 seconds) to /people.geo endpoint in get_representatives_by_coordinates()
- [x] T030 [US2] Add error handling for HTTP errors (401, 429, 500, timeout) in get_representatives_by_coordinates()
- [x] T031 [US2] Create transform_openstates_person_to_representative() function in backend/src/services/openstates.py
- [x] T032 [US2] Implement field mapping in transform_openstates_person_to_representative() per data-model.md
- [x] T033 [US2] Create group_by_government_level() function in backend/src/services/openstates.py
- [x] T034 [US2] Implement jurisdiction classification logic (country→federal, state→state, other→local) in group_by_government_level()
- [x] T035 [US2] Add logging with Lambda Powertools in get_representatives_by_coordinates()
- [x] T036 [US2] Run all User Story 2 tests and verify they pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - coordinates can be used to fetch representatives

---

## Phase 5: User Story 3 - End-to-End Integration (Priority: P3)

**Goal**: Integrate geocoding and representative lookup into complete address-to-representatives flow

**Independent Test**: Can be fully tested by entering various addresses (urban, rural, edge cases) and verifying correct representatives are returned within 3 seconds

### Tests for User Story 3 (TDD - Write FIRST)

- [x] T037 [P] [US3] Create test_address_to_reps.py in backend/tests/integration/ with test for complete address flow
- [x] T038 [P] [US3] Add test case for urban address with all government levels in backend/tests/integration/test_address_to_reps.py
- [x] T039 [P] [US3] Add test case for rural address or partial data in backend/tests/integration/test_address_to_reps.py
- [x] T040 [P] [US3] Add test case for zip code only input in backend/tests/integration/test_address_to_reps.py
- [x] T041 [P] [US3] Add test case for invalid address returning 400 error in backend/tests/integration/test_address_to_reps.py
- [x] T042 [P] [US3] Add test case for response structure matching API contract in backend/tests/integration/test_address_to_reps.py
- [x] T043 [P] [US3] Update existing test_address_lookup.py in backend/tests/unit/handlers/ with new flow tests

### Implementation for User Story 3

- [x] T044 [US3] Update AddressLookupHandler in backend/src/handlers/address_lookup.py to initialize GoogleMapsClient
- [x] T045 [US3] Replace Google Civic flow with geocoding call in AddressLookupHandler.handle()
- [x] T046 [US3] Add coordinate extraction from geocoding result in AddressLookupHandler.handle()
- [x] T047 [US3] Add OpenStates geo endpoint call with coordinates in AddressLookupHandler.handle()
- [x] T048 [US3] Add transformation and grouping of representatives in AddressLookupHandler.handle()
- [x] T049 [US3] Build final response with metadata (address, coordinates, total_count, government_levels) in AddressLookupHandler.handle()
- [x] T050 [US3] Add warnings array for partial results in AddressLookupHandler.handle()
- [x] T051 [US3] Verify error handling preserves existing error codes and messages
- [x] T052 [US3] Add performance logging (track geocoding time, OpenStates time, total time)
- [x] T053 [US3] Run all User Story 3 tests and verify they pass
- [x] T054 [US3] Validate end-to-end response time is under 3 seconds using quickstart.md test scenarios

**Checkpoint**: All user stories should now be independently functional - complete address lookup flow works

---

## Phase 6: User Story 4 - Legacy Code Cleanup (Priority: P4)

**Goal**: Remove all deprecated Google Civic API code and configurations after new flow is verified

**Independent Test**: Can be verified by searching codebase for Google Civic references and confirming none remain except historical documentation

### Tests for User Story 4 (Verification)

- [x] T055 [P] [US4] Run full test suite to ensure no tests depend on GoogleCivicClient
- [x] T056 [P] [US4] Verify all integration tests pass without Google Civic mocks

### Implementation for User Story 4

- [x] T057 [P] [US4] Remove GoogleCivicClient class from backend/src/services/google_civic.py
- [x] T058 [P] [US4] Remove test_google_civic.py from backend/tests/unit/services/ if exists
- [x] T059 [P] [US4] Remove Google Civic API key from AWS Parameter Store or mark as deprecated
- [x] T060 [P] [US4] Update Lambda IAM role to remove Google Civic API permissions if any
- [x] T061 [P] [US4] Search codebase for remaining Google Civic references and remove/update
- [x] T062 [US4] Run full test suite after cleanup to verify nothing broke
- [x] T063 [US4] Update any documentation referencing Google Civic API to geolocation approach

**Checkpoint**: Legacy Google Civic code completely removed, new geolocation flow is the only implementation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [x] T064 [P] Update backend/README.md with geolocation flow documentation
- [x] T065 [P] Verify all tests pass and coverage remains at 100% for unit tests
- [x] T066 [P] Run pylint and black formatter on all modified files
- [x] T067 [P] Update API documentation with new internal implementation notes
- [x] T068 Run quickstart.md validation scenarios end-to-end
- [x] T069 Verify CloudWatch logs show proper X-Ray tracing for new flow
- [x] T070 [P] Create migration notes documenting changes for team

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 3 (P3): Depends on User Story 1 AND User Story 2 completion
  - User Story 4 (P4): Depends on User Story 3 completion and validation
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independently testable)
- **User Story 3 (P3)**: **DEPENDS ON** User Story 1 AND User Story 2 (needs both geocoding and geo endpoint working)
- **User Story 4 (P4)**: **DEPENDS ON** User Story 3 (must verify new flow works before removing old code)

### Within Each User Story

**TDD Workflow (Red-Green-Refactor)**:
1. Write tests FIRST (T010-T014 for US1)
2. Run tests → Verify they FAIL (Red)
3. Implement code (T015-T019 for US1)
4. Run tests → Verify they PASS (Green)
5. Refactor while keeping tests green (Refactor)

**Implementation Order within Story**:
- Tests before implementation
- Core functionality before error handling
- Error handling before logging
- Validation checkpoint at end of each story

### Parallel Opportunities

- **Setup Phase**: All tasks marked [P] can run in parallel (T003, T004)
- **Foundational Phase**: All tasks marked [P] can run in parallel (T006, T007, T008, T009)
- **User Story 1 & 2**: Can be developed in parallel after Foundational phase completes
  - Team Member A: User Story 1 (Geocoding)
  - Team Member B: User Story 2 (OpenStates geo)
- **Tests within User Story**: All test creation tasks marked [P] can run in parallel
  - US1 tests: T010-T014 can all be written simultaneously
  - US2 tests: T021-T026 can all be written simultaneously
  - US3 tests: T037-T043 can all be written simultaneously

---

## Parallel Example: User Story 1

If you have multiple developers, you can parallelize test creation:

```bash
# Developer A: Write these tests in parallel
Task T010: Create test_google_maps.py with successful geocoding test
Task T011: Add invalid address test case
Task T012: Add timeout error test case

# Developer B: Write these tests in parallel
Task T013: Add authentication error test case
Task T014: Add ambiguous address test case

# All developers: Wait for tests to be complete, then implement together
Task T015: Create GoogleMapsClient class
# ... implementation tasks ...
```

For User Story 2, tests T021-T026 (all marked [P]) can be written simultaneously by different developers.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → Dependencies installed
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories) → Foundation ready
3. Complete Phase 3: User Story 1 → Geocoding works
4. **STOP and VALIDATE**: Test geocoding independently using quickstart.md
5. Decision point: Deploy partial feature or continue to complete flow

### Recommended: Complete Flow (User Stories 1-3)

1. Complete Setup + Foundational → Foundation ready
2. Complete User Story 1 + User Story 2 in parallel → Both pieces work independently
3. Complete User Story 3 → Complete end-to-end flow works
4. **VALIDATION CHECKPOINT**: Run all quickstart.md scenarios
5. Deploy complete feature → Full address-to-representatives lookup live
6. Complete User Story 4 → Legacy code removed

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup + Foundational
2. **Parallel (after Foundational done)**:
   - Developer A: User Story 1 (Geocoding) → T010-T020
   - Developer B: User Story 2 (OpenStates geo) → T021-T036
3. **Together**: User Story 3 (Integration) → T037-T054
4. **Together**: User Story 4 (Cleanup) → T055-T063
5. **Together**: Polish → T064-T070

---

## Notes

- **[P] tasks** = Different files, no dependencies, can run in parallel
- **[Story] label** = Maps task to specific user story for traceability
- **TDD Required**: Project constitution requires Test-Driven Development - tests MUST be written first
- **Each user story** should be independently completable and testable
- **Verify tests fail** before implementing (Red phase of Red-Green-Refactor)
- **Commit frequently** after each task or logical group
- **Stop at checkpoints** to validate story independently before proceeding
- **User Story 3** depends on User Stories 1 AND 2 being complete
- **User Story 4** depends on User Story 3 being validated
- **Frontend**: No changes required - maintains existing API contract

---

## Success Criteria

At completion, the feature should demonstrate:

- ✅ All tests pass (unit and integration)
- ✅ Test coverage remains at or above current levels (100% for unit tests)
- ✅ End-to-end lookup completes in <3 seconds
- ✅ 95% of valid US addresses geocode successfully
- ✅ Representative data accuracy matches or exceeds current implementation
- ✅ All error scenarios handled gracefully with appropriate error codes
- ✅ Frontend continues to work without modifications
- ✅ No Google Civic API code remains in codebase
- ✅ CloudWatch logs show proper X-Ray tracing
- ✅ All quickstart.md validation scenarios pass

---

**Generated**: 2026-02-10  
**Status**: Ready for implementation  
**Total Tasks**: 70 tasks across 7 phases
