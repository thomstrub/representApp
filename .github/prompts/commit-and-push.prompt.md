---
description: "Analyze changes, generate commit message, and push to feature branch"
tools: ["read", "execute", "todo"]
---

# Commit and Push to Feature Branch

Analyze current changes, generate a conventional commit message, and push to a feature branch.

## Input Parameters

Branch Name: ${input:branch-name:Feature branch name (e.g., feature/zip-code-validation)}

## Instructions

### 1. Validate Branch Name

**CRITICAL**: You MUST have a branch name to proceed.

**If branch name was NOT provided:**
- STOP and ask the user for the branch name
- Explain format: `feature/<descriptive-name>`, `fix/<descriptive-name>`, or `docs/<descriptive-name>`
- Example: `feature/representative-lookup`, `fix/cache-ttl-bug`

**Branch name is REQUIRED** - Do not proceed without it.

### 2. Analyze Changes

Run: `git status` to see modified files

Run: `git diff` to see what changed

**Understand the changes:**
- What features were added?
- What bugs were fixed?
- What was refactored?
- What tests were added/modified?

### 3. Generate Conventional Commit Message

Use the conventional commit format from `.github/copilot-instructions.md`:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring (no feature or bug fix)
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, no logic change)
- `chore:` - Build process, dependencies, tooling

**Examples:**
```bash
feat(api): add zip code validation endpoint

Implement /api/representatives endpoint with zip code validation.
Uses regex pattern for 5-digit and 9-digit formats.
Includes comprehensive test coverage.

feat(ui): add representative search component

Create RepresentativeSearch component with Material UI.
Includes zip code input, search button, and results display.
Follows React Testing Library best practices.

test(handlers): add integration tests for API flow

Add end-to-end tests for API Gateway → Lambda → DynamoDB flow.
Tests cover success cases, error handling, and edge cases.

fix(cache): correct TTL configuration for DynamoDB

Set TTL attribute to 24 hours instead of 24 seconds.
Prevents premature cache eviction.
```

**Generate a commit message** that:
- Uses the appropriate type
- Describes what was done
- Includes context in the body if needed
- References any issue numbers in footer if applicable

### 4. Create or Switch to Branch

**Check if branch exists:**
```bash
git branch --list <branch-name>
```

**If branch does NOT exist:**
```bash
git checkout -b <branch-name>
```

**If branch exists:**
```bash
git checkout <branch-name>
```

### 5. Stage All Changes

Run: `git add .`

This stages all modified, new, and deleted files.

### 6. Commit with Generated Message

Run: `git commit -m "<your-generated-message>"`

**Use the conventional commit message you generated in Step 3.**

### 7. Push to Feature Branch

Run: `git push origin <branch-name>`

**CRITICAL**: ONLY push to the branch name provided by the user.
- ❌ DO NOT push to `main`
- ❌ DO NOT push to any other branch
- ✅ ONLY push to the user-specified feature branch

### 8. Confirm Success

Report to the user:
- ✅ Branch created/switched to: `<branch-name>`
- ✅ Changes staged: [list modified files]
- ✅ Committed with message: `<commit-message>`
- ✅ Pushed to: `origin/<branch-name>`

**Next steps for the user:**
- Create a pull request if ready to merge
- Continue working on the branch for more changes
- Run `/validate-step` if validating exercise steps

## Expected Workflow

```
Validate Branch Name → Analyze Changes → Generate Commit Message → Create/Switch Branch → Stage → Commit → Push → Confirm
```

## Safety Checks

### Before Pushing
- ✅ All tests pass (`pytest` or `npm test`)
- ✅ No lint errors (if applicable)
- ✅ Branch name is correct (not `main`)
- ✅ Commit message follows conventional format

### If Tests Are Failing
- STOP and inform the user
- Do NOT commit failing tests
- Suggest running `/execute-step` or manual fixes

## Example Usage

**Scenario 1: After Implementing Feature**
```
User: /commit-and-push
Prompt: Branch Name: feature/zip-code-validation

Response:
1. Analyzing changes...
   - Modified: backend/src/handlers/api.py
   - Added: backend/tests/unit/test_zip_validation.py
2. Generated commit message: "feat(api): add zip code validation endpoint"
3. Creating branch feature/zip-code-validation...
4. Staging changes...
5. Committing with message...
6. Pushing to origin/feature/zip-code-validation...
✅ Success! Changes pushed to feature/zip-code-validation.
```

**Scenario 2: After Test Fixes**
```
User: /commit-and-push
Prompt: Branch Name: fix/cache-ttl-config

Response:
1. Analyzing changes...
   - Modified: infrastructure/stacks/backend_stack.py
2. Generated commit message: "fix(infra): correct DynamoDB TTL configuration"
3. Switching to existing branch fix/cache-ttl-config...
4. Staging changes...
5. Committing with message...
6. Pushing to origin/fix/cache-ttl-config...
✅ Success! Changes pushed to fix/cache-ttl-config.
```

## What NOT To Do

- ❌ Never commit without a conventional commit message
- ❌ Never push to `main` directly
- ❌ Never commit failing tests
- ❌ Never stage and commit without analyzing changes first
- ❌ Never proceed without a branch name

## Success Criteria

You have successfully committed and pushed when:
- ✅ Branch name was provided and validated
- ✅ Changes analyzed and understood
- ✅ Conventional commit message generated
- ✅ Branch created or switched to correctly
- ✅ All changes staged with `git add .`
- ✅ Committed with descriptive message
- ✅ Pushed to correct feature branch (NOT main)
- ✅ User informed of success with next steps

## Reference Documentation

Consult these sections from `.github/copilot-instructions.md`:
- **Git Workflow** section: Conventional commits, branch strategy
- **Development Principles** section: Validation before commit

Remember: **Feature branches, not main** - Keep main clean and stable.
