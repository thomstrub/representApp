# Tasks: Address Lookup Web Interface

**Input**: Design documents from `/specs/004-address-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md, github-research.md (prerequisite - already complete)

**Tests**: TDD approach required per constitution - tests included for all user stories

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with frontend/ at repository root

---

## Phase 1: Setup (Shared Infrastructure) ✅

**Purpose**: Project initialization and basic structure

- [X] T001 Create Vite project with React + TypeScript template in frontend/
- [X] T002 Install Material UI dependencies (@mui/material, @emotion/react, @emotion/styled, @mui/icons-material) in frontend/
- [X] T003 [P] Install React Hook Form and Zod (react-hook-form, @hookform/resolvers, zod) in frontend/
- [X] T004 [P] Install Vitest and React Testing Library (@testing-library/react, @testing-library/jest-dom, @testing-library/user-event, vitest, jsdom, @vitest/ui) in frontend/
- [X] T005 [P] Configure ESLint and Prettier for code quality in frontend/
- [X] T006 Configure Vitest in frontend/vite.config.ts with jsdom environment and setupFiles
- [X] T007 Create frontend/src/setupTests.ts to import @testing-library/jest-dom
- [X] T008 Create directory structure: frontend/src/components, frontend/src/pages, frontend/src/hooks, frontend/src/types, frontend/src/utils, frontend/tests/components, frontend/tests/integration, frontend/tests/utils
- [X] T009 Update frontend/package.json scripts for dev, build, test, test:coverage, lint
- [X] T010 Create frontend/.env with VITE_API_BASE_URL placeholder (add to .gitignore)

---

## Phase 2: Foundational (Blocking Prerequisites) ✅

**Purpose**: Core TypeScript types and infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 [P] Create Representative interface in frontend/src/types/representative.ts
- [X] T012 [P] Create AddressFormData type and Zod schema in frontend/src/types/form.ts
- [X] T013 [P] Create AppState discriminated union type with type guards in frontend/src/types/state.ts
- [X] T014 [P] Create API response types (ApiSuccessResponse, ApiErrorResponse) in frontend/src/types/api.ts
- [X] T015 [P] Create groupByGovernmentLevel helper function in frontend/src/utils/grouping.ts
- [X] T016 [P] Create getErrorMessage helper function in frontend/src/utils/errors.ts
- [X] T017 [P] Write unit test for groupByGovernmentLevel in frontend/tests/utils/grouping.test.ts
- [X] T018 [P] Write unit test for getErrorMessage in frontend/tests/utils/errors.test.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 1 - Address Entry and Representative Lookup (Priority: P1) 🎯 MVP

**Goal**: User can enter address, submit form, and see representatives grouped by government level

**Independent Test**: Load web page, enter "123 Main St, Seattle, WA 98101", click submit, verify representatives appear in Federal/State/Local sections

### Tests for User Story 1 (TDD - Write FIRST, ensure FAIL) ✅

- [X] T019 [P] [US1] Write test for useRepresentatives hook (idle → loading → success states) in frontend/tests/hooks/useRepresentatives.test.ts
- [X] T020 [P] [US1] Write test for AddressForm validation and submit in frontend/tests/components/AddressForm.test.tsx
- [X] T021 [P] [US1] Write test for RepresentativeCard with required and optional fields in frontend/tests/components/RepresentativeCard.test.tsx
- [X] T022 [P] [US1] Write test for ResultsDisplay grouping by government level in frontend/tests/components/ResultsDisplay.test.tsx
- [X] T023 [US1] Write integration test for complete flow (form → loading → results) in frontend/tests/integration/AddressLookup.test.tsx

### Implementation for User Story 1 ✅

- [X] T024 [US1] Implement useRepresentatives hook in frontend/src/hooks/useRepresentatives.ts (fetchByAddress, clearResults, appState management)
- [X] T025 [P] [US1] Implement AddressForm component in frontend/src/components/AddressForm.tsx (React Hook Form + Zod validation, onSubmit prop, disabled state)
- [X] T026 [P] [US1] Implement RepresentativeCard component in frontend/src/components/RepresentativeCard.tsx (MUI Card, Avatar with photo/initials, contact fields, website link)
- [X] T027 [P] [US1] Implement LoadingIndicator component in frontend/src/components/LoadingIndicator.tsx (MUI CircularProgress, centered message)
- [X] T028 [US1] Implement ResultsDisplay component in frontend/src/components/ResultsDisplay.tsx (group by government level, vertically stacked sections with headers, MUI Grid for responsive cards)
- [X] T029 [US1] Implement HomePage component in frontend/src/pages/HomePage.tsx (integrates AddressForm, useRepresentatives hook, LoadingIndicator, ResultsDisplay, state-driven rendering)
- [X] T030 [US1] Update frontend/src/App.tsx to render HomePage component
- [X] T031 [US1] Verify all User Story 1 tests pass

**Checkpoint**: At this point, User Story 1 should be fully functional - users can lookup representatives by address ✅

---

## Phase 4: User Story 2 - Input Validation and Error Handling (Priority: P2)

**Goal**: User gets helpful feedback for invalid inputs and clear error messages for API failures

**Independent Test**: Enter empty address → see validation error on blur/submit; simulate API 404 → see user-friendly error message

### Tests for User Story 2 (TDD - Write FIRST, ensure FAIL)

- [ ] T032 [P] [US2] Write test for empty address validation (blur and submit triggers) in frontend/tests/components/AddressForm.test.tsx
- [ ] T033 [P] [US2] Write test for address exceeding 200 characters validation in frontend/tests/components/AddressForm.test.tsx
- [ ] T034 [P] [US2] Write test for invalid zip code format validation in frontend/tests/components/AddressForm.test.tsx
- [ ] T035 [P] [US2] Write test for ErrorMessage component display in frontend/tests/components/ErrorMessage.test.tsx
- [ ] T036 [P] [US2] Write test for useRepresentatives hook error state handling (404, 500, 503) in frontend/tests/hooks/useRepresentatives.test.ts
- [ ] T037 [US2] Write integration test for validation preventing submission in frontend/tests/integration/Validation.test.tsx
- [ ] T038 [US2] Write integration test for API error displaying error message in frontend/tests/integration/ErrorHandling.test.tsx

### Implementation for User Story 2

- [ ] T039 [US2] Enhance Zod schema in frontend/src/types/form.ts with zip code regex validation
- [ ] T040 [US2] Update AddressForm in frontend/src/components/AddressForm.tsx to show validation errors on blur (mode: 'onBlur')
- [ ] T041 [US2] Implement ErrorMessage component in frontend/src/components/ErrorMessage.tsx (user-friendly error display, optional retry button)
- [ ] T042 [US2] Update getErrorMessage in frontend/src/utils/errors.ts to map HTTP status codes (400, 404, 500, 503) to user-friendly messages
- [ ] T043 [US2] Update HomePage in frontend/src/pages/HomePage.tsx to render ErrorMessage component when appState.status === 'error'
- [ ] T044 [US2] Add error state handling to useRepresentatives hook in frontend/src/hooks/useRepresentatives.ts (catch network errors, map API errors)
- [ ] T045 [US2] Verify all User Story 2 tests pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - validation and error handling are robust

---

## Phase 5: User Story 3 - Responsive Design Across Devices (Priority: P2)

**Goal**: Application adapts layout for desktop (≥1024px), tablet (768-1023px), and mobile (<768px) screen widths

**Independent Test**: Open application at 1920x1080, 768x1024, 375x667 → verify layout adjusts appropriately without horizontal scrolling

### Tests for User Story 3 (TDD - Write FIRST, ensure FAIL)

- [ ] T046 [P] [US3] Write test for HomePage responsive layout at desktop breakpoint in frontend/tests/components/HomePage.test.tsx
- [ ] T047 [P] [US3] Write test for ResultsDisplay responsive grid at mobile/tablet/desktop in frontend/tests/components/ResultsDisplay.test.tsx
- [ ] T048 [P] [US3] Write test for AddressForm full-width inputs on mobile in frontend/tests/components/AddressForm.test.tsx
- [ ] T049 [US3] Write integration test for responsive behavior at different viewport sizes in frontend/tests/integration/Responsive.test.tsx

### Implementation for User Story 3

- [ ] T050 [P] [US3] Add MUI responsive Grid configuration to ResultsDisplay in frontend/src/components/ResultsDisplay.tsx (xs=12, sm=6, md=4)
- [ ] T051 [P] [US3] Add responsive MUI Container to HomePage in frontend/src/pages/HomePage.tsx with maxWidth constraints
- [ ] T052 [P] [US3] Ensure AddressForm uses fullWidth prop on TextField in frontend/src/components/AddressForm.tsx
- [ ] T053 [P] [US3] Add responsive padding/margins to RepresentativeCard in frontend/src/components/RepresentativeCard.tsx
- [ ] T054 [US3] Test application manually at breakpoints: 375px (mobile), 768px (tablet), 1024px (desktop), 1920px (large desktop)
- [ ] T055 [US3] Verify all User Story 3 tests pass

**Checkpoint**: All layout breakpoints should work correctly - application is responsive across devices

---

## Phase 6: User Story 4 - Application Accessibility (Priority: P3)

**Goal**: Application meets WCAG AA standards with keyboard navigation, screen reader compatibility, and color contrast

**Independent Test**: Navigate entire application using only keyboard (Tab, Enter); test with screen reader (VoiceOver/NVDA); verify color contrast ratios

### Tests for User Story 4 (TDD - Write FIRST, ensure FAIL)

- [ ] T056 [P] [US4] Write test for keyboard navigation through AddressForm (Tab through input → button) in frontend/tests/components/AddressForm.test.tsx
- [ ] T057 [P] [US4] Write test for ARIA labels on AddressForm input and button in frontend/tests/components/AddressForm.test.tsx
- [ ] T058 [P] [US4] Write test for screen reader announcements on ErrorMessage in frontend/tests/components/ErrorMessage.test.tsx
- [ ] T059 [P] [US4] Write test for RepresentativeCard ARIA region label in frontend/tests/components/RepresentativeCard.test.tsx
- [ ] T060 [P] [US4] Write test for focus management when results appear in frontend/tests/integration/Accessibility.test.tsx
- [ ] T061 [US4] Write test for visible focus indicators on all interactive elements in frontend/tests/components/HomePage.test.tsx

### Implementation for User Story 4

- [ ] T062 [P] [US4] Add ARIA labels to AddressForm input and button in frontend/src/components/AddressForm.tsx
- [ ] T063 [P] [US4] Add ARIA live region to ErrorMessage for screen reader announcements in frontend/src/components/ErrorMessage.tsx
- [ ] T064 [P] [US4] Add ARIA region with label to RepresentativeCard in frontend/src/components/RepresentativeCard.tsx
- [ ] T065 [P] [US4] Ensure website links in RepresentativeCard have rel="noopener noreferrer" in frontend/src/components/RepresentativeCard.tsx
- [ ] T066 [US4] Add focus management to HomePage (move focus to results section) in frontend/src/pages/HomePage.tsx
- [ ] T067 [US4] Configure MUI theme for sufficient color contrast (WCAG AA 4.5:1) in frontend/src/App.tsx
- [ ] T068 [US4] Run Lighthouse accessibility audit and fix any critical violations
- [ ] T069 [US4] Test manually with keyboard navigation (Tab, Enter, Escape)
- [ ] T070 [US4] Test manually with screen reader (VoiceOver on macOS or NVDA on Windows)
- [ ] T071 [US4] Verify all User Story 4 tests pass

**Checkpoint**: All user stories should now be independently functional with full accessibility support

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final deployment

- [ ] T072 [P] Add "Clear" button to AddressForm in frontend/src/components/AddressForm.tsx (clears input but keeps results visible)
- [ ] T073 [P] Add "Search another address" button below ResultsDisplay in frontend/src/pages/HomePage.tsx (triggers new search flow)
- [ ] T074 [P] Add form state persistence so entered address remains visible during loading in frontend/src/components/AddressForm.tsx
- [ ] T075 [P] Prevent multiple simultaneous submissions by disabling button during loading in frontend/src/components/AddressForm.tsx
- [ ] T076 [P] Add timeout handling (30 seconds) to useRepresentatives hook with AbortController in frontend/src/hooks/useRepresentatives.ts
- [ ] T077 [P] Add frontend README.md with setup instructions, development commands, testing guide
- [ ] T078 [P] Update repository root README.md to document frontend directory and deployment
- [ ] T079 Code cleanup and refactoring across all components
- [ ] T080 Run test coverage report (npm run test:coverage) and verify >80% coverage
- [ ] T081 Run linter (npm run lint) and fix all errors/warnings
- [ ] T082 Create infrastructure/stacks/frontend_stack.py for S3 + CloudFront deployment
- [ ] T083 Test frontend build (npm run build) and verify dist/ output
- [ ] T084 Deploy frontend to S3 + CloudFront using CDK (cdk deploy FrontendStack)
- [ ] T085 Configure CORS on backend API Gateway to allow frontend origin
- [ ] T086 Update frontend .env.production with production API Gateway URL
- [ ] T087 Test production deployment with real addresses from multiple devices
- [ ] T088 Run quickstart.md validation and verify all steps work correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ MVP
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 layout but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 accessibility but independently testable

### Within Each User Story (TDD Workflow)

1. Write tests FIRST (all [P] tests can be written in parallel)
2. Run tests → Verify they FAIL (Red phase)
3. Implement components/hooks ([P] tasks within story can be done in parallel where noted)
4. Run tests → Verify they PASS (Green phase)
5. Refactor code while keeping tests green (Refactor phase)
6. Story complete → Move to next priority

### Parallel Opportunities

**Phase 1 - Setup**: T002, T003, T004, T005 can run in parallel (different dependency installations)

**Phase 2 - Foundational**: T011, T012, T013, T014, T015, T016 can run in parallel (different files), then T017, T018 can run in parallel

**Phase 3 - US1 Tests**: T019, T020, T021, T022 can be written in parallel (different test files)

**Phase 3 - US1 Implementation**: T025, T026, T027 can run in parallel (different component files)

**Phase 4 - US2 Tests**: T032, T033, T034, T035, T036 can be written in parallel

**Phase 5 - US3 Implementation**: T050, T051, T052, T053 can run in parallel (different component updates)

**Phase 6 - US4 Tests**: T056, T057, T058, T059, T060 can be written in parallel

**Phase 6 - US4 Implementation**: T062, T063, T064, T065 can run in parallel (different component updates)

**Phase 7 - Polish**: T072, T073, T074, T075, T076, T077, T078 can run in parallel (different features/files)

**Cross-Story Parallelism** (if multiple developers):
- Once Foundational (Phase 2) completes:
  - Developer A: User Story 1 (Phase 3)
  - Developer B: User Story 2 (Phase 4)
  - Developer C: User Story 3 (Phase 5)
  - Developer D: User Story 4 (Phase 6)

---

## Parallel Example: User Story 1

```bash
# Write all tests for User Story 1 together (Red phase):
T019: "Write test for useRepresentatives hook in frontend/tests/hooks/useRepresentatives.test.ts"
T020: "Write test for AddressForm in frontend/tests/components/AddressForm.test.tsx"
T021: "Write test for RepresentativeCard in frontend/tests/components/RepresentativeCard.test.tsx"
T022: "Write test for ResultsDisplay in frontend/tests/components/ResultsDisplay.test.tsx"

