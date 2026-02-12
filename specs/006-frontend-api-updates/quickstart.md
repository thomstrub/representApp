# Quickstart: Frontend API Integration Updates

**Feature**: Frontend API Integration Updates  
**Branch**: `006-frontend-api-updates`  
**Date**: 2026-02-10

## Overview

This guide provides step-by-step instructions for updating the React/TypeScript frontend to consume the new nested API response structure from the backend. The changes involve updating TypeScript types, modifying the `useRepresentatives` hook, updating the `ResultsDisplay` component, and adding display components for metadata and warnings.

**Estimated Time**: 3-4 hours  
**Prerequisites**: Node.js 18+, npm, familiarity with React, TypeScript, and Jest

---

## Quick Start

```bash
# 1. Checkout and setup
git checkout 006-frontend-api-updates
cd frontend
npm install

# 2. Run tests in watch mode (TDD workflow)
npm test -- --watch

# 3. Start development server (optional, for manual testing)
npm run dev
```

---

## Step-by-Step Implementation (TDD Approach)

### Phase 1: Update TypeScript Types (Red-Green-Refactor)

**Goal**: Define the new API response structure and ensure type safety.

#### Step 1.1: Write failing test for new API types

**File**: `frontend/tests/unit/types/api.test.ts` (create if doesn't exist)

```typescript
import { describe, it, expect } from 'vitest';
import type { ApiSuccessResponse } from '../../../src/types/api';
import { isApiErrorResponse } from '../../../src/types/api';

describe('API Types', () => {
  it('should accept new nested representatives structure', () => {
    const response: ApiSuccessResponse = {
      representatives: {
        federal: [
          {
            id: 'ocd-division/country:us',
            name: 'Joe Biden',
            office: 'President',
            party: 'Democratic',
            government_level: 'federal',
            jurisdiction: 'United States',
          },
        ],
        state: [],
        local: [],
      },
      metadata: {
        address: '1600 Pennsylvania Avenue NW, Washington, DC 20500',
        total_count: 1,
        government_levels: ['federal'],
      },
    };

    // Should compile without errors
    expect(response.representatives.federal).toHaveLength(1);
    expect(response.metadata.total_count).toBe(1);
  });

  it('should accept metadata with optional coordinates', () => {
    const response: ApiSuccessResponse = {
      representatives: { federal: [], state: [], local: [] },
      metadata: {
        address: '123 Main St',
        coordinates: {
          latitude: 38.8977,
          longitude: -77.0365,
        },
        total_count: 0,
        government_levels: [],
      },
    };

    expect(response.metadata.coordinates?.latitude).toBe(38.8977);
  });

  it('should accept optional warnings array', () => {
    const response: ApiSuccessResponse = {
      representatives: { federal: [], state: [], local: [] },
      metadata: {
        address: '123 Main St',
        total_count: 0,
        government_levels: [],
      },
      warnings: ['No local representatives found'],
    };

    expect(response.warnings).toHaveLength(1);
  });

  it('should identify error responses with type guard', () => {
    const errorResponse = {
      error: {
        code: 'INVALID_ADDRESS',
        message: 'Invalid address format',
      },
    };

    expect(isApiErrorResponse(errorResponse)).toBe(true);
  });
});
```

**Run test**: `npm test` → Should FAIL (Red) because types don't exist yet.

#### Step 1.2: Update API types to make tests pass

**File**: `frontend/src/types/api.ts`

```typescript
import type { Representative } from './representative';

/**
 * Representatives grouped by government level
 */
export interface GovernmentLevelGroup {
  federal: Representative[];
  state: Representative[];
  local: Representative[];
}

/**
 * Geographic coordinates
 */
export interface Coordinates {
  latitude: number;
  longitude: number;
}

/**
 * Search metadata with context and statistics
 */
export interface Metadata {
  address: string;
  coordinates?: Coordinates;
  total_count: number;
  government_levels: string[];
  response_time_ms?: number;
}

/**
 * Success response from GET /representatives
 */
export interface ApiSuccessResponse {
  representatives: GovernmentLevelGroup;
  metadata: Metadata;
  warnings?: string[];
}

/**
 * Error response from backend API
 */
export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: string;
  };
}

/**
 * Type guard for API error response
 */
export const isApiErrorResponse = (data: unknown): data is ApiErrorResponse => {
  return (
    typeof data === 'object' &&
    data !== null &&
    'error' in data &&
    typeof (data as { error: unknown }).error === 'object' &&
    (data as { error: unknown }).error !== null &&
    'code' in (data as { error: { code?: unknown } }).error &&
    'message' in (data as { error: { message?: unknown } }).error
  );
};
```

**Run test**: `npm test` → Should PASS (Green).

**Refactor**: Types are clean, no refactoring needed.

---

### Phase 2: Update useRepresentatives Hook (Red-Green-Refactor)

**Goal**: Update the hook to parse the new nested API response structure.

#### Step 2.1: Write failing tests for updated hook

**File**: `frontend/tests/unit/hooks/useRepresentatives.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useRepresentatives } from '../../../src/hooks/useRepresentatives';

// Mock fetch globally
global.fetch = vi.fn();

describe('useRepresentatives Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should parse nested representatives structure from API', async () => {
    const mockResponse = {
      representatives: {
        federal: [
          {
            id: 'ocd-1',
            name: 'John Doe',
            office: 'Senator',
            party: 'Democratic',
            government_level: 'federal',
            jurisdiction: 'State',
          },
        ],
        state: [
          {
            id: 'ocd-2',
            name: 'Jane Smith',
            office: 'Representative',
            party: 'Republican',
            government_level: 'state',
            jurisdiction: 'District 5',
          },
        ],
        local: [],
      },
      metadata: {
        address: '123 Main St, City, ST 12345',
        total_count: 2,
        government_levels: ['federal', 'state'],
      },
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useRepresentatives());
    
    result.current.fetchRepresentatives('123 Main St');

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockResponse);
    expect(result.current.data?.representatives.federal).toHaveLength(1);
    expect(result.current.data?.representatives.state).toHaveLength(1);
    expect(result.current.data?.representatives.local).toHaveLength(0);
    expect(result.current.data?.metadata.total_count).toBe(2);
  });

  it('should store warnings when present in response', async () => {
    const mockResponse = {
      representatives: { federal: [], state: [], local: [] },
      metadata: {
        address: '123 Main St',
        total_count: 0,
        government_levels: [],
      },
      warnings: ['Local representatives data may be incomplete'],
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useRepresentatives());
    
    result.current.fetchRepresentatives('123 Main St');

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data?.warnings).toHaveLength(1);
    expect(result.current.data?.warnings?.[0]).toContain('incomplete');
  });
});
```

**Run test**: `npm test` → Should FAIL (Red) because hook expects old structure.

#### Step 2.2: Update hook implementation

**File**: `frontend/src/hooks/useRepresentatives.ts`

```typescript
import { useState } from 'react';
import type { ApiSuccessResponse } from '../types/api';
import { isApiErrorResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

export const useRepresentatives = () => {
  const [data, setData] = useState<ApiSuccessResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRepresentatives = async (address: string) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/representatives?address=${encodeURIComponent(address)}`
      );

      const json = await response.json();

      if (!response.ok || isApiErrorResponse(json)) {
        const errorMsg = isApiErrorResponse(json) 
          ? json.error.message 
          : 'Failed to fetch representatives';
        setError(errorMsg);
        return;
      }

      setData(json as ApiSuccessResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return {
    data,
    loading,
    error,
    fetchRepresentatives,
  };
};
```

**Run test**: `npm test` → Should PASS (Green).

**Refactor**: Code is clean, error handling is comprehensive.

---

### Phase 3: Update ResultsDisplay Component (Red-Green-Refactor)

**Goal**: Update component to consume pre-grouped data and display metadata/warnings.

#### Step 3.1: Write failing tests for updated component

**File**: `frontend/tests/unit/components/ResultsDisplay.test.tsx`

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResultsDisplay } from '../../../src/components/ResultsDisplay';
import type { ApiSuccessResponse } from '../../../src/types/api';

const mockData: ApiSuccessResponse = {
  representatives: {
    federal: [
      {
        id: 'ocd-1',
        name: 'John Federal',
        office: 'Senator',
        party: 'Democratic',
        government_level: 'federal',
        jurisdiction: 'United States',
      },
    ],
    state: [
      {
        id: 'ocd-2',
        name: 'Jane State',
        office: 'State Rep',
        party: 'Republican',
        government_level: 'state',
        jurisdiction: 'District 5',
      },
    ],
    local: [],
  },
  metadata: {
    address: '123 Main St, City, ST 12345',
    total_count: 2,
    government_levels: ['federal', 'state'],
  },
};

describe('ResultsDisplay Component', () => {
  it('should display representatives grouped by level from API', () => {
    render(<ResultsDisplay data={mockData} />);

    // Check sections appear
    expect(screen.getByText('Federal Representatives')).toBeInTheDocument();
    expect(screen.getByText('State Representatives')).toBeInTheDocument();
    expect(screen.queryByText('Local Representatives')).not.toBeInTheDocument();

    // Check representatives appear
    expect(screen.getByText('John Federal')).toBeInTheDocument();
    expect(screen.getByText('Jane State')).toBeInTheDocument();
  });

  it('should display resolved address from metadata', () => {
    render(<ResultsDisplay data={mockData} />);

    expect(screen.getByText(/123 Main St, City, ST 12345/)).toBeInTheDocument();
  });

  it('should display total count from metadata', () => {
    render(<ResultsDisplay data={mockData} />);

    expect(screen.getByText(/Found 2 representatives/i)).toBeInTheDocument();
  });

  it('should display warnings when present', () => {
    const dataWithWarnings: ApiSuccessResponse = {
      ...mockData,
      warnings: ['Local representatives data may be incomplete'],
    };

    render(<ResultsDisplay data={dataWithWarnings} />);

    expect(screen.getByText(/Local representatives data may be incomplete/)).toBeInTheDocument();
  });

  it('should show helpful message when all levels are empty', () => {
    const emptyData: ApiSuccessResponse = {
      representatives: { federal: [], state: [], local: [] },
      metadata: {
        address: '123 Main St',
        total_count: 0,
        government_levels: [],
      },
    };

    render(<ResultsDisplay data={emptyData} />);

    expect(screen.getByText(/No representatives found/i)).toBeInTheDocument();
    expect(screen.getByText(/check the address/i)).toBeInTheDocument();
  });
});
```

