---
description: "Validate that all success criteria for the current step are met"
agent: "code-reviewer"
tools: ["search", "read", "execute", "web", "todo"]
---

# Validate Step Success Criteria

Validate that all success criteria for a specific GitHub Issue step are met.

## Input Parameters

Step Number: ${input:step-number:Step number to validate (e.g., 5-0, 5-1, 5-2)}

## Instructions

### 1. Validate Step Number

**CRITICAL**: You MUST have a step number to proceed.

**If step number was NOT provided:**
- STOP and ask the user for the step number
- Explain format: `X-Y` where X is the main step and Y is the substep
- Example: `5-0`, `5-1`, `5-2`, `6-0`

**Step number is REQUIRED** - Do not proceed without it.

### 2. Find the Exercise Issue

Run: `gh issue list --state open`

Find the issue with **"Exercise:"** in the title.

Note the issue number.

### 3. Get Issue Content with Comments

Run: `gh issue view <issue-number> --comments`

This retrieves all steps posted as comments on the issue.

### 4. Locate the Specific Step

Search through the issue content for:

```
# Step <step-number>:
```

For example, if validating step `5-1`, search for `# Step 5-1:`

Extract all content for that step until the next `# Step` heading or end of comment.

### 5. Extract Success Criteria

From the step content, find the **"Success Criteria"** section.

This section lists what must be true for the step to be considered complete.

Example format:
```
## Success Criteria

- [ ] Criterion 1: Description
- [ ] Criterion 2: Description
- [ ] Criterion 3: Description
```

### 6. Validate Each Criterion

For each success criterion, check the current workspace state:

#### File Existence Checks
**Criterion**: "File X exists"
- Run: `ls <file-path>` or use read tool
- ✅ Pass: File exists
- ❌ Fail: File not found

#### Test Coverage Checks
**Criterion**: "Tests pass"
- Run: `cd backend && pytest` or `cd frontend && npm test`
- ✅ Pass: All tests pass
- ❌ Fail: Tests failing with specific errors

#### Code Content Checks
**Criterion**: "Function X is implemented"
- Read the relevant file
- Search for the function/class/method
- ✅ Pass: Code exists and looks complete
- ❌ Fail: Code missing or incomplete

#### Lint Checks
**Criterion**: "No lint errors"
- Run: `cd backend && pylint src/` or `cd frontend && npm run lint`
- ✅ Pass: Zero errors
- ❌ Fail: Lint errors present

#### Implementation Checks
**Criterion**: "Endpoint returns correct response"
- Read the implementation
- Check tests verify the behavior
- ✅ Pass: Implementation matches requirements
- ❌ Fail: Implementation incomplete

### 7. Generate Validation Report

Create a report showing:

```
## Step <step-number> Validation Report

### Success Criteria Status

✅ Criterion 1: [Description]
   - Status: PASS
   - Details: [What was verified]

❌ Criterion 2: [Description]
   - Status: FAIL
   - Details: [What's missing/wrong]
   - Action Needed: [Specific guidance to fix]

✅ Criterion 3: [Description]
   - Status: PASS
   - Details: [What was verified]

### Overall Status: [X/Y criteria met]

[If all pass]: ✅ All success criteria met! Ready to commit.
[If any fail]: ❌ Some criteria not met. Address the items above before committing.
```

### 8. Provide Specific Guidance

**For each failing criterion:**
- Explain exactly what's missing
- Provide specific file paths or commands to fix
- Reference project patterns from `.github/memory/patterns-discovered.md` if applicable
- Suggest running `/execute-step` again if major work needed

**If all criteria pass:**
- Congratulate the user
- Recommend running `/commit-and-push` to commit changes
- Suggest updating `.github/memory/scratch/working-notes.md` with learnings

## Expected Workflow

```
Get Step Number → Find Issue → Get Issue Content → Locate Step → Extract Criteria → Validate Each → Report Status → Guide Next Actions
```

## Example Validation

**Step 5-1: Implement Zip Code Validation**

**Success Criteria:**
```
- [ ] Test file exists: backend/tests/unit/test_zip_validation.py
- [ ] Handler implements validation: backend/src/handlers/api.py
- [ ] All tests pass: pytest returns 0 exit code
- [ ] No lint errors: pylint returns 0 errors
```

**Validation Process:**
1. Check file exists: `ls backend/tests/unit/test_zip_validation.py` → ✅ Exists
2. Read handler: Search for zip validation logic → ✅ Found
3. Run tests: `cd backend && pytest` → ❌ 2 tests failing
4. Run lint: `cd backend && pylint src/` → ✅ No errors

**Report:**
```
## Step 5-1 Validation Report

### Success Criteria Status

✅ Test file exists: backend/tests/unit/test_zip_validation.py
   - Status: PASS
   - Details: File found at expected location

✅ Handler implements validation: backend/src/handlers/api.py
   - Status: PASS
   - Details: Validation logic found in get_representatives handler

❌ All tests pass: pytest returns 0 exit code
   - Status: FAIL
   - Details: 2 tests failing in test_zip_validation.py
     - test_invalid_zip_format: AssertionError: Expected 400, got 500
     - test_military_zip: Expected True, got False
   - Action Needed: Fix validation logic to handle military zip codes and return proper 400 status for invalid formats

✅ No lint errors: pylint returns 0 errors
   - Status: PASS
   - Details: Clean pylint run

### Overall Status: 3/4 criteria met

❌ Some criteria not met. Fix the failing tests before committing.

**Next Steps:**
1. Fix the validation logic in backend/src/handlers/api.py
2. Run pytest to verify fixes
3. Run /validate-step 5-1 again to confirm all criteria pass
4. Then run /commit-and-push to commit changes
```

## Success Criteria Validation Checklist

### Code Quality
- ✅ All tests pass (pytest or npm test)
- ✅ No lint errors (pylint or eslint)
- ✅ Code follows project conventions
- ✅ Proper error handling implemented

### Implementation Completeness
- ✅ Required files exist
- ✅ Required functions/classes implemented
- ✅ Required tests written and passing
- ✅ Edge cases handled

### Documentation
- ✅ Code is documented (docstrings, comments where needed)
- ✅ Working memory updated with findings
- ✅ Patterns documented if reusable

## What NOT To Do

- ❌ Never validate without a step number
- ❌ Never skip checking actual test results
- ❌ Never report "pass" without verifying
- ❌ Never provide vague guidance for failures
- ❌ Never validate against wrong step number

## Success Criteria

You have successfully validated when:
- ✅ Step number was provided and located in issue
- ✅ All success criteria extracted correctly
- ✅ Each criterion was checked against workspace state
- ✅ Detailed validation report generated
- ✅ Specific guidance provided for any failures
- ✅ User knows exactly what to do next
- ✅ If all pass, user is ready to commit

## Reference Documentation

Consult these sections from `.github/copilot-instructions.md`:
- **Workflow Utilities** section: gh CLI commands
- **Testing Scope** section: What tests should exist
- **Development Principles** section: Validation requirements

Remember: **Validation is thorough, not superficial** - Check everything.