# Launch all parallel US1 components together (Green phase):
T025: "Implement AddressForm component in frontend/src/components/AddressForm.tsx"
T026: "Implement RepresentativeCard component in frontend/src/components/RepresentativeCard.tsx"
T027: "Implement LoadingIndicator component in frontend/src/components/LoadingIndicator.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) 🎯

1. Complete Phase 1: Setup (~1-2 hours)
2. Complete Phase 2: Foundational (~2-3 hours)
3. Complete Phase 3: User Story 1 (~1-2 days)
4. **STOP and VALIDATE**: Test US1 independently with real addresses
5. Deploy to S3 + CloudFront (T082-T087)
6. Demo MVP to stakeholders

**MVP Deliverable**: Users can enter address and see their representatives grouped by government level

---

### Incremental Delivery

1. **Iteration 1**: Setup + Foundational → Foundation ready (~0.5 day)
2. **Iteration 2**: Add User Story 1 → Test independently → Deploy/Demo (~2 days) **🎯 MVP COMPLETE**
3. **Iteration 3**: Add User Story 2 → Test independently → Deploy/Demo (~1 day) - Robust validation/errors
4. **Iteration 4**: Add User Story 3 → Test independently → Deploy/Demo (~1 day) - Responsive design
5. **Iteration 5**: Add User Story 4 → Test independently → Deploy/Demo (~1-2 days) - Accessibility
6. **Iteration 6**: Polish + Final Deployment (~0.5-1 day)

