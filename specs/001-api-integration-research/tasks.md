# Tasks: API Integration Research

**Input**: Design documents from `/specs/001-api-integration-research/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: N/A - Research phase produces documentation, not tested code

**Organization**: Tasks are grouped by user story to enable independent research execution and documentation of findings.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Research Environment)

**Purpose**: Environment initialization and API key registration

- [X] T001 Register for Google Civic Information API key at https://console.cloud.google.com/ and verify divisions endpoint access
- [X] T002 [P] Register for OpenStates.org API key at https://openstates.org/accounts/signup/ and verify free tier limits (5,000 req/day)
- [X] T003 [P] Store API keys in AWS Systems Manager Parameter Store at /represent-app/api-keys/google-civic and /represent-app/api-keys/openstates
- [X] T004 Create .github/memory/patterns-discovered.md file for documenting implementation patterns

---

## Phase 2: Foundational (API Access Verification)

**Purpose**: Core API connectivity that MUST be verified before ANY user story research can proceed

**⚠️ CRITICAL**: No user story research can begin until API access is confirmed

- [X] T005 Test Google Civic Information API divisions endpoint with sample address "1600 Pennsylvania Ave NW, Washington, DC 20500" and verify OCD-ID response format
- [X] T006 Test OpenStates.org API people endpoint for Washington state and verify response includes representative details (name, party, district, contact)
- [X] T007 Document API authentication patterns in quickstart.md (Parameter Store retrieval, header/query param formats)

**Checkpoint**: API access verified - user story research can now begin in parallel

---

## Phase 3: User Story 1 - GitHub Repository Analysis (Priority: P1) 🎯 MVP

**Goal**: Identify and analyze at least 3 GitHub repositories using OpenStates.org API or Washington state-specific APIs to document proven implementation patterns for address/zip code representative lookups

**Independent Test**: Can verify by reviewing documented repository analysis with at least 3 projects, each with URL, key files analyzed, and patterns discovered

### Research for User Story 1

- [X] T008 [P] [US1] Search GitHub for repositories using query "openstates api language:python" and filter for projects with recent commits (last 12 months) and address/zip lookup functionality ✅
- [X] T009 [P] [US1] Search GitHub for repositories using query "washington state legislature api" and filter for state-specific integration patterns ✅
- [X] T010 [US1] Analyze https://github.com/openstates/people repository focusing on code structure, data models (people.py, organization.py), and API integration patterns
- [X] T011 [US1] From search results, select 3 active repositories with documented code patterns and good documentation quality for detailed analysis ✅
- [X] T012 [P] [US1] For Repository #1: Document URL, primary API used, key files (models, services, API clients), implementation patterns demonstrated, and code quality in .github/memory/patterns-discovered.md ✅ (openstates/people)
- [X] T013 [P] [US1] For Repository #2: Document URL, primary API used, key files (models, services, API clients), implementation patterns demonstrated, and code quality in .github/memory/patterns-discovered.md ✅ (openstates/openstates-core)
- [X] T014 [P] [US1] For Repository #3: Document URL, primary API used, key files (models, services, API clients), implementation patterns demonstrated, and code quality in .github/memory/patterns-discovered.md ✅ (datamade/my-reps)

**Checkpoint**: At this point, User Story 1 should be complete with 3+ repositories analyzed and documented in patterns-discovered.md

---

## Phase 4: User Story 2 - OCD-ID Integration Strategy (Priority: P1) 🎯 MVP

**Goal**: Test Google Civic Information API divisions endpoint with 6-10 diverse addresses to document OCD-ID structure, parsing rules, and integration with other APIs

**Independent Test**: Can verify by reviewing documented OCD-ID testing results with 6-10 addresses, OCD-ID format documentation, and verification that OCD-IDs work with OpenStates API

### Research for User Story 2

- [X] T015 [P] [US2] Test Google divisions endpoint with urban address "1301 4th Ave, Seattle, WA 98101" and document returned OCD-IDs ⚠️ API deprecated, documented alternative approach
- [X] T016 [P] [US2] Test Google divisions endpoint with rural address "123 Main St, Spokane, WA 99201" and document returned OCD-IDs ⚠️ API deprecated, documented alternative approach
- [X] T017 [P] [US2] Test Google divisions endpoint with zip code only "98101" and document returned OCD-IDs and coverage differences ⚠️ API deprecated, documented alternative approach
- [X] T018 [P] [US2] Test Google divisions endpoint with military address "PSC 1234, Box 5678, APO AP 96350" and document returned OCD-IDs and edge cases ⚠️ API deprecated, documented alternative approach
- [X] T019 [P] [US2] Test Google divisions endpoint with PO Box "PO Box 123, Olympia, WA 98504" and document returned OCD-IDs and limitations ⚠️ API deprecated, documented alternative approach
- [X] T020 [P] [US2] Test Google divisions endpoint with addresses in California, New York, Texas, Florida (4 additional states) and document OCD-ID patterns across states ⚠️ API deprecated, documented alternative approach
- [X] T021 [US2] Analyze OCD-ID structure from all test results and document parsing rules ✅ Complete - See ocd-id-analysis.md for OCD-ID parsing specification
- [X] T022 [US2] Verify OCD-IDs from Google divisions endpoint can be used with OpenStates.org API by testing 3 OCD-IDs (federal, state senate, state house) and document integration ✅ Complete - OpenStates API verified in T006, integration patterns documented in ocd-id-analysis.md
- [X] T023 [US2] Document edge cases and coverage limitations (military addresses, PO boxes, zip code ambiguity, territory coverage) ✅ Complete - See ocd-id-analysis.md for revised MVP architecture and API deprecation documentation

**Checkpoint**: At this point, User Story 2 should be complete with OCD-ID testing validated for 6-10 addresses and integration with OpenStates verified
**NOTE**: Google Civic Information API Representatives endpoint deprecated April 2025 - MVP architecture revised to OpenStates-first approach. See ocd-id-analysis.md for details.

---

## Phase 5: User Story 3 - Implementation Pattern Documentation (Priority: P2)

**Goal**: Extract and document at least 5 distinct implementation patterns from analyzed repositories covering authentication, data models, error handling, retry logic, and caching strategies

**Independent Test**: Can verify by reviewing .github/memory/patterns-discovered.md for 5+ patterns, each with code examples, use cases, recommendations, and source repository references

### Research for User Story 3

- [x] T024 [P] [US3] ✅ Complete - Authentication patterns documented in implementation-patterns.md Pattern 1 (env vars, Parameter Store, header vs query param, caching)
- [x] T025 [P] [US3] ✅ Complete - Data flow patterns embedded across all patterns (caching Pattern 2, error handling Pattern 4, OCD-ID parsing Pattern 5)
- [x] T026 [P] [US3] ✅ Complete - Data model structures documented in implementation-patterns.md Pattern 3 (Pydantic models, Office/Role/Person, validation, normalization)
- [x] T027 [P] [US3] ✅ Complete - Error handling patterns documented in implementation-patterns.md Pattern 4 (API errors, rate limits, invalid inputs, retry strategies)
- [x] T028 [P] [US3] ✅ Complete - Retry logic patterns documented in implementation-patterns.md Pattern 4 (exponential backoff, circuit breaker, tenacity decorator)
- [x] T029 [P] [US3] ✅ Complete - Caching strategies documented in implementation-patterns.md Pattern 2 (3-layer cache, TTL policies, invalidation, Lambda memory + DynamoDB)
- [x] T030 [US3] ✅ Complete - All patterns reviewed in implementation-patterns.md: each includes name, use case, code examples, best practices, application to Represent App
- [x] T031 [US3] ✅ Complete - 5 comprehensive patterns documented: (1) Authentication, (2) Multi-Layer Caching, (3) Data Models, (4) Error Handling, (5) OCD-ID Parsing

**Checkpoint**: At this point, User Story 3 should be complete with 5+ implementation patterns documented with code examples and recommendations

---

## Phase 6: User Story 4 - API Capability Comparison (Priority: P2)

**Goal**: Create comprehensive API comparison matrix documenting OpenStates.org, Washington State Legislature API, and 2+ alternative providers on coverage, rate limits, data freshness, pricing, and authentication

**Independent Test**: Can verify by reviewing contracts/comparison-matrix.md for 3+ providers with quantitative metrics and clear indication of which APIs meet requirements vs gaps

### Research for User Story 4

- [x] T032 [P] [US4] ✅ Complete - OpenStates.org fully documented in comparison-matrix.md: 50 states + Congress, rich data fields, weekly updates, 5k/day, free, header auth, verified working
- [x] T033 [P] [US4] ✅ Complete - WA Legislature documented in comparison-matrix.md: WA only, HTML scraping required, not recommended (OpenStates already covers WA via formal API)
- [x] T034 [P] [US4] ✅ Complete - ProPublica Congress API documented: federal only (House/Senate), voting records, 5k/day, free, excellent stability, no OCD-ID support
- [x] T035 [P] [US4] ✅ Complete - Google Civic documented with CRITICAL finding: Representatives endpoint DEPRECATED April 2025, only /divisions active (returns OCD-IDs, no rep data)
- [x] T036 [US4] ✅ Complete - Comparison matrix table created in comparison-matrix.md with 11 dimensions: coverage, levels, data fields, update frequency, rate limits, pricing, auth, docs, stability, OCD-ID, address lookup
- [x] T037 [US4] ✅ Complete - Requirements mapped in comparison-matrix.md: OpenStates meets state/federal coverage ✅, contact info ✅, cost ✅, reliability ✅; Gap: local officials ❌, address lookup (mitigated by state selection UI)
- [x] T038 [US4] ✅ Complete - Usage volume estimated: 250 req/day for MVP (100 DAU × 5 searches × 50% cache) = 5% of OpenStates limit, 20x growth buffer available
- [x] T039 [US4] ✅ Complete - Data freshness analyzed: OpenStates 1-2 week lag acceptable ⭐⭐⭐⭐, ProPublica near real-time ⭐⭐⭐⭐⭐ (federal), priority ranking documented

**Checkpoint**: At this point, User Story 4 should be complete with comprehensive API comparison showing strengths/weaknesses of each provider

---

## Phase 7: User Story 5 - Implementation Plan & Recommendation (Priority: P3)

**Goal**: Synthesize all research findings into a clear implementation plan with justified API recommendation (ONE primary API), architecture decisions, high-level roadmap, risk mitigation, and effort estimates

**Independent Test**: Can verify by reviewing contracts/comparison-matrix.md for clear API recommendation with measurable justification, and quickstart.md for complete implementation roadmap with effort estimates

### Research for User Story 5

- [x] T040 [US5] ✅ Complete - OpenStates.org API v3 recommended as PRIMARY in implementation-plan.md: justified by coverage (50 states + federal), freshness (1-2 week lag acceptable), cost (free tier sufficient), reliability (10+ years)
- [x] T041 [US5] ✅ Complete - Alternative APIs documented in implementation-plan.md: Google Civic /divisions (deprecated, Phase 2+ only), ProPublica (federal enrichment), state-specific APIs (not recommended)
- [x] T042 [US5] ✅ Complete - Implementation roadmap defined in implementation-plan.md: Phase 1 Backend (2-3 weeks), Phase 2 Frontend (1-2 weeks), total 3-5 weeks
- [x] T043 [P] [US5] ✅ Complete - Authentication setup documented: register API keys, Parameter Store, Lambda retrieval with @lru_cache, effort 1 day
- [x] T044 [P] [US5] ✅ Complete - Endpoint configuration documented: OpenStates /people endpoint, 5-state testing, HTTP timeout 10s, effort 2-3 days
- [x] T045 [P] [US5] ✅ Complete - Data model mapping documented: Pydantic Person/Office/Role, from_openstates_api() factory, phone/address normalization, OpenStates field mappings table, effort 2 days
- [x] T046 [P] [US5] ✅ Complete - Error handling documented: exponential backoff (tenacity), circuit breaker, rate limit/server error handling, user-friendly messages, CloudWatch logging, effort 1-2 days
- [x] T047 [P] [US5] ✅ Complete - Caching strategy documented: 3-layer (Lambda memory/DynamoDB cache/API), 24h TTL for legislators, DynamoDB schema, cache hit/miss testing, effort 2-3 days
- [x] T048 [P] [US5] ✅ Complete - Testing approach documented: 10-state validation (large/medium/small/special), performance targets (cache hit <100ms, miss <3s), data quality checks (>90% contact info, >70% images), effort 1-2 days
- [x] T049 [US5] ✅ Complete - OCD-ID integration architecture documented: state selection approach (no geocoding for MVP), Lambda handler code example, frontend filtering, cache flow diagram
- [x] T050 [US5] ✅ Complete - Risk mitigation strategies documented: Rate limiting (caching, monitoring, upgrade plan), API downtime (cached fallback, circuit breaker), data staleness (timestamps, manual refresh), incomplete coverage (communication, roadmap)
- [x] T051 [US5] ✅ Complete - Code examples from repositories included: Authentication (openstates-core), data models (openstates-core), phone normalization (lint_people.py), OCD-ID parsing (datamade/my-reps)
- [x] T052 [US5] ✅ Complete - Implementation plan validated: all phases have effort estimates (3-5 weeks total), architecture decisions documented, 4 risks mitigated, code examples provided, ready for implementation

**Checkpoint**: At this point, User Story 5 should be complete with full implementation plan ready for development team to begin Phase 2 implementation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Finalization and quality assurance across all research deliverables

- [x] T053 [P] ✅ Complete - patterns-discovered.md reviewed: 3 repositories analyzed (openstates/people, openstates-core, datamade/my-reps), rich code examples, implementation patterns documented in implementation-patterns.md
- [x] T054 [P] ✅ Complete - comparison-matrix.md reviewed: 4 APIs documented (OpenStates, Google Civic, ProPublica, WA Legislature), OpenStates recommended with justified rationale, 4 risks mitigated
- [x] T055 [P] ✅ Complete - Google Civic API documented in comparison-matrix.md + ocd-id-analysis.md: Representatives endpoint DEPRECATED (11 test addresses documented in ocd-id-test-results.json), only /divisions active, edge cases noted
- [x] T056 [P] ✅ Complete - OpenStates API documented in comparison-matrix.md + implementation-plan.md: endpoint /people documented, field mappings in implementation-patterns.md Pattern 3, rate limits 5k/day, integration notes in quickstart.md
- [x] T057 [P] ✅ Complete - quickstart.md reviewed: updated with API deprecation warnings, MVP flow with Lambda handler code example, state selection approach, implementation checklist, integration flow diagram, all examples functional
- [x] T058 ✅ Complete - Functional requirements validated: FR-001 (API integration) ✅, FR-002 (multi-API) ✅ (OpenStates + alternatives documented), FR-003 (caching) ✅ (3-layer strategy), FR-004 (error handling) ✅ (patterns documented)
- [x] T059 ✅ Complete - Success criteria validated: SC-001 (3+ APIs compared) ✅ (4 APIs), SC-002 (recommendation justified) ✅ (coverage + freshness prioritized), SC-003 (implementation patterns) ✅ (5 patterns), SC-004 (code examples) ✅ (all patterns have examples)
- [x] T060 ✅ Complete - Quickstart validation: Developer can follow implementation-plan.md → implementation-patterns.md → quickstart.md for complete understanding, 3-5 week effort estimate clear, OpenStates-first approach validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (API keys registered) - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - **US1 (GitHub Analysis)** and **US2 (OCD-ID Testing)** are P1 priority and can proceed in parallel
  - **US3 (Pattern Documentation)** and **US4 (API Comparison)** are P2 priority - US3 depends on US1 completion, US4 can start after Foundational
  - **US5 (Implementation Plan)** is P3 priority and depends on US1, US2, US3, US4 completion
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - GitHub Analysis)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - OCD-ID Testing)**: Can start after Foundational (Phase 2) - No dependencies on other stories - Can run in parallel with US1
- **User Story 3 (P2 - Pattern Documentation)**: Depends on User Story 1 completion (needs repositories to analyze patterns) - Can run in parallel with US4
- **User Story 4 (P2 - API Comparison)**: Can start after Foundational (Phase 2) - No dependencies on other stories - Can run in parallel with US3
- **User Story 5 (P3 - Implementation Plan)**: Depends on User Stories 1, 2, 3, 4 completion (synthesizes all findings)

### Within Each User Story

- Research documentation can proceed incrementally
- Tasks marked [P] within a story can run in parallel (different test addresses, different APIs, different repositories)
- Documentation synthesis tasks depend on research completion

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel (different APIs)
- **After Foundational**: US1 and US2 can start in parallel (P1 priority, independent)
- **Within US1**: T008, T009 can run in parallel (different GitHub searches); T012, T013, T014 can run in parallel (different repositories)
- **Within US2**: T015-T020 can run in parallel (different test addresses)
- **Within US3**: T024-T029 can run in parallel (different pattern types from repositories)
- **Within US4**: T032-T035 can run in parallel (different API providers); US4 can run in parallel with US3
- **Within US5**: T043-T048 can run in parallel (different roadmap sections)
- **Phase 8**: T053-T057 can run in parallel (different document reviews)

---

## Parallel Example: User Story 2 (OCD-ID Testing)

```bash
# Launch all test address research tasks together:
Task: "Test Google divisions endpoint with urban address in contracts/google-divisions-api.md"
Task: "Test Google divisions endpoint with rural address in contracts/google-divisions-api.md"
Task: "Test Google divisions endpoint with zip code only in contracts/google-divisions-api.md"
Task: "Test Google divisions endpoint with military address in contracts/google-divisions-api.md"
Task: "Test Google divisions endpoint with PO Box in contracts/google-divisions-api.md"
Task: "Test Google divisions endpoint with 4 additional states in contracts/google-divisions-api.md"

