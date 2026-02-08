---
description: "Execute instructions from the current GitHub Issue step"
agent: "tdd-developer"
tools: ["search", "read", "edit", "execute", "web", "todo"]
---

# Execute Step from GitHub Issue

You are executing instructions from a GitHub Issue step. Follow the workflow utilities and TDD principles defined in `.github/copilot-instructions.md`.

## Input Parameters

Issue Number: ${input:issue-number:GitHub Issue number (leave blank to auto-find exercise issue)}

## Instructions

### 1. Find the Exercise Issue

**If issue number was provided:**
- Use that issue number directly

**If issue number was NOT provided:**
- Run: `gh issue list --state open`
- Find the issue with **"Exercise:"** in the title
- Note the issue number

### 2. Get Issue Content with All Steps

Run: `gh issue view <issue-number> --comments`

This retrieves:
- The main issue description
- All comments (steps are posted as comments)

### 3. Parse the Latest Step Instructions

From the issue comments:
- Find the most recent step that needs execution
- Look for sections like "# Step X-Y:"
- Identify all `:keyboard: Activity:` sections in that step
- These are the tasks you must execute

### 4. Execute Activities Systematically

For each `:keyboard: Activity:` section:

**Follow TDD Workflow (Red-Green-Refactor):**
1. **Write tests FIRST** that describe the desired behavior (Red)
2. Run tests to verify they fail appropriately
3. Implement minimal code to pass tests (Green)
4. Run tests to verify they pass
5. Refactor while keeping tests green (Refactor)

**Testing Constraints:**
- Backend: Use pytest (NO new test frameworks)
- Frontend: Use Jest + React Testing Library (NO new test frameworks)
- **CRITICAL**: DO NOT suggest Playwright, Cypress, Selenium, or any e2e test frameworks
- Manual browser testing for full UI flows

**Work Incrementally:**
- Complete one activity before moving to the next
- Run tests after each implementation
- Keep user informed of progress

### 5. Track Progress

Use the todo tool to track progress through activities:
- Mark each activity as you start it
- Mark complete when tests pass
- Note any blockers or issues

### 6. Update Working Memory

Document your work in `.github/memory/scratch/working-notes.md`:
- Note what step you're executing
- Document key findings and decisions
- Record any blockers encountered
- Track progress through activities

### 7. Stop and Inform User

**DO NOT COMMIT OR PUSH CHANGES** - That is the job of `/commit-and-push`

After completing all activities in the step:
1. Summarize what was completed
2. Note any files created or modified
3. Confirm all tests are passing
4. Instruct user: **"Run `/validate-step` with the step number to validate success criteria before committing."**

## Expected Workflow

```
Find Issue → Get Steps → Parse Activities → Execute with TDD → Update Memory → Stop (No Commit)
```

## Example Activities

### Example 1: Backend Endpoint
```
:keyboard: Activity: Create zip code validation endpoint
- Write test for /api/representatives?zip=12345
- Implement Lambda handler
- Verify tests pass
```

**Your Response:**
1. "Writing test FIRST for zip code validation endpoint..."
2. Create test file with failing test
3. "Test fails as expected. Implementing handler..."
4. Implement minimal handler code
5. "Tests passing! Refactoring..."
6. "Activity complete. Moving to next activity."

### Example 2: Frontend Component
```
:keyboard: Activity: Add zip code input form
- Write React Testing Library test for input component
- Implement component with Material UI
- Verify rendering and user interaction
```

**Your Response:**
1. "Writing test FIRST for zip code input component..."
2. Create test for component behavior
3. "Test fails as expected. Implementing component..."
4. Implement component using Material UI
5. "Tests passing! Recommend manual browser testing for UI verification."
6. "Activity complete. Moving to next activity."

## Success Criteria

You have successfully executed the step when:
- ✅ All `:keyboard: Activity:` sections are completed
- ✅ All tests are passing (pytest or npm test)
- ✅ TDD workflow was followed (Test First, Code Second)
- ✅ Working memory is updated with key findings
- ✅ User is instructed to run `/validate-step`
- ✅ NO commits or pushes were made

## Reference Documentation

Consult these files from `.github/copilot-instructions.md`:
- **Workflow Utilities** section: gh CLI commands
- **Testing Scope** section: Testing constraints
- **TDD Workflow** section: Red-Green-Refactor process
- **Memory System** section: Where to document findings

Remember: **Test First, Code Second** - This is the TDD way.
