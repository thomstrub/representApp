# GitHub Copilot Instructions

> **Note**: This file is located at `.github/copilot-instructions.md` and is used by GitHub Copilot to understand project context.

This file contains high-level instructions for GitHub Copilot to follow when generating code for this project. For detailed guidance, refer to the documentation files in the `docs/` directory.

## Project Context

#file:project-overview.md

Represent App is a full-stack serverless application designed to bridge the gap between political infrastructure and constituents' day-to-day lives. The application helps citizens find, contact, and track their local, state, and federal representatives using a modern cloud-native architecture.

**Key Architecture:**
- **Frontend**: React-based SPA with Material UI (future: map-based interface)
- **Backend**: Python 3.9 Lambda handlers with AWS Lambda Powertools
- **API**: HTTP API Gateway v2 for RESTful endpoints
- **Database**: DynamoDB with multi-tenancy support
- **Infrastructure**: AWS CDK for Infrastructure as Code
- **Location Services**: Zip code-based queries for finding representatives

**Technology Stack:**
- Backend: Python 3.9, AWS Lambda Powertools, pytest
- Frontend: React, Material UI, Jest, React Testing Library
- Infrastructure: AWS CDK (Python), DynamoDB, API Gateway, CloudWatch

**Current Phase**: Phase 2 - Design Research Implementation
- Implementing Google Civic Information API integration
- Designing DynamoDB multi-tenant schema
- Building OCD Division ID parsing
- Implementing multi-layer caching strategy

## Documentation References

The project documentation provides detailed guidance for all aspects of development:

- [Project Overview](../docs/project-overview.md) - Architecture and technology stack
- [Functional Requirements](../docs/functional-requirements.md) - Core functional requirements
- [UI Guidelines](../docs/ui-guidelines.md) - Material UI component standards
- [Testing Guidelines](../docs/testing-guidelines.md) - Testing principles and requirements
- [Coding Guidelines](../docs/coding-guidelines.md) - Code style and quality standards

## Interaction Guidelines

- Do not make assumptions about requirements
- Prompt for clarifications when necessary
- Follow the coding style and conventions outlined in the documentation
- Reference documentation links when providing guidance

## Development Principles

This project follows strict engineering discipline:

1. **Test-Driven Development**: Follow the Red-Green-Refactor cycle
   - Write failing tests FIRST (Red)
   - Implement minimal code to pass tests (Green)
   - Refactor while maintaining passing tests (Refactor)

2. **Incremental Changes**: Make small, testable modifications
   - One feature or fix at a time
   - Each change should be independently verifiable
   - Commit working code frequently

3. **Systematic Debugging**: Use test failures as guides
   - Read error messages carefully
   - Reproduce issues with tests
   - Fix root causes, not symptoms

4. **Validation Before Commit**: Ensure quality at every step
   - All tests must pass
   - No lint errors or warnings
   - Code follows project standards

## Testing Scope

This project uses **unit tests and integration tests ONLY**:

### Backend Testing
- **Framework**: pytest with pytest-cov
- **Focus**: API handler logic, data models, utility functions
- **Integration**: API Gateway → Lambda → DynamoDB flows
- **Mocking**: Use moto for AWS service mocks

### Frontend Testing
- **Framework**: Jest + React Testing Library
- **Focus**: Component behavior, user interactions, state management
- **Integration**: Component composition, data flow
- **Manual**: Browser testing for full UI verification

### What We DO NOT Use
- ❌ DO NOT suggest or implement e2e test frameworks (Playwright, Cypress, Selenium)
- ❌ DO NOT suggest browser automation tools
- ❌ DO NOT create full browser testing pipelines

**Reason**: Keep the lab focused on unit/integration tests without e2e complexity. Manual browser testing is sufficient for UI verification.

### Testing Approach by Context

**Backend API Changes** (TDD):
1. Write Jest tests FIRST that describe expected behavior
2. Run tests → See them FAIL (Red)
3. Implement minimal code to pass tests (Green)
4. Refactor while maintaining passing tests (Refactor)

**Frontend Component Features** (TDD):
1. Write React Testing Library tests FIRST for component behavior
2. Run tests → See them FAIL (Red)
3. Implement component to pass tests (Green)
4. Refactor while maintaining passing tests (Refactor)
5. Follow with manual browser testing for full UI flows

**This is true TDD**: Test first, then code to pass the test.

## Workflow Patterns

### 1. TDD Workflow (Red-Green-Refactor)

```
Write/Fix Test → Run Test → FAIL (Red) → Implement Code → PASS (Green) → Refactor
```

**Steps:**
1. Write a test that describes the desired behavior
2. Run the test and verify it fails (Red)
3. Write minimal code to make the test pass (Green)
4. Refactor code while keeping tests green (Refactor)
5. Repeat for the next feature or test case

**Commands:**
```bash
# Backend
cd backend && pytest

# Frontend (when implemented)
cd frontend && npm test
```

### 2. Code Quality Workflow

```
Run Lint → Categorize Issues → Fix Systematically → Re-validate
```