**Total Estimated Time**: 6-8 days for full feature with all user stories

---

### Parallel Team Strategy

With 2-3 developers (after Foundational phase):

**Week 1**:
- Developer A: User Story 1 (P1) - MVP
- Developer B: User Story 2 (P2) - Validation
- Developer C: Setup infrastructure for S3 + CloudFront

**Week 2**:
- Developer A: User Story 3 (P2) - Responsive
- Developer B: User Story 4 (P3) - Accessibility
- Developer C: Polish + Deployment

**Benefit**: All user stories complete in ~2 weeks with parallel development

---

## Test Coverage Targets

| Component/Hook | Target Coverage | Priority |
|----------------|-----------------|----------|
| useRepresentatives | >90% | P1 (MVP) |
| AddressForm | >90% | P1 (MVP) |
| RepresentativeCard | >85% | P1 (MVP) |
| ResultsDisplay | >85% | P1 (MVP) |
| ErrorMessage | >80% | P2 |
| LoadingIndicator | >75% | P1 (MVP) |
| HomePage | >80% | P1 (MVP) |
| Utility functions | >95% | Foundational |

**Overall Target**: >80% coverage (per constitution)

---

## Manual Testing Checklist

After automated tests pass, perform manual testing:

### MVP (User Story 1)
- [ ] Load application at http://localhost:5173
- [ ] Enter valid address "1600 Pennsylvania Ave NW, Washington, DC 20500"
- [ ] Click submit → Verify loading indicator appears
- [ ] Verify Federal representatives appear (President, Senators, House member)
- [ ] Verify State representatives appear (DC officials)
- [ ] Verify representative cards show name, office, party, contact info, photo/initials