**Run test**: `npm test` → Should FAIL (Red) because component expects old structure.

#### Step 3.2: Update ResultsDisplay component

**File**: `frontend/src/components/ResultsDisplay.tsx`

```typescript
import { Box, Typography, Grid, Alert, AlertTitle } from '@mui/material';
import type { ApiSuccessResponse } from '../types/api';
import { RepresentativeCard } from './RepresentativeCard';

interface ResultsDisplayProps {
  data: ApiSuccessResponse;
}

export const ResultsDisplay = ({ data }: ResultsDisplayProps) => {
  const { representatives, metadata, warnings } = data;
  const hasAnyRepresentatives = metadata.total_count > 0;

  return (
    <Box sx={{ mt: 4 }}>
      {/* Metadata: Resolved Address */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Showing representatives for:
        </Typography>
        <Typography variant="h6" component="address" sx={{ fontStyle: 'normal' }}>
          {metadata.address}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Found {metadata.total_count} representative{metadata.total_count !== 1 ? 's' : ''} 
          {metadata.government_levels.length > 0 && 
            ` across ${metadata.government_levels.length} government level${metadata.government_levels.length !== 1 ? 's' : ''}`
          }
        </Typography>
      </Box>

      {/* Warnings */}
      {warnings && warnings.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {warnings.map((warning, index) => (
            <Alert severity="warning" key={index} role="alert" sx={{ mb: 1 }}>
              <AlertTitle>Note</AlertTitle>
              {warning}
            </Alert>
          ))}
        </Box>
      )}

      {/* Empty State */}
      {!hasAnyRepresentatives && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No representatives found for this address.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Please check the address and try again.
          </Typography>
        </Box>
      )}

      {/* Federal Representatives */}
      {representatives.federal.length > 0 && (
        <Box sx={{ mb: 4 }} role="region" aria-label="Federal Representatives">
          <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
            Federal Representatives
          </Typography>
          <Grid container spacing={2}>
            {representatives.federal.map((rep) => (
              <Grid item xs={12} sm={6} md={4} key={rep.id}>
                <RepresentativeCard representative={rep} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* State Representatives */}
      {representatives.state.length > 0 && (
        <Box sx={{ mb: 4 }} role="region" aria-label="State Representatives">
          <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
            State Representatives
          </Typography>
          <Grid container spacing={2}>
            {representatives.state.map((rep) => (
              <Grid item xs={12} sm={6} md={4} key={rep.id}>
                <RepresentativeCard representative={rep} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Local Representatives */}
      {representatives.local.length > 0 && (
        <Box sx={{ mb: 4 }} role="region" aria-label="Local Representatives">
          <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
            Local Representatives
          </Typography>
          <Grid container spacing={2}>
            {representatives.local.map((rep) => (
              <Grid item xs={12} sm={6} md={4} key={rep.id}>
                <RepresentativeCard representative={rep} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
};
```

