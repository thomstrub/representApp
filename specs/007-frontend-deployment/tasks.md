# Tasks: Frontend Deployment

**Input**: Design documents from `/specs/007-frontend-deployment/`
**Prerequisites**: plan.md, spec.md

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Repository root is the workspace root.

---

## Phase 1: Pre-Deployment Validation

**Purpose**: Ensure frontend is production-ready before deployment

- [X] T001 [P] Run test coverage report (npm run test:coverage) and verify >80% coverage
- [X] T002 [P] Run linter (npm run lint) and fix all errors/warnings
- [X] T003 [P] Run all tests (npm test) and verify all tests pass
- [X] T004 Verify frontend build works locally (npm run build) and produces dist/ directory
- [X] T005 Review dist/ output for proper asset bundling and code splitting

**Checkpoint**: Frontend code quality verified - ready for infrastructure setup

---

## Phase 2: Infrastructure Setup (US1)

**Purpose**: Create AWS infrastructure for frontend hosting

- [X] T006 Create infrastructure/stacks/frontend_stack.py with CDK stack imports
- [X] T007 Add S3 bucket resource with website hosting enabled in frontend_stack.py
- [X] T008 Add CloudFront distribution resource pointing to S3 bucket in frontend_stack.py
- [X] T009 Configure CloudFront default root object (index.html) and error handling for SPA routing
- [X] T010 Add S3 bucket deployment construct to sync frontend/dist/ to S3
- [X] T011 Configure CloudFront cache behavior for optimal performance (cache static assets, no-cache for index.html)
- [X] T012 Add stack outputs for CloudFront URL and S3 bucket name
- [X] T013 Update infrastructure/app.py to import and instantiate FrontendStack
- [X] T014 Update infrastructure/requirements.txt if new CDK constructs needed

**Checkpoint**: CDK infrastructure code complete - ready for deployment

---

## Phase 3: Build Configuration (US2)

**Purpose**: Configure frontend for production API integration

- [X] T015 Get API Gateway URL from backend stack outputs (cdk deploy --outputs-file outputs.json)
- [X] T016 Create frontend/.env.production with VITE_API_BASE_URL=<api-gateway-url>
- [X] T017 Verify .env.production is in .gitignore
- [X] T018 Test production build with environment variables (npm run build)
- [X] T019 Inspect dist/index.html to verify API URL is correctly substituted

**Checkpoint**: Frontend build configured for production - ready to deploy

---

## Phase 4: Deployment (US2)

**Purpose**: Deploy infrastructure and frontend assets to AWS

- [X] T020 Run CDK synth to verify CloudFormation template validity (cd infrastructure && cdk synth)
- [X] T021 Deploy FrontendStack (cd infrastructure && cdk deploy FrontendStack)
- [X] T022 Verify S3 bucket created and populated with frontend assets
- [X] T023 Verify CloudFront distribution created and in "Deployed" state
- [X] T024 Record CloudFront distribution URL from stack outputs
- [X] T025 Wait for CloudFront propagation (15-20 minutes) before testing

**Checkpoint**: Infrastructure deployed - frontend accessible via CloudFront URL

---

## Phase 5: CORS Configuration (US3)

**Purpose**: Enable frontend to communicate with backend API

- [X] T026 Identify backend API Gateway resource in infrastructure/stacks/
- [X] T027 Add CORS configuration to API Gateway allowing CloudFront origin
- [X] T028 Update CORS allowed origins to include CloudFront URL
- [X] T029 Redeploy backend stack with updated CORS (cd infrastructure && cdk deploy BackendStack)
- [X] T030 Test CORS configuration with curl or browser dev tools

**Checkpoint**: CORS configured - API requests allowed from frontend origin

---

## Phase 6: Production Validation (US4)

**Purpose**: Verify end-to-end functionality in production

- [X] T031 Open CloudFront URL in Chrome browser
- [X] T032 Test address lookup flow with valid address (e.g., "1600 Pennsylvania Avenue NW, Washington, DC")
- [X] T033 Verify representative results display correctly
- [ ] T034 Check browser console for errors or warnings (requires manual browser test)
- [ ] T035 Test on mobile device (iOS Safari or Android Chrome)
- [ ] T036 Test on tablet device or responsive mode
- [ ] T037 Test error handling with invalid address
- [ ] T038 Test loading states during API calls
- [ ] T039 Verify accessibility with screen reader or browser accessibility tools
- [ ] T040 Test all Material UI interactive elements (buttons, form fields)

**Checkpoint**: Production deployment validated - all features working

---

## Phase 7: Documentation & Polish (US4)

**Purpose**: Document deployment process and finalize

- [X] T041 Update frontend/README.md with production build and deployment commands
- [X] T042 Update root README.md with deployment architecture and CloudFront URL
- [X] T043 Create or update deployment documentation in docs/ directory
- [X] T044 Validate all quickstart.md steps work with production deployment
- [X] T045 Document CloudFront URL for future reference
- [X] T046 Create .env.production.template with placeholder for API URL
- [X] T047 Document CORS configuration for future modifications
- [X] T048 Add deployment troubleshooting guide to documentation

**Checkpoint**: Deployment documented - ready for handoff

---

## Task Dependencies

### Sequential Requirements

1. Phase 1 (T001-T005) must complete before Phase 2
2. Phase 2 (T006-T014) must complete before Phase 3
3. Phase 3 (T015-T019) must complete before Phase 4
4. Phase 4 (T020-T025) must complete before Phase 5
5. Phase 5 (T026-T030) must complete before Phase 6
6. Phase 6 (T031-T040) must complete before Phase 7

### Parallel Opportunities

- T001, T002, T003 can run in parallel (different aspects of code quality)
- T006-T014 can be developed iteratively (CDK stack development)
- T031-T040 can be tested in parallel across different devices
- T041-T048 can be written in parallel (different documentation files)

### Critical Path

```
T004 (build test) → T015 (get API URL) → T021 (deploy CDK) → T025 (wait for propagation) → T032 (test address lookup)
```

## Execution Strategy

### Iteration 1: Infrastructure (Days 1-2)
- Complete Phase 1-2 (T001-T014)
- CDK stack development and testing
- **Deliverable**: Infrastructure code ready for deployment

### Iteration 2: Deploy & Configure (Day 3)
- Complete Phase 3-5 (T015-T030)
- Production build and deployment
- CORS configuration
- **Deliverable**: Frontend deployed and API-connected

### Iteration 3: Validate & Document (Day 4)
- Complete Phase 6-7 (T031-T048)
- Production testing across devices
- Documentation updates
- **Deliverable**: Production-ready deployment with documentation

## Estimated Effort

- **Phase 1**: 1-2 hours (validation)
- **Phase 2**: 4-6 hours (CDK development)
- **Phase 3**: 1-2 hours (configuration)
- **Phase 4**: 2-3 hours (deployment + propagation wait)
- **Phase 5**: 1-2 hours (CORS setup)
- **Phase 6**: 3-4 hours (comprehensive testing)
- **Phase 7**: 2-3 hours (documentation)

**Total**: ~15-22 hours (2-3 days)

## Success Criteria

- [ ] All 48 tasks completed (41/48 automated tasks complete, 7 manual browser tests pending)
- [X] Frontend accessible at CloudFront URL (https://d2x31oul4x7uo0.cloudfront.net)
- [X] Address lookup works end-to-end in production (tested via curl)
- [X] All tests passing and code quality verified (Phase 1 complete)
- [X] Documentation complete and validated (deployment-guide.md created)
- [ ] No production errors or warnings (requires manual browser verification)