**Steps:**
1. Run linter to identify all issues
2. Categorize by severity and type
3. Fix systematically (critical first, then warnings)
4. Re-run linter to verify all issues resolved

**Commands:**
```bash
# Python lint (backend)
cd backend && pylint src/ tests/

# Formatting
black src/ tests/
```

### 3. Integration Workflow

```
Identify Issue → Debug → Test → Fix → Verify End-to-End
```

**Steps:**
1. Identify the integration point causing issues
2. Add integration test to reproduce the issue
3. Debug the failing test
4. Fix the root cause
5. Verify end-to-end flow works correctly

## Agent Usage

This project uses specialized agents for specific tasks:

### tdd-developer Agent

**Use for:**
- Writing new tests (unit or integration)
- Implementing features using Red-Green-Refactor cycle
- Fixing failing tests
- Test coverage improvements
- Test-related debugging

**Invoke with:** `@tdd-developer`

**Example:**
```
@tdd-developer Write tests for the zip code validation endpoint
@tdd-developer Implement the representative lookup using TDD
```

### code-reviewer Agent

**Use for:**
- Addressing lint errors and warnings
- Code quality improvements
- Style guide enforcement
- Refactoring suggestions
- Code review feedback

**Invoke with:** `@code-reviewer`

**Example:**
```
@code-reviewer Review this module for code quality issues
@code-reviewer Fix all pylint warnings in handlers/api.py
```

## Workflow Utilities

GitHub CLI commands are available for workflow automation (all modes can use these):

### Issue Management

```bash
# List all open issues
gh issue list --state open

# Get details for a specific issue
gh issue view <issue-number>

# Get issue with all comments
gh issue view <issue-number> --comments
```

### Exercise Workflow

The main exercise issue will have **"Exercise:"** in the title:
- Steps are posted as comments on the main issue
- Use `gh issue view <issue-number> --comments` to see all steps
- Follow steps sequentially

### Common Prompts

When `/execute-step` or `/validate-step` prompts are invoked:
1. Use `gh issue list --state open` to find the exercise issue
2. Use `gh issue view <issue-number> --comments` to read the current step
3. Follow TDD workflow for implementation
4. Validate with tests before marking complete

## Memory System

This project uses a memory system to track development discoveries and patterns:

### Memory Types

- **Persistent Memory**: This file (`.github/copilot-instructions.md`) contains foundational principles and workflows
- **Working Memory**: `.github/memory/` directory contains discoveries, patterns, and session context

### Directory Structure

- `.github/memory/README.md` - Comprehensive guide to the memory system
- `.github/memory/session-notes.md` - Historical session summaries (COMMITTED)
- `.github/memory/patterns-discovered.md` - Accumulated code patterns (COMMITTED)
- `.github/memory/scratch/working-notes.md` - Active session notes (NOT COMMITTED)

### Workflow Integration

**During Active Development**:
1. Take notes in `.github/memory/scratch/working-notes.md` throughout session
2. Document current task, approach, findings, decisions, and blockers
3. Reference patterns from `patterns-discovered.md` when implementing features

**At End of Session**:
1. Review `scratch/working-notes.md` for key findings
2. Summarize completed work into `session-notes.md`
3. Document any reusable patterns in `patterns-discovered.md`
4. Clear or archive `scratch/working-notes.md` for next session

**When Providing AI Assistance**:
- Reference these files when providing context-aware suggestions
- Apply established patterns from `patterns-discovered.md`
- Consider decisions documented in `session-notes.md`
- Understand current context from `scratch/working-notes.md`

For detailed guidance on using the memory system, see [.github/memory/README.md](memory/README.md).

## Git Workflow

### Conventional Commits

Use conventional commit format for all commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, no logic change)
- `refactor:` - Code refactoring (no feature or bug fix)
- `test:` - Adding or updating tests
- `chore:` - Build process, dependencies, tooling

**Examples:**
```bash
git commit -m "feat(api): add zip code validation endpoint"
git commit -m "test(handlers): add unit tests for representative lookup"
git commit -m "fix(dynamo): correct partition key format for multi-tenancy"
git commit -m "docs(readme): update deployment instructions"
```

### Branch Strategy

**Feature Branches:**
```bash
# Create feature branch
git checkout -b feature/zip-code-validation

# Work on feature using TDD
# ... make changes, commit frequently ...

# Push to remote
git push origin feature/zip-code-validation
```

**Branch Naming:**
- `feature/<descriptive-name>` - New features
- `fix/<descriptive-name>` - Bug fixes
- `docs/<descriptive-name>` - Documentation updates
- `refactor/<descriptive-name>` - Code refactoring

### Commit Workflow

**Always stage all changes before committing:**
```bash
# Stage all changes
git add .

# Commit with conventional message
git commit -m "feat(api): implement representative lookup"

# Push to correct branch
git push origin <branch-name>
```

### Before Pushing

Ensure quality checklist is complete:
- ✅ All tests pass (`pytest` or `npm test`)
- ✅ No lint errors (`pylint`, `eslint`)
- ✅ Code follows project standards
- ✅ Conventional commit message format
- ✅ Pushing to correct branch