### Validation (User Story 2)
- [ ] Leave address field empty → Click submit → Verify validation error
- [ ] Enter "123" → Blur field → Verify validation error
- [ ] Enter 201-character address → Verify validation error
- [ ] Enter fake address "123 Nonexistent St" → Verify user-friendly 404 error

### Responsive (User Story 3)
- [ ] Resize browser to 375px width → Verify mobile layout (single column)
- [ ] Resize browser to 768px width → Verify tablet layout (2 columns)
- [ ] Resize browser to 1920px width → Verify desktop layout (3 columns)
- [ ] Verify no horizontal scrolling at any breakpoint

### Accessibility (User Story 4)
- [ ] Tab through form → Verify focus indicators visible
- [ ] Submit with keyboard (Enter on button) → Verify works
- [ ] Test with VoiceOver/NVDA → Verify all elements announced correctly
- [ ] Run Lighthouse audit → Verify >90 accessibility score

### Production
- [ ] Deploy to S3 + CloudFront
- [ ] Test from multiple devices (iPhone, Android, Desktop)
- [ ] Test from multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Verify HTTPS certificate works
- [ ] Verify CORS allows API calls from frontend domain

---

## Notes

- **[P] tasks** = different files, no dependencies within phase
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD workflow**: Write tests FIRST (Red) → Implement (Green) → Refactor (Refactor)
- Verify tests fail before implementing (Red phase is critical)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **Test early, test often**: Run `npm test` frequently during development
- **Coverage monitoring**: Run `npm run test:coverage` before committing