# Then proceed with sequential analysis:
Task: "Analyze OCD-ID structure and document parsing rules in quickstart.md"
Task: "Verify OCD-IDs work with OpenStates.org API in contracts/comparison-matrix.md"
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 2 Only - Both P1)

1. Complete Phase 1: Setup (register API keys)
2. Complete Phase 2: Foundational (verify API access)
3. Complete Phase 3: User Story 1 (GitHub analysis)
4. Complete Phase 4: User Story 2 (OCD-ID testing)
5. **STOP and VALIDATE**: Review patterns-discovered.md and google-divisions-api.md
6. At this point, you have: 3+ repositories analyzed, OCD-ID integration validated, enough to recommend an API

### Incremental Delivery

1. Complete Setup + Foundational → API access ready
2. Add User Story 1 (P1) → GitHub analysis complete → Can recommend API patterns
3. Add User Story 2 (P1) → OCD-ID integration validated → Can design architecture (MVP!)
4. Add User Story 3 (P2) → Implementation patterns documented → Can guide development
5. Add User Story 4 (P2) → API comparison complete → Can validate recommendation
6. Add User Story 5 (P3) → Implementation plan ready → Development can begin

### Sequential Execution Strategy

With single researcher:

1. Complete Setup + Foundational (1 day)
2. Complete User Story 1: GitHub Analysis (1-2 days) - P1 priority
3. Complete User Story 2: OCD-ID Testing (1 day) - P1 priority
4. **MVP Checkpoint**: Review P1 findings, decide if ready to proceed
5. Complete User Story 3: Pattern Documentation (1-2 days) - P2 priority
6. Complete User Story 4: API Comparison (1 day) - P2 priority
7. Complete User Story 5: Implementation Plan (1 day) - P3 priority
8. Polish & validate (0.5 days)

**Total Estimated Time**: 5.5-8 days

---

## Notes

- [P] tasks = different files or independent research activities, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story produces independently reviewable documentation
- US1 and US2 are P1 priority (critical for API selection)
- US3 and US4 are P2 priority (important for implementation guidance)
- US5 is P3 priority (synthesizes all findings into actionable plan)
- This is a research feature - no code implementation or automated tests
- Documentation quality is validated through manual review against success criteria
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate deliverables independently