**Run test**: `npm test` → Should PASS (Green).

**Refactor**: Consider extracting metadata and warnings into separate components for better separation of concerns (optional).

---

### Phase 4: Update HomePage Integration (Red-Green-Refactor)

**Goal**: Update the main page to pass the full API response to ResultsDisplay.

#### Step 4.1: Write failing integration test

**File**: `frontend/tests/integration/HomePage.test.tsx`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HomePage } from '../../src/pages/HomePage';

global.fetch = vi.fn();

describe('HomePage Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display grouped representatives with metadata after search', async () => {
    const mockResponse = {
      representatives: {
        federal: [
          {
            id: 'ocd-1',
            name: 'Federal Rep',
            office: 'Senator',
            party: 'Democratic',
            government_level: 'federal',
            jurisdiction: 'US',
          },
        ],
        state: [],
        local: [],
      },
      metadata: {
        address: '1600 Pennsylvania Avenue NW, Washington, DC 20500',
        total_count: 1,
        government_levels: ['federal'],
      },
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(<HomePage />);

    const input = screen.getByLabelText(/address/i);
    const button = screen.getByRole('button', { name: /search/i });

    await userEvent.type(input, '1600 Pennsylvania Avenue NW');
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Federal Rep')).toBeInTheDocument();
    });

    expect(screen.getByText(/1600 Pennsylvania Avenue NW, Washington, DC 20500/)).toBeInTheDocument();
    expect(screen.getByText(/Found 1 representative/i)).toBeInTheDocument();
  });

  it('should display warnings when API returns them', async () => {
    const mockResponse = {
      representatives: {
        federal: [],
        state: [],
        local: [],
      },
      metadata: {
        address: '123 Main St',
        total_count: 0,
        government_levels: [],
      },
      warnings: ['Could not find local representatives'],
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(<HomePage />);

    const input = screen.getByLabelText(/address/i);
    const button = screen.getByRole('button', { name: /search/i });

    await userEvent.type(input, '123 Main St');
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Could not find local representatives/)).toBeInTheDocument();
    });
  });
});
```

**Run test**: `npm test` → May PASS or FAIL depending on current HomePage implementation.

#### Step 4.2: Update HomePage if needed

**File**: `frontend/src/pages/HomePage.tsx`

```typescript
import { Container, Typography, Box } from '@mui/material';
import { AddressForm } from '../components/AddressForm';
import { ResultsDisplay } from '../components/ResultsDisplay';
import { LoadingIndicator } from '../components/LoadingIndicator';
import { useRepresentatives } from '../hooks/useRepresentatives';

