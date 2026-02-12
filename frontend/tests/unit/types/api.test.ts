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
    expect(response.metadata.coordinates?.longitude).toBe(-77.0365);
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
    expect(response.warnings?.[0]).toBe('No local representatives found');
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

  it('should reject non-error responses with type guard', () => {
    const successResponse = {
      representatives: { federal: [], state: [], local: [] },
      metadata: {
        address: '123 Main St',
        total_count: 0,
        government_levels: [],
      },
    };

    expect(isApiErrorResponse(successResponse)).toBe(false);
  });
});
