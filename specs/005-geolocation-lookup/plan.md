# Implementation Plan: Geolocation-Based Representative Lookup

**Branch**: `005-geolocation-lookup` | **Date**: 2026-02-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-geolocation-lookup/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Replace the deprecated Google Civic Information API with a geolocation-based flow: users enter an address, the system geocodes it to latitude/longitude coordinates using Google Maps Geocoding API, then queries the OpenStates `/people.geo` endpoint to retrieve representatives. This maintains the same frontend contract while migrating to a more reliable data source after Google Civic's representatives endpoint deprecation (April 2025).

## Technical Context

**Language/Version**: Python 3.9 (AWS Lambda runtime)  
**Primary Dependencies**: AWS Lambda Powertools 2.30.0, googlemaps Python library, boto3, requests  
**Storage**: DynamoDB (not used in MVP - direct API calls only), AWS Systems Manager Parameter Store (API keys)  
**Testing**: pytest with moto for AWS service mocks, pytest-cov for coverage  
**Target Platform**: AWS Lambda with HTTP API Gateway v2  
**Project Type**: Web application (backend/frontend split)  
**Performance Goals**: <3 seconds end-to-end for address-to-representatives lookup, handle 95% of valid US addresses  
**Constraints**: <5 second timeout for geocoding API, <10 second timeout for OpenStates API, no caching layer (direct API calls)  
**Scale/Scope**: MVP scope with 4 user stories, replacing existing API integration without frontend changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-Driven Development (NON-NEGOTIABLE)
**Status**: ✅ PASS  
**Rationale**: Feature implementation will follow TDD cycle for all new services (GoogleMapsClient, updated AddressLookupHandler). Tests written first for geocoding, OpenStates geo endpoint integration, and error handling.

### II. Testing Scope
**Status**: ✅ PASS  
**Rationale**: Using pytest unit tests with moto for AWS mocks, integration tests for end-to-end flows. No e2e frameworks. Manual browser testing sufficient for frontend verification.

### III. Code Quality Gates
**Status**: ✅ PASS  
**Rationale**: All existing quality gates apply (pytest, pylint, black formatting, conventional commits). No exceptions needed.

### IV. Incremental Development
**Status**: ✅ PASS  
**Rationale**: Feature naturally breaks into 4 priority-ordered user stories (P1: geocoding, P2: OpenStates geo, P3: end-to-end, P4: cleanup). Each independently testable and committable.

### V. Serverless Architecture
**Status**: ✅ PASS  
**Rationale**: Uses existing Lambda + API Gateway + DynamoDB infrastructure. Adds Parameter Store for Google Maps API key. No architectural changes.

### VI. Accessible Information Design
**Status**: ✅ PASS  
**Rationale**: Maintains existing frontend contract and user experience. Address input → representatives output flow unchanged. <3 second response time preserved.

**GATE DECISION**: ✅ PROCEED - All constitutional principles satisfied. No violations to justify.

---

## Post-Design Constitution Re-Evaluation

*Re-evaluated after Phase 1 design artifacts completed.*

### Design Artifacts Review

1. **research.md**: Technology decisions documented with alternatives considered
2. **data-model.md**: Entity models maintain existing patterns, no new complexity added
3. **contracts/address-lookup-api.yaml**: API contract maintains frontend compatibility
4. **quickstart.md**: Testing guide emphasizes TDD approach and unit/integration tests

### Constitutional Compliance Post-Design

#### I. Test-Driven Development (NON-NEGOTIABLE)
**Status**: ✅ PASS  
**Validation**: 
- Research document emphasizes test-first approach for each user story
- Quickstart provides TDD workflow examples (test → fail → implement → pass)
- Data model includes transformation functions ready for unit testing
- Integration test structure documented in quickstart

#### II. Testing Scope
**Status**: ✅ PASS  
**Validation**:
- Quickstart explicitly shows unit tests (services, handlers)
- Integration tests cover end-to-end flow (address → representatives)
- No e2e frameworks introduced
- Manual API testing with curl/Python for validation

#### III. Code Quality Gates
**Status**: ✅ PASS  
**Validation**:
- No new tools or exceptions required
- Existing pylint, black, pytest standards apply
- OpenAPI contract validates API structure
- Code review checklist in quickstart

#### IV. Incremental Development
**Status**: ✅ PASS  
**Validation**:
- Four priority-ordered user stories (P1-P4)
- Each story independently testable and deliverable
- Clear dependency chain (P1 → P2 → P3 → P4)
- Cleanup step (P4) only after validation of new flow

#### V. Serverless Architecture
**Status**: ✅ PASS  
**Validation**:
- Uses existing Lambda + API Gateway infrastructure (no new services)
- Parameter Store follows existing pattern (consistent with OpenStates key)
- No architectural changes, only service-layer additions
- Lambda timeout increased to 15s (well within limits)

#### VI. Accessible Information Design
**Status**: ✅ PASS  
**Validation**:
- API contract maintains existing frontend structure
- Response format unchanged (representatives grouped by level)
- Performance target maintained (<3 seconds)
- User-facing error messages clear and actionable

### Final Gate Decision

**✅ PROCEED TO IMPLEMENTATION**

All constitutional principles remain satisfied after Phase 1 design completion. No violations detected. Design artifacts demonstrate:
- Strong TDD foundation with comprehensive test plans
- Incremental, testable implementation approach
- Consistent architectural patterns
- Clear documentation for rapid onboarding

**Recommended Implementation Order**:
1. User Story 1 (P1): Google Maps geocoding
2. User Story 2 (P2): OpenStates geo endpoint
3. User Story 3 (P3): End-to-end integration
4. User Story 4 (P4): Legacy code cleanup

**Next Command**: `/speckit.tasks` to generate detailed task breakdown.

## Project Structure

### Documentation (this feature)

```text
specs/005-geolocation-lookup/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── address-lookup-api.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── handlers/
│   │   ├── api.py                  # MODIFY: Update AddressLookupHandler
│   │   └── address_lookup.py       # MODIFY: Replace with geolocation flow
│   ├── services/
│   │   ├── google_civic.py         # REMOVE: After migration complete (User Story 4)
│   │   ├── google_maps.py          # NEW: Google Maps Geocoding client
│   │   └── openstates.py           # MODIFY: Add geo endpoint method
│   ├── models/
│   │   ├── domain.py               # REVIEW: Ensure Representative model compatible
│   │   └── person.py               # REVIEW: Ensure Person model compatible
│   └── utils/
│       ├── validators.py           # MODIFY: Add address validation
│       └── parameter_store.py      # MODIFY: Add Google Maps API key retrieval
└── tests/
    ├── unit/
    │   ├── services/
    │   │   ├── test_google_maps.py           # NEW: Unit tests for geocoding
    │   │   └── test_openstates_geo.py        # NEW: Unit tests for geo endpoint
    │   └── handlers/
    │       └── test_address_lookup.py        # MODIFY: Update for new flow
    └── integration/
        └── test_address_to_reps.py           # NEW: End-to-end flow tests

frontend/
├── src/
│   └── (NO CHANGES - maintains contract compatibility)
└── tests/
    └── (NO CHANGES - existing tests should pass)

infrastructure/
└── stacks/
    └── (MODIFY: Update Lambda IAM role for Parameter Store access)
```

**Structure Decision**: Web application with backend/frontend split. Frontend requires no changes due to contract compatibility. Backend adds new GoogleMapsClient service, modifies existing AddressLookupHandler to use geolocation flow, and removes GoogleCivicClient after migration verification.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitutional principles satisfied.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       | N/A        | N/A                                 |