export const HomePage = () => {
  const { data, loading, error, fetchRepresentatives } = useRepresentatives();

  const handleSearch = (address: string) => {
    fetchRepresentatives(address);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Find Your Representatives
        </Typography>
        
        <AddressForm onSubmit={handleSearch} />
        
        {loading && <LoadingIndicator />}
        
        {error && (
          <Box sx={{ mt: 4 }}>
            <Typography color="error">{error}</Typography>
          </Box>
        )}
        
        {data && !loading && !error && <ResultsDisplay data={data} />}
      </Box>
    </Container>
  );
};
```

**Run test**: `npm test` → Should PASS (Green).

---

### Phase 5: Remove Deprecated Code

**Goal**: Remove the `groupByGovernmentLevel` utility function since it's no longer needed.

#### Step 5.1: Remove utility and tests

```bash
# Remove grouping utility (no longer needed)
rm frontend/src/utils/grouping.ts
rm frontend/tests/unit/utils/grouping.test.ts
```

#### Step 5.2: Run all tests to ensure nothing breaks

```bash
npm test
```

All tests should still pass since no component uses the grouping utility anymore.

---

## Verification Checklist

Before committing, verify:

- [ ] All tests pass (`npm test`)
- [ ] No TypeScript errors (`npm run type-check` or check IDE)
- [ ] No ESLint errors (`npm run lint`)
- [ ] Manual browser test: Search for an address and verify:
  - [ ] Representatives grouped by level
  - [ ] Resolved address displays correctly
  - [ ] Total count displays correctly
  - [ ] Warnings display when present (you may need to test with edge case addresses)
  - [ ] Empty state shows helpful message
  - [ ] Contact info displays as clickable links
  - [ ] Photo fallback (initials) works for reps without photos

---

## Manual Testing

```bash
# Start dev server
cd frontend
npm run dev

