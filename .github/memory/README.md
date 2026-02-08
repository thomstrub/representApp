# Memory System for Represent App

## Overview

This memory system helps track development discoveries, patterns, decisions, and lessons learned throughout the project lifecycle. It complements the foundational principles in `.github/copilot-instructions.md` by providing a space to document active learning and accumulated wisdom.

## Purpose

During development, we discover patterns, make decisions, encounter blockers, and learn from mistakes. This system captures that knowledge so:

- **AI assistants** can learn from past decisions and apply proven patterns
- **Developers** can understand why decisions were made and what patterns work
- **The team** builds institutional knowledge over time
- **Context** is preserved across sessions and team members

## Memory Types

### Persistent Memory (`.github/copilot-instructions.md`)
- **What**: Foundational principles, workflows, and established practices
- **When to Update**: Rarely - only when core practices change
- **Committed**: Yes - this is the project's constitution
- **Examples**: TDD workflow, testing scope, git conventions

### Working Memory (`.github/memory/`)
- **What**: Active discoveries, evolving patterns, session-specific context
- **When to Update**: Frequently - during and after development sessions
- **Committed**: Partially - see directory structure below
- **Examples**: "Why we chose X over Y", "Pattern for Z that works well"

## Directory Structure

```
.github/memory/
├── README.md                    # This file - explains the memory system
├── session-notes.md             # Historical session summaries (COMMITTED)
├── patterns-discovered.md       # Accumulated code patterns (COMMITTED)
└── scratch/                     # Active session workspace (NOT COMMITTED)
    ├── .gitignore              # Ignores all files in scratch/
    └── working-notes.md        # Current session notes (ephemeral)
```

### File Purposes

#### `session-notes.md` (Committed)
- **Purpose**: Document completed development sessions for future reference
- **Content**: What was accomplished, key findings, decisions made, outcomes
- **Update When**: At the END of each session, summarize key findings from `scratch/working-notes.md`
- **Audience**: Future developers and AI assistants reviewing project history

#### `patterns-discovered.md` (Committed)
- **Purpose**: Document recurring code patterns and architectural decisions
- **Content**: Named patterns with context, problem, solution, examples
- **Update When**: When you discover or establish a reusable pattern
- **Audience**: Developers implementing similar features

#### `scratch/working-notes.md` (Not Committed)
- **Purpose**: Active note-taking during current development session
- **Content**: Current task, approach, findings, blockers, decisions, next steps
- **Update When**: Throughout the session as you work
- **Audience**: Yourself and AI during the current session only
- **Lifecycle**: Clear or archive at session end after summarizing into `session-notes.md`

## When to Use Each File

### During TDD Workflow

**Write Test (Red Phase):**
- Note in `scratch/working-notes.md`: What test you're writing and why
- Reference patterns from `patterns-discovered.md` if applicable

**Implement Code (Green Phase):**
- Note in `scratch/working-notes.md`: Implementation approach, challenges encountered
- Document new patterns in `patterns-discovered.md` if you discover something reusable

**Refactor:**
- Note in `scratch/working-notes.md`: What you refactored and why
- Update patterns in `patterns-discovered.md` if the pattern evolved

### During Code Quality Workflow

**Run Lint:**
- Note in `scratch/working-notes.md`: Categories of errors found

**Fix Issues:**
- Note in `scratch/working-notes.md`: Key decisions made (e.g., "Chose X over Y because...")
- Document pattern in `patterns-discovered.md` if the solution is reusable

**Re-validate:**
- Note in `scratch/working-notes.md`: Any remaining issues or follow-up needed

### During Debugging Workflow

**Identify Issue:**
- Note in `scratch/working-notes.md`: Problem description, initial hypothesis

**Debug:**
- Note in `scratch/working-notes.md`: What you tried, what worked/didn't work

**Fix:**
- Note in `scratch/working-notes.md`: Root cause and solution
- Document in `patterns-discovered.md` if it reveals a common pitfall or best practice

**Verify:**
- Note in `scratch/working-notes.md`: How you verified the fix

### At End of Session

1. Review `scratch/working-notes.md`
2. Extract key findings, decisions, and outcomes
3. Add session summary to `session-notes.md`
4. Update `patterns-discovered.md` with any new patterns
5. Clear or archive `scratch/working-notes.md` for next session

## How AI Uses This System

When you ask AI assistants for help, they will:

1. **Read `.github/copilot-instructions.md`** for foundational principles and workflows
2. **Read `patterns-discovered.md`** to apply established patterns to your problem
3. **Read `session-notes.md`** to understand recent decisions and context
4. **Read `scratch/working-notes.md`** to understand your current session context
5. **Apply learned patterns** to provide context-aware suggestions
6. **Reference past decisions** to maintain consistency

This creates a feedback loop where each session builds on previous learnings.

## Example Usage Scenario

**Session Start:**
```markdown
# scratch/working-notes.md
## Current Task
Implement zip code validation endpoint

## Approach
- Write tests first (TDD)
- Use Google Civic API format validation
- Return 400 for invalid address or zip codes
```

**During Development:**
```markdown
## Key Findings
- Google API accepts both 5-digit and 9-digit formats
- Need to handle military/PO box zip codes differently
- API rate limiting requires exponential backoff

## Decisions Made
- Used regex pattern from civic tech best practices
- Implemented 3-retry logic with exponential backoff
- Cached validation results for 24 hours
```

**Session End:**
Transfer to `session-notes.md`:
```markdown
## Session: Zip Code Validation Implementation (2026-02-07)
Implemented and tested zip code validation endpoint with Google Civic API integration.
Key decisions: regex validation pattern, 3-retry exponential backoff, 24-hour caching.
Outcome: All tests passing, endpoint ready for integration.
```

Update `patterns-discovered.md`:
```markdown
## Pattern: API Retry with Exponential Backoff
**Problem**: External API calls may fail due to transient issues
**Solution**: Implement retry logic with exponential backoff and jitter
**Example**: See `backend/src/utils/api_client.py`
```

## Best Practices

1. **Be Specific**: Document concrete decisions, not vague observations
2. **Include Context**: Explain WHY, not just WHAT
3. **Reference Files**: Link to actual code when describing patterns
4. **Keep Current**: Update patterns as they evolve
5. **Clear Scratch**: Don't let `scratch/working-notes.md` accumulate cruft
6. **Summarize Sessions**: Always extract learnings into `session-notes.md`
7. **Review Before Starting**: Read recent session notes to refresh context

## Benefits

- **Faster Onboarding**: New developers understand decisions and patterns quickly
- **Better AI Assistance**: AI provides context-aware suggestions based on your learnings
- **Reduced Repetition**: Don't re-solve the same problems
- **Knowledge Retention**: Decisions and rationale are preserved over time
- **Pattern Recognition**: Accumulated patterns become reusable solutions

## Getting Started

1. At session start, open `scratch/working-notes.md` in your editor
2. Note your current task and approach
3. Update throughout the session with findings and decisions
4. At session end, summarize key learnings into `session-notes.md`
5. Document any reusable patterns in `patterns-discovered.md`
6. Clear `scratch/working-notes.md` for next session

The memory system is a living document - use it, update it, and let it evolve with your project.
