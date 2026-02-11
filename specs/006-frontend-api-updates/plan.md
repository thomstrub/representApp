# Implementation Plan: Frontend API Integration Updates

**Branch**: `006-frontend-api-updates` | **Date**: 2026-02-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-frontend-api-updates/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Update the React/TypeScript frontend to consume the new nested API response structure from the backend. The backend now returns representatives pre-grouped by government level (federal, state, local) with enhanced metadata (resolved address, coordinates, total counts) and warnings array. This change eliminates client-side grouping logic and provides better context about the search results and data completeness.

## Technical Context

**Language/Version**: TypeScript 5.x with React 18.x  
**Primary Dependencies**: React, Material UI (MUI), React Hook Form, Zod (validation)  
**Storage**: N/A (state management via React hooks, no persistence)  
**Testing**: Jest + React Testing Library (unit & integration tests only)  
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)  
**Project Type**: Web application (frontend-only changes)  
**Performance Goals**: < 100ms to re-render after API response, < 1 second from API response to fully rendered UI  
**Constraints**: Must maintain backward compatibility with existing components, all existing tests must pass or be updated, no breaking changes to public component APIs  
**Scale/Scope**: ~4-6 components affected (ResultsDisplay, useRepresentatives hook, API types), ~10-15 test files to update, ~500-800 lines of code changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Test-Driven Development** | ✅ PASS | All changes will follow Red-Green-Refactor: write failing tests for new API structure, implement type updates, update component logic to pass tests, refactor while maintaining green |
| **II. Testing Scope** | ✅ PASS | Jest + React Testing Library for component tests, no e2e frameworks. Manual browser testing acceptable for final UI verification |
| **III. Code Quality Gates** | ✅ PASS | All existing tests must pass or be updated to reflect new API structure. ESLint must report no errors. TypeScript strict mode enabled with no type errors |
| **IV. Incremental Development** | ✅ PASS | Changes will be made incrementally: (1) Update types, (2) Update useRepresentatives hook, (3) Update ResultsDisplay component, (4) Add metadata/warnings display, (5) Update tests. Each step independently testable |
| **V. Serverless Architecture** | N/A | Frontend-only changes, no backend architecture modifications |
| **VI. Accessible Information Design** | ✅ PASS | Maintains existing accessibility (ARIA labels, semantic HTML). New features (resolved address, warnings) will be clearly presented with Material UI components. Representative grouping already implemented, just consuming pre-grouped data |

**Gate Status**: ✅ ALL APPLICABLE GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/006-frontend-api-updates/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api-response.schema.json
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── types/
│   │   ├── api.ts                    # UPDATE: New nested response structure
│   │   └── representative.ts         # NO CHANGE: Representative type stays same
│   ├── hooks/
│   │   └── useRepresentatives.ts     # UPDATE: Parse new nested response
│   ├── components/
│   │   ├── ResultsDisplay.tsx        # UPDATE: Remove client-side grouping, add metadata/warnings
│   │   ├── RepresentativeCard.tsx    # MINOR UPDATE: Ensure contact info displayed as links
│   │   ├── AddressForm.tsx           # NO CHANGE: Form stays same
│   │   └── LoadingIndicator.tsx      # NO CHANGE: Loading UI stays same
│   ├── utils/
│   │   └── grouping.ts               # REMOVE OR DEPRECATE: No longer needed (backend groups)
│   └── pages/
│       └── HomePage.tsx              # MINOR UPDATE: May need to pass metadata to ResultsDisplay
└── tests/
    ├── unit/
    │   ├── types/
    │   │   └── api.test.ts           # UPDATE: Test new type guards
    │   ├── hooks/
    │   │   └── useRepresentatives.test.ts  # UPDATE: Test new response parsing
    │   └── components/
    │       └── ResultsDisplay.test.tsx     # UPDATE: Test with pre-grouped data
    └── integration/
        └── HomePage.test.tsx         # UPDATE: Test full flow with new API structure
```

**Structure Decision**: Using existing Web application structure (Option 2 from template) with frontend/ directory. All changes are confined to frontend/ - no backend or infrastructure changes needed. The frontend already has proper separation of concerns (types, hooks, components, utils, pages) that supports this incremental update.

## Complexity Tracking

**No constitutional violations** - All applicable principles (I-IV, VI) are satisfied by this design. No justifications needed.

---

## Post-Design Constitution Re-Check

*Phase 1 Complete: Re-evaluating constitution compliance after design phase*

| Principle | Status | Post-Design Notes |
|-----------|--------|-------------------|
| **I. Test-Driven Development** | ✅ PASS | Quickstart guide provides explicit TDD workflow for each phase: write failing tests → implement → pass tests → refactor. All code changes documented with test-first approach |
| **II. Testing Scope** | ✅ PASS | Design uses Jest + React Testing Library exclusively. No e2e frameworks introduced. Manual browser testing documented for final verification |
| **III. Code Quality Gates** | ✅ PASS | Verification checklist in quickstart ensures: all tests pass, no TypeScript errors, no ESLint errors, conventional commits required |
| **IV. Incremental Development** | ✅ PASS | Implementation broken into 5 incremental phases: (1) Types, (2) Hook, (3) Component, (4) Integration, (5) Cleanup. Each phase independently testable and verifiable |
| **V. Serverless Architecture** | N/A | Frontend-only changes, no backend architecture modifications |
| **VI. Accessible Information Design** | ✅ PASS | Design maintains existing ARIA labels, adds semantic HTML (`<address>` tag), uses Material UI Alert for warnings with `role="alert"`, provides helpful empty states with clear guidance |

**Final Gate Status**: ✅ ALL APPLICABLE GATES PASS

**Design Changes from Initial Plan**: None - original approach validated through design phase.

**Risk Mitigation**: 
- Comprehensive test coverage documented (unit, integration, edge cases)
- Backward compatibility maintained (no breaking changes to public APIs)
- Performance improved (removes client-side grouping)
- Type safety enforced (TypeScript strict mode, type guards)