# Open browser: http://localhost:5173
```

**Test Cases**:

1. **Full results**: Search "1600 Pennsylvania Avenue NW, Washington DC"
   - Should show federal representatives
   - Should display resolved address
   - Should show total count

2. **Empty results**: Search "Invalid Address XYZ"
   - Should show error message or empty state
   - Should suggest checking the address

3. **Partial results**: Search addresses in different states
   - Some may have only federal and state (no local)
   - Should gracefully handle empty local array

---

## Troubleshooting

### TypeScript Errors

**Issue**: Type errors about `data.representatives` not having `federal`, `state`, `local` properties.

**Solution**: Ensure you've updated the `ApiSuccessResponse` interface in `frontend/src/types/api.ts` to use the `GovernmentLevelGroup` structure.

### Tests Failing

**Issue**: Tests expect old flat array structure.

**Solution**: Update test fixtures to use the new nested structure with `{ federal: [], state: [], local: [] }`.

### Component Not Rendering

**Issue**: Component shows blank screen or "No representatives found" even with valid data.

**Solution**: Check that `ResultsDisplay` is receiving `data` prop and that it's accessing `data.representatives.federal`, etc. (not `data.representatives` as a flat array).

---

## Next Steps

After completing this feature:

1. **Code Review**: Create a pull request for team review
2. **Manual Testing**: QA team should test various addresses
3. **Performance Testing**: Verify render times in Chrome DevTools
4. **Accessibility Testing**: Test with screen reader (VoiceOver, NVDA)
5. **Deploy**: Merge to main and deploy to staging environment

---

## References

- [Feature Specification](spec.md)
- [Data Model](data-model.md)
- [API Contract Schema](contracts/api-response.schema.json)
- [Research Document](research.md)
- [Project Testing Guidelines](../../docs/testing-guidelines.md)
- [Project Coding Guidelines](../../docs/coding-guidelines.md)
