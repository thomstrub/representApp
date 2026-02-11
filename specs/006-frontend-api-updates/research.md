# Research: Frontend API Integration Updates

**Date**: 2026-02-10  
**Feature**: Frontend API Integration Updates  
**Phase**: 0 - Research & Analysis

## Overview

This research document captures technical decisions and best practices for updating the React/TypeScript frontend to consume the new nested API response structure from the backend.

## Research Questions Answered

### 1. Pre-Grouped API Response Structure

**Question**: Should representatives be grouped on the backend or frontend?

**Decision**: Backend grouping (already implemented)

**Rationale**:
- **Performance**: Backend can group once during data fetch; frontend would group on every render or state change
- **Data source of truth**: Government level is determined by backend data sources (Google Civic API, OpenStates); backend has authoritative information
- **Reduced client complexity**: Removes need for client-side grouping logic and testing
- **Consistency**: All clients (web, future mobile) receive data in same structure
- **Bandwidth**: No difference in payload size, but clearer semantic structure

**Alternatives Considered**:
- **Client-side grouping**: More flexible for dynamic grouping criteria, but adds unnecessary complexity when grouping criteria is fixed (government level). Rejected because government level is a stable, authoritative property from data sources.

### 2. TypeScript Type Safety for API Updates

**Question**: How to ensure type safety when updating API response structure?

**Decision**: Use TypeScript discriminated unions and type guards for response parsing

**Best Practices Applied**:
- Define strict TypeScript interfaces for new nested structure: `ApiSuccessResponse` with nested `representatives` object containing `federal`, `state`, `local` arrays
- Use Zod schemas for runtime validation (already in place for form validation, can extend to API responses if needed)
- Implement type guards for error responses (`isApiErrorResponse`)
- Enable TypeScript strict mode (already enabled)
- Use `unknown` for API responses until validated, then narrow to specific types

**Implementation Pattern**:
```typescript
interface GroupedRepresentatives {
  federal: Representative[];
  state: Representative[];
  local: Representative[];
}

interface ApiSuccessResponse {
  representatives: GroupedRepresentatives;
  metadata: {
    address: string;
    coordinates?: { latitude: number; longitude: number };
    total_count: number;
    government_levels: string[];
  };
  warnings?: string[];
}
```

**Rationale**: Strong typing catches errors at compile-time, IDE autocomplete works correctly, refactoring is safer with type checking.

### 3. React Component Update Strategy

**Question**: What's the best approach for updating React components with minimal breaking changes?

**Decision**: Incremental update with backward-compatible intermediate state

**Best Practices Applied**:
- **Update data layer first**: Change API types and `useRepresentatives` hook to parse new structure
- **Update display layer second**: Modify `ResultsDisplay` to consume pre-grouped data (remove `groupByGovernmentLevel` call)
- **Add new features last**: Add metadata display (resolved address, counts) and warnings display components
- **Follow TDD**: Write failing tests for new structure → update implementation → verify tests pass → refactor

**Rationale**: This sequence minimizes risk by validating data parsing before changing UI. Each step is independently testable.

### 4. Handling Missing Data and Edge Cases

**Question**: How to gracefully handle missing optional fields (photo, email, phone, etc.)?

**Decision**: Use nullish coalescing operators and conditional rendering

**Best Practices Applied**:
- **TypeScript**: Mark optional fields as `field?: type | null` in interfaces
- **React**: Use `{field && <Component />}` for conditional rendering
- **Fallbacks**: Display initials avatar when `photo_url` is null/missing (already implemented in RepresentativeCard)
- **Contact info**: Show contact fields as clickable links (email → mailto:, phone → tel:, website → opens in new tab) only when present
- **Empty states**: Show helpful messages when arrays are empty at each government level

**Implementation Example** (already in use):
```typescript
// RepresentativeCard.tsx
{representative.photo_url ? (
  <Avatar src={representative.photo_url} />
) : (
  <Avatar>{getInitials(representative.name)}</Avatar>
)}

{representative.email && (
  <Link href={`mailto:${representative.email}`}>
    <EmailIcon /> Email
  </Link>
)}
```

**Rationale**: Prevents displaying "null" or "undefined" to users, provides meaningful fallbacks, maintains accessibility.

