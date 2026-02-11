# Tasks: Frontend API Integration Updates

**Input**: Design documents from `/specs/006-frontend-api-updates/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-response.schema.json

**Tests**: Included - This project follows TDD principles with Jest + React Testing Library

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and validation

- [ ] T001 Checkout branch `006-frontend-api-updates` and run `cd frontend && npm install`
- [ ] T002 Verify existing frontend structure: types/, hooks/, components/, pages/, tests/
- [ ] T003 [P] Run initial test suite to confirm baseline: `npm test` (all existing tests should pass)

---

## Phase 2: User Story 1 - View Representatives Grouped by Government Level (Priority: P1) 🎯 MVP

**Goal**: Update frontend to consume pre-grouped API response structure (federal, state, local arrays) instead of flat array

**Independent Test**: Search for an address and verify representatives appear under "Federal", "State", and "Local" headings using pre-grouped data from backend

### Tests for User Story 1 (Write FIRST - Red Phase)

- [ ] T004 [P] [US1] Create test file for API types in frontend/tests/unit/types/api.test.ts with tests for GovernmentLevelGroup, ApiSuccessResponse, Coordinates, and isApiErrorResponse type guard
- [ ] T005 [P] [US1] Create tests for updated useRepresentatives hook in frontend/tests/unit/hooks/useRepresentatives.test.ts to verify parsing of nested representatives structure
- [ ] T006 [P] [US1] Create tests for updated ResultsDisplay component in frontend/tests/unit/components/ResultsDisplay.test.tsx to verify display of pre-grouped data
- [ ] T007 [P] [US1] Create integration tests for full flow in frontend/tests/integration/HomePage.test.tsx to verify end-to-end grouped display

### Implementation for User Story 1 (Green Phase)

- [ ] T008 [US1] Update TypeScript API types in frontend/src/types/api.ts to define GovernmentLevelGroup, Coordinates, Metadata, ApiSuccessResponse interfaces
- [ ] T009 [US1] Update useRepresentatives hook in frontend/src/hooks/useRepresentatives.ts to parse new nested response structure with representatives, metadata, warnings
- [ ] T010 [US1] Update ResultsDisplay component in frontend/src/components/ResultsDisplay.tsx to consume pre-grouped data directly (remove client-side grouping logic)
- [ ] T011 [US1] Update HomePage component in frontend/src/pages/HomePage.tsx to pass full ApiSuccessResponse to ResultsDisplay
- [ ] T012 [US1] Run all User Story 1 tests to verify they pass: `npm test -- tests/unit/types/ tests/unit/hooks/ tests/unit/components/ResultsDisplay tests/integration/HomePage`

**Checkpoint**: At this point, representatives should display in grouped sections (Federal, State, Local) using backend-provided grouping

---

## Phase 3: User Story 2 - Display Search Context and Warnings (Priority: P2)

**Goal**: Display resolved address, total counts from metadata, and warning messages when data is incomplete

**Independent Test**: Search for various addresses and verify resolved address displays, total count shows correctly, and warnings appear when present in API response

### Tests for User Story 2 (Write FIRST - Red Phase)

- [ ] T013 [P] [US2] Add tests for metadata display to frontend/tests/unit/components/ResultsDisplay.test.tsx to verify resolved address and total count render correctly
- [ ] T014 [P] [US2] Add tests for warnings display to frontend/tests/unit/components/ResultsDisplay.test.tsx to verify warning messages appear with Material UI Alert component
- [ ] T015 [P] [US2] Add tests for empty state to frontend/tests/unit/components/ResultsDisplay.test.tsx to verify helpful message when all government level arrays are empty
- [ ] T016 [P] [US2] Add integration tests to frontend/tests/integration/HomePage.test.tsx to verify metadata and warnings display in full flow

### Implementation for User Story 2 (Green Phase)

- [ ] T017 [US2] Add metadata display section to ResultsDisplay component in frontend/src/components/ResultsDisplay.tsx to show resolved address and total count
- [ ] T018 [US2] Add warnings display section to ResultsDisplay component in frontend/src/components/ResultsDisplay.tsx using Material UI Alert with severity="warning" and role="alert"
- [ ] T019 [US2] Add empty state display to ResultsDisplay component in frontend/src/components/ResultsDisplay.tsx to show helpful message when metadata.total_count is 0
- [ ] T020 [US2] Run all User Story 2 tests to verify they pass: `npm test -- tests/unit/components/ResultsDisplay tests/integration/HomePage`

**Checkpoint**: At this point, users should see resolved address, total counts, warning messages, and helpful empty states

---

## Phase 4: User Story 3 - View Representative Details with Jurisdiction (Priority: P3)

**Goal**: Ensure jurisdiction information displays clearly for each representative (likely already implemented, but verify and enhance)

**Independent Test**: View any representative card and verify jurisdiction label displays clearly (e.g., "California's 11th District", "United States")

### Tests for User Story 3 (Write FIRST - Red Phase)

- [ ] T021 [P] [US3] Add tests to frontend/tests/unit/components/RepresentativeCard.test.tsx to verify jurisdiction displays for federal, state, and local representatives
- [ ] T022 [P] [US3] Add tests to frontend/tests/unit/components/RepresentativeCard.test.tsx to verify contact info (email, phone, address, website) displays as clickable links with icons
- [ ] T023 [P] [US3] Add tests to frontend/tests/unit/components/RepresentativeCard.test.tsx to verify photo fallback (initials avatar) when photo_url is null
- [ ] T024 [P] [US3] Add edge case tests to frontend/tests/unit/components/RepresentativeCard.test.tsx for missing optional fields (no email, no phone, etc.)

### Implementation for User Story 3 (Green Phase)

- [ ] T025 [US3] Review and update RepresentativeCard component in frontend/src/components/RepresentativeCard.tsx to ensure jurisdiction displays prominently
- [ ] T026 [US3] Verify contact info rendering in frontend/src/components/RepresentativeCard.tsx to ensure clickable links with icons (email → mailto:, phone → tel:, website → opens in new tab)
- [ ] T027 [US3] Verify photo fallback in frontend/src/components/RepresentativeCard.tsx displays initials avatar when photo_url is null
- [ ] T028 [US3] Run all User Story 3 tests to verify they pass: `npm test -- tests/unit/components/RepresentativeCard`

**Checkpoint**: All user stories should now be independently functional with complete representative details

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, optimization, and final validation

- [ ] T029 [P] Remove deprecated grouping utility file frontend/src/utils/grouping.ts (no longer needed with backend grouping)
- [ ] T030 [P] Remove deprecated grouping utility test file frontend/tests/unit/utils/grouping.test.ts
- [ ] T031 Run full test suite to ensure all tests pass: `npm test`
- [ ] T032 Run TypeScript type check to ensure no type errors: `npm run type-check` or verify in IDE
- [ ] T033 Run ESLint to ensure no lint errors: `npm run lint`
- [ ] T034 [P] Update type exports in frontend/src/types/api.ts to ensure all new types are properly exported
- [ ] T035 Manual browser testing per quickstart.md validation checklist (address search, grouping, metadata, warnings, empty state)
- [ ] T036 Refactor ResultsDisplay component if needed (consider extracting metadata and warnings into separate components for better separation of concerns)
- [ ] T037 [P] Update frontend README.md with notes about new API structure if needed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Stories (Phase 2-4)**: 
  - **US1 (Phase 2)** can start immediately after Setup (Phase 1) - independent
  - **US2 (Phase 3)** depends on US1 completion (builds on ResultsDisplay changes)
  - **US3 (Phase 4)** is independent of US1/US2 (only updates RepresentativeCard) - can start after Phase 1
- **Polish (Phase 5)**: Depends on US1, US2, US3 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup (Phase 1) - No dependencies on other stories - BLOCKS US2
- **User Story 2 (P2)**: Depends on User Story 1 completion (extends ResultsDisplay component updated in US1)
- **User Story 3 (P3)**: Independent of US1/US2 - Can start after Setup (Phase 1) in parallel with US1

### Within Each User Story

- Tests MUST be written FIRST and FAIL before implementation (Red phase)
- Type definitions before hooks/components (US1)
- Hooks before components (US1)
- Core implementation before integration (all stories)
- All tests must pass before moving to next story (Green phase)

### Parallel Opportunities

**Phase 1 (Setup)**:
- All setup tasks can run sequentially (they're quick validation steps)

**Phase 2 (User Story 1 - Tests)**:
- T004, T005, T006, T007 can all be written in parallel (different test files, no dependencies)

**Phase 3 (User Story 2 - Tests)**:
- T013, T014, T015, T016 can all be written in parallel (different test sections/files)

**Phase 4 (User Story 3 - Tests)**:
- T021, T022, T023, T024 can all be written in parallel (same file but different test cases, no conflicts)

**Phase 5 (Polish)**:
- T029 and T030 can run in parallel (different files)
- T032, T033, T034 can run in parallel (different validation activities)
- T035, T037 can run in parallel (manual testing and documentation)

**Cross-Story Parallelization**:
- User Story 3 (Phase 4) can be worked on in parallel with User Story 1 (Phase 2) by a different developer
- Once US1 is complete, US2 can proceed while US3 continues (if not yet finished)

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together (write in parallel):
Task T004: "Create API types tests in frontend/tests/unit/types/api.test.ts"
Task T005: "Create hook tests in frontend/tests/unit/hooks/useRepresentatives.test.ts"
Task T006: "Create ResultsDisplay tests in frontend/tests/unit/components/ResultsDisplay.test.tsx"
Task T007: "Create integration tests in frontend/tests/integration/HomePage.test.tsx"

# Then run all tests at once to see them fail (Red phase)
npm test
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: User Story 1 (core grouping functionality)
3. **STOP and VALIDATE**: Test US1 independently with manual browser testing
4. Deploy/demo if ready

### Recommended Incremental Delivery

1. Complete Setup (Phase 1) → Project ready
2. Add User Story 1 (Phase 2) → Test independently → **MVP Complete! 🎉**
3. Add User Story 2 (Phase 3) → Test independently → Enhanced UX with metadata/warnings
4. Add User Story 3 (Phase 4) → Test independently → Complete feature with all details
5. Polish (Phase 5) → Production-ready

### Parallel Team Strategy

With 2 developers:

1. **Both complete Phase 1 together** → Setup done
2. **Split work**:
   - Developer A: User Story 1 (Phase 2) - CRITICAL PATH
   - Developer B: User Story 3 (Phase 4) - Independent work
3. **Once US1 complete**:
   - Developer A: User Story 2 (Phase 3) - Depends on US1
   - Developer B: Continue US3 or start Polish (Phase 5)
4. **Both complete Phase 5 together** → Final validation

---

## Validation Checklist (Before Committing)

Per quickstart.md and coding guidelines:

- [ ] All tests pass: `npm test` (shows green checkmarks)
- [ ] No TypeScript errors: `npm run type-check` or IDE shows no red squiggles
- [ ] No ESLint errors: `npm run lint` (reports 0 errors)
- [ ] Manual browser test completed:
  - [ ] Representatives grouped by federal/state/local
  - [ ] Resolved address displays correctly
  - [ ] Total count displays correctly
  - [ ] Warnings display when present (Material UI Alert with warning severity)
  - [ ] Empty state shows helpful message
  - [ ] Contact info displays as clickable links (email, phone, website)
  - [ ] Photo fallback (initials) works for reps without photos
  - [ ] Jurisdiction displays for each representative
- [ ] Conventional commit message prepared (e.g., `feat(frontend): update to consume nested API response structure`)
- [ ] Pushing to correct branch: `006-frontend-api-updates`

---

## Notes

- **[P] tasks**: Different files, no dependencies - can execute in parallel
- **[Story] label**: Maps task to specific user story (US1, US2, US3) for traceability
- **TDD workflow**: Write failing tests (Red) → Implement code (Green) → Refactor → Commit
- **Each user story**: Should be independently completable and testable
- **Stop at checkpoints**: Validate each story independently before proceeding
- **Commit frequently**: After each task or logical group of changes
- **File paths**: All paths relative to repository root (`frontend/src/...`, `frontend/tests/...`)
- **Validation**: Run full test suite between phases to catch regressions early

---

## Quick Reference: File Changes

| File | Change Type | User Stories | Description |
|------|-------------|--------------|-------------|
| `frontend/src/types/api.ts` | UPDATE | US1 | Add GovernmentLevelGroup, Metadata, Coordinates, ApiSuccessResponse interfaces |
| `frontend/src/hooks/useRepresentatives.ts` | UPDATE | US1 | Parse nested response with representatives, metadata, warnings |
| `frontend/src/components/ResultsDisplay.tsx` | UPDATE | US1, US2 | Consume pre-grouped data, add metadata/warnings display |
| `frontend/src/components/RepresentativeCard.tsx` | VERIFY/UPDATE | US3 | Ensure jurisdiction, contact info, photo fallback display correctly |
| `frontend/src/pages/HomePage.tsx` | MINOR UPDATE | US1 | Pass full ApiSuccessResponse to ResultsDisplay |
| `frontend/src/utils/grouping.ts` | DELETE | Polish | Remove deprecated client-side grouping utility |
| `frontend/tests/unit/types/api.test.ts` | CREATE | US1 | Test new API types and type guards |
| `frontend/tests/unit/hooks/useRepresentatives.test.ts` | UPDATE | US1 | Test nested response parsing |
| `frontend/tests/unit/components/ResultsDisplay.test.tsx` | UPDATE | US1, US2 | Test grouped display, metadata, warnings |
| `frontend/tests/unit/components/RepresentativeCard.test.tsx` | UPDATE | US3 | Test jurisdiction, contact info, photo fallback |
| `frontend/tests/integration/HomePage.test.tsx` | UPDATE | US1, US2 | Test full flow with new API structure |
| `frontend/tests/unit/utils/grouping.test.ts` | DELETE | Polish | Remove deprecated test file |

---

## Summary

- **Total Tasks**: 37 across 5 phases
- **Phase 1 (Setup)**: 3 tasks - Project validation
- **Phase 2 (User Story 1)**: 9 tasks - Core grouping functionality
- **Phase 3 (User Story 2)**: 8 tasks - Metadata and warnings
- **Phase 4 (User Story 3)**: 8 tasks - Jurisdiction and contact details
- **Phase 5 (Polish)**: 9 tasks - Cleanup and validation
- **Parallel Opportunities**: 15 tasks marked [P] can execute in parallel
- **Independent Tests**: Each user story has clear acceptance criteria
- **MVP Scope**: Phases 1-2 only (User Story 1) - View representatives grouped by government level

**Estimated Effort**: 3-4 hours for MVP (Phases 1-2), 6-8 hours for complete feature (all phases)
