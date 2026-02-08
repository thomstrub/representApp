<!--
Sync Impact Report:
- Version: INITIAL → 1.0.0 (initial ratification)
- Principles established: 6 core principles derived from project documentation
- Templates status:
  ✅ plan-template.md - Constitution Check section aligns with principles
  ✅ spec-template.md - User story format compatible with TDD approach
  ✅ tasks-template.md - Task categorization reflects principle-driven development
  ⚠ Command files - Will need review for agent-specific references
- Follow-up: None (all placeholders filled from existing documentation)
-->

# Represent App Constitution

## Core Principles

### I. Test-Driven Development (NON-NEGOTIABLE)

All code MUST follow the Red-Green-Refactor cycle:
- Write failing tests FIRST that describe expected behavior
- Run tests and verify they FAIL (Red phase)
- Implement minimal code to make tests pass (Green phase)
- Refactor while maintaining passing tests (Refactor phase)
- One feature or fix at a time, each independently verifiable

**Rationale**: TDD ensures code correctness, prevents regressions, and creates
living documentation through tests. This discipline is foundational to
delivering reliable civic infrastructure.

### II. Testing Scope

Testing MUST use unit tests and integration tests ONLY:
- Backend: pytest with moto for AWS service mocks
- Frontend: Jest + React Testing Library for components
- Integration: API Gateway → Lambda → DynamoDB flows
- Manual browser testing for UI verification is acceptable

Testing MUST NOT include:
- End-to-end test frameworks (Playwright, Cypress, Selenium)
- Browser automation tools
- Full browser testing pipelines

**Rationale**: Focused testing scope maintains lab simplicity while ensuring
quality. Manual UI verification is sufficient without e2e complexity.

### III. Code Quality Gates

All code MUST pass quality gates before commit:
- All tests pass (pytest for backend, npm test for frontend)
- No lint errors or warnings (pylint, eslint)
- Code follows project coding standards
- Conventional commit message format used
- Pushing to correct feature branch

Code quality tools MUST be configured:
- Python: pylint, black (formatting), pytest-cov (coverage >80%)
- JavaScript: ESLint, Prettier (formatting)

**Rationale**: Quality gates prevent technical debt accumulation and ensure
consistent codebase maintainability across the team.

### IV. Incremental Development

Development MUST proceed in small, testable steps:
- Make one change at a time
- Each change independently verifiable
- Commit working code frequently
- Feature branches for all non-trivial changes

Systematic debugging MUST guide fixes:
- Read error messages carefully
- Reproduce issues with tests first
- Fix root causes, not symptoms
- Validate fixes with tests

**Rationale**: Incremental changes reduce risk, simplify debugging, and enable
frequent integration without destabilizing the codebase.

### V. Serverless Architecture

Infrastructure MUST follow serverless patterns:
- AWS Lambda for compute (Python 3.9+)
- API Gateway HTTP v2 for REST endpoints
- DynamoDB for data persistence with multi-tenancy
- AWS CDK for Infrastructure as Code
- CloudWatch for logging, X-Ray for tracing

Multi-tenancy MUST use Lambda tenant isolation mode:
- State/county as tenant identifiers
- Execution environments never shared across tenants
- Tenant-specific data cached in memory remains isolated

**Rationale**: Serverless architecture provides scalability, reduces operational
overhead, and aligns with cloud-native best practices for civic applications.

### VI. Accessible Information Design

Application MUST prioritize citizen accessibility:
- Political information in plain, digestible language
- No dense legal jargon in user-facing content
- Location-based queries (zip code) for representative discovery
- Clear categorization by government level (federal, state, local)
- Response times <3 seconds for lookups

Data presentation MUST be hierarchical:
- Most relevant to least relevant based on user location
- Clear indication of data source and freshness
- Contact information easily accessible (email, phone, address)

**Rationale**: The mission is bridging the gap between political infrastructure
and constituents. Information must be as accessible to citizens as it is to
lobbyists.

## Technology Standards

**Backend Stack**:
- Runtime: Python 3.9+
- Framework: AWS Lambda Powertools (Logger, Tracer, Validator)
- API: HTTP API Gateway v2 with Lambda proxy integration
- Database: DynamoDB with on-demand billing
- Testing: pytest, moto, pytest-cov

**Frontend Stack** (when implemented):
- Framework: React with React DOM
- UI Library: Material UI (MUI) for components
- Testing: Jest, React Testing Library
- CSS for styling

**Infrastructure**:
- IaC: AWS CDK (Python)
- Deployment: CDK deploy from infrastructure/
- Environment: .env files for configuration (never committed)

**External APIs**:
- Google Civic Information API (Primary - MVP)
- ProPublica Congress API (Post-MVP - voting records)
- OpenStates API (Post-MVP - state legislature)

## Development Workflow

**Branch Strategy**:
- Feature branches: `feature/<descriptive-name>`
- Bug fixes: `fix/<descriptive-name>`
- Documentation: `docs/<descriptive-name>`
- Refactoring: `refactor/<descriptive-name>`

**Commit Format** (Conventional Commits):
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Code Review Requirements**:
- All changes via pull requests
- Review for clarity, maintainability, and guideline adherence
- Address feedback promptly and respectfully
- No merge without passing CI checks

**Deployment Process**:
1. Run tests locally: `make test`
2. Run linter: `make lint`
3. Deploy infrastructure: `cd infrastructure && cdk deploy`
4. Verify deployment via health check endpoint

## Governance

This constitution supersedes all other practices and guidelines. All development
decisions MUST align with these principles.

**Amendment Process**:
- Amendments require documented justification
- Version number MUST increment per semantic versioning:
  - MAJOR: Backward incompatible governance changes or principle removals
  - MINOR: New principles added or materially expanded guidance
  - PATCH: Clarifications, wording fixes, non-semantic refinements
- Constitution changes MUST be propagated to dependent templates
- All team members MUST be notified of amendments

**Compliance**:
- All PRs MUST verify constitutional compliance
- Complexity deviations MUST be justified with rationale
- Memory system (`.github/memory/`) tracks patterns and decisions
- Runtime guidance in `.github/copilot-instructions.md`

**Review Cycle**:
- Constitution reviewed quarterly for relevance
- Outdated principles retired with migration plans
- New patterns from session notes promoted to principles when proven

**Version**: 1.0.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07