### 5. Testing Strategy for API Structure Changes

**Question**: How to test the updated components without breaking existing tests?

**Decision**: Update mock data to match new structure, add integration tests for full flow

**Best Practices Applied**:
- **Update mocks first**: Change test fixtures to use nested `representatives` structure
- **Unit tests**: Test each component with new data structure independently
- **Integration tests**: Test `HomePage` → `useRepresentatives` → `ResultsDisplay` flow with new API response
- **Error cases**: Test empty arrays at each level, missing optional fields, error responses
- **Type guards**: Test `isApiErrorResponse` with various payloads

**Test Coverage Goals**:
- All existing tests pass after updates
- New tests for metadata and warnings display
- Edge case tests for empty results at each government level
- Type guard tests for API response validation

**Rationale**: Comprehensive testing ensures the update doesn't break existing functionality while validating new features.

## Technology Choices

### Frontend Stack (No Changes)
- **React 18.x**: Already in use, hooks-based architecture
- **TypeScript 5.x**: Strong typing for API contracts
- **Material UI (MUI)**: Component library for consistent design
- **React Hook Form + Zod**: Form validation (unchanged)
- **Jest + React Testing Library**: Testing framework (unchanged)

### New Display Components Needed
- **Metadata Display Component**: Show resolved address, total counts
  - Material UI Typography for text
  - Material UI Card or Paper for container
- **Warnings Display Component**: Show warnings array when present
  - Material UI Alert component (severity="warning")
  - Material UI Box for layout

## Performance Considerations

### Rendering Performance
- **Current**: `groupByGovernmentLevel` utility runs on every render of `ResultsDisplay`
  - Complexity: O(n) where n = number of representatives
  - Typical n: 10-50 representatives per query
- **Proposed**: Direct consumption of pre-grouped data
  - Complexity: O(1) - no client-side processing needed
  - Result: Faster render, especially on lower-end devices

### Network Performance
- **Payload size**: No significant change (same data, different structure)
- **Parsing time**: Negligible (JSON parse is fast for small payloads)
- **Type validation**: If using Zod runtime validation, adds ~1-5ms per response (acceptable)

## Accessibility Considerations

### ARIA Labels (Maintained)
- Federal, State, Local sections already use `role="region"` with `aria-label`
- No changes needed to accessibility structure

### New Accessibility Requirements
- **Metadata**: Use semantic HTML (`<address>` tag for resolved address)
- **Warnings**: Use `role="alert"` for warning messages to announce to screen readers
- **Contact links**: Include `aria-label` with descriptive text (e.g., "Email John Doe")

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|----------|
| Breaking changes to existing UI | Low | High | Incremental updates with comprehensive test coverage |
| Type mismatches at runtime | Low | Medium | TypeScript strict mode + type guards |
| Missing data crashes UI | Low | Medium | Defensive programming with null checks |
| Performance regression | Very Low | Low | Pre-grouped data is more performant |
| Accessibility regression | Very Low | Medium | Manual testing with screen reader |

## Dependencies

### Existing Dependencies (No Updates Required)
- `react@^18.0.0` - Core framework
- `react-dom@^18.0.0` - DOM rendering
- `@mui/material@^5.0.0` - UI components
- `react-hook-form@^7.0.0` - Form handling
- `zod@^3.0.0` - Schema validation
- `@testing-library/react@^14.0.0` - Component testing
- `@testing-library/jest-dom@^6.0.0` - Testing matchers

### New Dependencies Required
- **None** - All required functionality available with existing dependencies

## Open Questions

None - All technical decisions resolved. Ready to proceed to Phase 1 (Design & Contracts).

## References

- [React TypeScript Best Practices](https://react-typescript-cheatsheet.netlify.app/)
- [Material UI Component API](https://mui.com/material-ui/api/)
- [React Testing Library Best Practices](https://testing-library.com/docs/react-testing-library/intro/)
- [TypeScript Handbook - Type Guards](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- Project documentation:
  - [functional-requirements.md](../../docs/functional-requirements.md)
  - [ui-guidelines.md](../../docs/ui-guidelines.md)
  - [testing-guidelines.md](../../docs/testing-guidelines.md)
  - [coding-guidelines.md](../../docs/coding-guidelines.md)
