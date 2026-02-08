# Patterns Discovered

This file documents recurring code patterns, architectural decisions, and best practices discovered during development. Each pattern provides reusable solutions to common problems.

**Purpose**: Create a library of proven patterns for consistent implementation across the codebase.

**When to Update**: When you discover or establish a reusable pattern, add it here.

---

## Pattern Template

```markdown
## Pattern: [Pattern Name]

**Context**: When and where this pattern applies

**Problem**: What problem does this pattern solve?

**Solution**: How to implement the pattern

**Example**:
```[language]
// Code example demonstrating the pattern
```

**Related Files**:
- [file1.py](../../backend/src/file1.py)
- [file2.py](../../backend/src/file2.py)

**Notes**: Any additional considerations or caveats
```

---

## Pattern: Service Initialization - Empty Array vs Null

**Context**: When initializing service objects that may have optional collections or lists

**Problem**: Should we initialize optional collections as empty arrays `[]` or `null`/`None`? This affects:
- Type safety and null checks throughout the codebase
- API response consistency
- Frontend null handling

**Solution**: Use **empty arrays** for optional collections by default:

1. **Backend (Python)**: Initialize with empty list `[]` rather than `None`
2. **Data Models**: Use `Field(default_factory=list)` in Pydantic models
3. **API Responses**: Always return empty arrays, never null for collections
4. **Frontend**: Can safely iterate without null checks

**Rationale**:
- **Consistency**: APIs always return arrays (empty or populated)
- **Type Safety**: Frontend can assume array type without null guards
- **Simplicity**: `for item in items:` works without checking `if items is not None`
- **JSON Standard**: Empty array `[]` is more semantic than `null` for collections

**Example**:

```python
from pydantic import BaseModel, Field
from typing import List

# ✅ GOOD: Empty array default
class Representative(BaseModel):
    name: str
    party: str
    contact_info: List[dict] = Field(default_factory=list)
    social_media: List[str] = Field(default_factory=list)

# ❌ AVOID: None default for collections
class Representative(BaseModel):
    name: str
    party: str
    contact_info: List[dict] | None = None  # Requires null checks
    social_media: List[str] | None = None   # Requires null checks
```

**Frontend Usage**:
```javascript
// ✅ GOOD: Can always iterate safely
representative.socialMedia.map(handle => ...)

// ❌ AVOID: Requires defensive coding
representative.socialMedia?.map(handle => ...) || []
```

**Related Files**:
- [backend/src/models/domain.py](../../backend/src/models/domain.py)
- [backend/src/handlers/api.py](../../backend/src/handlers/api.py)

**Notes**:
- **Exception**: Use `None` when absence of data has semantic meaning different from "empty collection"
- **Performance**: Empty arrays have negligible memory overhead in Python
- **GraphQL**: This pattern aligns with GraphQL best practices (non-nullable lists)

---

## Pattern: [Next Pattern]

**Context**: [When to use]

**Problem**: [Problem solved]

**Solution**: [Implementation approach]

**Example**:
```python
# Your code example
```

**Related Files**:
- [File references]

**Notes**: [Additional considerations]