---

## Success Metrics

### Development Metrics
- ✅ All tests pass with >80% coverage
- ✅ ESLint reports 0 errors, 0 warnings
- ✅ TypeScript compilation with 0 errors
- ✅ Lighthouse accessibility score >90
- ✅ Lighthouse performance score >80

### User Metrics (from spec.md)
- ✅ Complete lookup flow <5 seconds on broadband
- ✅ Initial load <2 seconds on 3G
- ✅ Loading indicator appears <100ms
- ✅ Error messages display <500ms
- ✅ 95% of valid addresses return results
- ✅ Works on Chrome, Firefox, Safari, Edge (latest versions)

---

## Deployment Checklist

Before production deployment:

- [ ] All Phase 7 tasks complete
- [ ] Test coverage >80%
- [ ] All linter errors resolved
- [ ] Manual testing checklist complete
- [ ] Backend API accessible via HTTPS
- [ ] CORS configured on backend
- [ ] S3 bucket and CloudFront distribution created (CDK)
- [ ] Frontend .env.production configured with production API URL
- [ ] Build succeeds: `npm run build`
- [ ] Preview works: `npm run preview`
- [ ] Deploy infrastructure: `cdk deploy FrontendStack`
- [ ] Sync build to S3: `aws s3 sync dist/ s3://bucket-name/`
- [ ] Invalidate CloudFront cache
- [ ] Test production URL from multiple devices/browsers
- [ ] Monitor CloudWatch for errors
- [ ] Document production URL in README.md

---

**Total Tasks**: 88 tasks
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 8 tasks
- Phase 3 (US1 - MVP): 13 tasks (5 tests + 8 implementation)
- Phase 4 (US2): 14 tasks (7 tests + 7 implementation)
- Phase 5 (US3): 10 tasks (4 tests + 6 implementation)
- Phase 6 (US4): 16 tasks (6 tests + 10 implementation)
- Phase 7 (Polish): 17 tasks

**MVP Task Count**: 31 tasks (Phase 1 + Phase 2 + Phase 3)
**Full Feature Task Count**: 88 tasks (all phases)

**Estimated Timeline**:
- MVP only: 2-3 days (1 developer)
- Full feature: 6-8 days (1 developer) or 2 weeks (3 developers in parallel)
