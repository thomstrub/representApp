# Implementation Plan: Address-Based Representative Lookup API

**Branch**: `003-address-lookup` | **Date**: February 8, 2026 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/003-address-lookup/spec.md`

## Summary

Build backend REST API endpoint (`GET /representatives?address={address}`) that converts US street addresses to political representatives. Integration uses Google Civic Information API to resolve addresses to OCD identifiers, then OpenStates.org API v3 to retrieve representative data (federal and state officials). No persistent caching in MVP - direct API calls only. Secure API key management via AWS Parameter Store.

## Technical Context

**Language/Version**: Python 3.9 (AWS Lambda runtime)  
**Primary Dependencies**: AWS Lambda Powertools (Logger, Tracer, Validator), boto3 (AWS SDK), requests (HTTP client)  
**Storage**: N/A (no persistent storage in MVP; caching deferred to Phase 4)  
**Testing**: pytest, moto (AWS service mocks), pytest-cov (>80% coverage)  
**Target Platform**: AWS Lambda (serverless compute) via API Gateway HTTP v2  
**Project Type**: Web application (backend-only; frontend is separate feature)  
**Performance Goals**: <3 seconds p95 latency for address lookups (end-to-end from API Gateway to client)  
**Constraints**: Google Civic API 25k req/day, OpenStates API 5k req/day (free tier limits); no retry logic in MVP  
**Scale/Scope**: MVP supporting 50 US states, ~250 requests/day estimated, single Lambda function with 4-5 handler methods

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-Driven Development ✅ PASS
- **Compliance**: Feature spec includes comprehensive acceptance criteria for TDD
- **Evidence**: 21 acceptance scenarios defined across 4 user stories; each can be written as failing test first
- **Plan**: Follow Red-Green-Refactor for each functional requirement

### II. Testing Scope ✅ PASS
- **Compliance**: Backend-only feature using pytest + moto for AWS mocks
- **Evidence**: FR functional requirements testable via unit tests (handler logic, validation) and integration tests (API Gateway → Lambda flow)
- **Plan**: No e2e frameworks; manual curl/Postman testing for end-to-end verification

### III. Code Quality Gates ✅ PASS
- **Compliance**: Existing backend infrastructure has pylint, black, pytest-cov configured
- **Evidence**: Backend/pyproject.toml defines quality tools; Makefile has `make lint` and `make test` targets
- **Plan**: All commits pass quality gates before merge

### IV. Incremental Development ✅ PASS
- **Compliance**: Feature broken into 4 prioritized user stories (P1-P4), each independently testable
- **Evidence**: P1 (Google Civic integration), P2 (OpenStates integration), P3 (API endpoint), P4 (secure keys) can be implemented and committed sequentially
- **Plan**: Commit after each passing user story with all tests green

### V. Serverless Architecture ✅ PASS
- **Compliance**: Feature uses AWS Lambda + API Gateway + Parameter Store per constitution
- **Evidence**: Existing backend infrastructure already deployed with HTTP API Gateway v2, Lambda, CloudWatch, X-Ray
- **Plan**: Extend existing Lambda handler with new `/representatives` route

### VI. Accessible Information Design ✅ PASS
- **Compliance**: API returns structured JSON with representatives categorized by government level
- **Evidence**: FR-007 specifies categorization (federal, state, local); FR-017 defines consistent response structure with warnings for missing data
- **Plan**: Response includes metadata and warnings arrays to clearly communicate data gaps (e.g., local officials not available)

**GATE RESULT**: ✅ **ALL GATES PASS** - No violations; no complexity justification needed. Proceed to Phase 0 research.

---

### Post-Phase 1 Re-Evaluation (February 8, 2026)

*RE-CHECK: After completing Phase 1 design (research.md, data-model.md, contracts/, quickstart.md)*

#### I. Test-Driven Development ✅ PASS
- **Validation**: Data models include validation rules → each rule testable via unit test
- **Evidence**: 6 entities defined with field-level validation (e.g., Representative.id required, address max 500 chars)
- **Status**: TDD approach remains viable; quickstart.md documents Red-Green-Refactor workflow

#### II. Testing Scope ✅ PASS
- **Validation**: No e2e frameworks introduced; integration testing uses moto mocks
- **Evidence**: Quickstart.md shows pytest-only testing with moto for Parameter Store/Lambda mocks
- **Status**: Testing scope unchanged from initial approval

#### III. Code Quality Gates ✅ PASS
- **Validation**: Quickstart.md includes lint workflow (`make lint`, `pylint`, `black`)
- **Evidence**: Quality gates documented in developer workflow section
- **Status**: Existing quality infrastructure sufficient; no new tools needed

#### IV. Incremental Development ✅ PASS
- **Validation**: OpenAPI contract confirms 1 endpoint, 6 entities → small, testable units
- **Evidence**: Contract defines single GET endpoint; data model shows 6 independent entities
- **Status**: Feature remains incrementally implementable (service by service, model by model)

#### V. Serverless Architecture ✅ PASS
- **Validation**: Quickstart references existing Lambda + API Gateway + Parameter Store infrastructure
- **Evidence**: No new AWS services beyond Parameter Store (already serverless)
- **Status**: Architecture unchanged; extends existing serverless backend

#### VI. Accessible Information Design ✅ PASS
- **Validation**: Data model includes `warnings` array in response for partial results transparency
- **Evidence**: AddressLookupResponse model has `warnings: list[str]` field; error model has user-friendly `message` field
- **Status**: Design prioritizes clear communication of data gaps and errors to end users

**RE-EVALUATION RESULT**: ✅ **ALL GATES STILL PASS** - Phase 1 design maintains constitutional compliance. No new violations introduced. Ready for Phase 2 implementation.

## Project Structure

### Documentation (this feature)

```text
specs/003-address-lookup/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology decisions and patterns (to be created)
├── data-model.md        # Phase 1: Entity models and validation rules (to be created)
├── quickstart.md        # Phase 1: Quick start guide for developers (to be created)
├── contracts/           # Phase 1: API contracts (OpenAPI/JSON schemas) (to be created)
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Specification completeness checklist (complete)
└── tasks.md             # Phase 2: Detailed task breakdown (NOT created by plan command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── api.py                    # [EXTEND] Add /representatives route handler
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                   # [EXTEND] Add Representative, Division models
│   │   ├── domain.py                 # [EXISTS] Domain models 
│   │   └── store.py                  # [EXISTS] DynamoDB store (not used in MVP)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── google_civic.py           # [NEW] Google Civic API client
│   │   ├── openstates.py             # [NEW] OpenStates API client
│   │   └── parameter_store.py        # [NEW] AWS Parameter Store key retrieval
│   └── utils/
│       ├── __init__.py
│       ├── validators.py             # [EXTEND] Add address validation
│       └── ocd_parser.py             # [NEW] OCD-ID parsing and categorization
├── tests/
│   ├── unit/
│   │   ├── test_api_handler.py       # [EXTEND] Add /representatives tests
│   │   ├── test_google_civic.py      # [NEW] Google Civic client tests
│   │   ├── test_openstates.py        # [NEW] OpenStates client tests
│   │   ├── test_validators.py        # [NEW] Address validation tests
│   │   └── test_ocd_parser.py        # [NEW] OCD-ID parsing tests
│   └── integration/
│       └── test_address_lookup.py    # [NEW] End-to-end address lookup flow
├── pyproject.toml                    # [EXISTS] Project dependencies
├── requirements.txt                  # [EXTEND] Add requests library
└── Makefile                          # [EXISTS] Build and test targets

infrastructure/
├── app.py                            # [EXISTS] CDK app entry point
├── stacks/
│   └── backend_stack.py              # [EXTEND] Add Parameter Store parameters
└── requirements.txt                  # [EXISTS] CDK dependencies
```

**Structure Decision**: Using existing backend-only web application structure. This is a pure backend API feature - no frontend components. All new code extends existing `backend/src/` directories. Infrastructure changes are minimal (add Parameter Store parameters for API keys via CDK).

## Complexity Tracking

No complexity violations detected. Feature aligns with all constitutional principles.
