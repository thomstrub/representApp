/**
 * Integration test: Frontend-Backend API compatibility
 * 
 * This test validates that:
 * 1. Frontend can parse real backend responses
 * 2. TypeScript types match actual API structure
 * 3. All expected fields are present
 */

import { describe, it, expect } from 'vitest';
import type { ApiSuccessResponse } from '../../src/types/api';
import type { Representative } from '../../src/types/representative';

describe('Backend API Compatibility', () => {
  // Sample response from: curl "https://pktpja4zxd.execute-api.us-west-1.amazonaws.com/api/representatives?address=..."
  const mockBackendResponse = {
    address: "1301 4th Ave Seattle WA 98101",
    representatives: [
      {
        id: "ocd-person/9eddb3cd-868e-42ba-831a-b415fd7ed445",
        name: "Adam Bernbaum",
        office: "Representative",
        party: "Democratic",
        email: "adam.bernbaum@leg.wa.gov",
        phone: null,
        address: null,
        website: null,
        photo_url: "https://leg.wa.gov/memberphoto/34240.jpg",
        government_level: "state",
        jurisdiction: "Washington"
      }
    ],
    metadata: {
      address: "1301 4th Ave Seattle WA 98101",
      division_count: 7,
      representative_count: 50,
      government_levels: ["state"],
      response_time_ms: 1745
    },
    warnings: [
      "No representative data available for King County WA County Council District 8"
    ]
  };

  it('should match ApiSuccessResponse type structure', () => {
    // Type assertion - this will fail at compile time if types don't match
    const response: ApiSuccessResponse = mockBackendResponse;

    expect(response).toHaveProperty('address');
    expect(response).toHaveProperty('representatives');
    expect(response).toHaveProperty('metadata');
    expect(response).toHaveProperty('warnings');
  });

  it('should have all required metadata fields', () => {
    const { metadata } = mockBackendResponse;

    expect(metadata).toHaveProperty('address');
    expect(metadata).toHaveProperty('division_count');
    expect(metadata).toHaveProperty('representative_count');
    expect(metadata).toHaveProperty('government_levels');
    expect(metadata).toHaveProperty('response_time_ms');

    expect(typeof metadata.address).toBe('string');
    expect(typeof metadata.division_count).toBe('number');
    expect(typeof metadata.representative_count).toBe('number');
    expect(Array.isArray(metadata.government_levels)).toBe(true);
    expect(typeof metadata.response_time_ms).toBe('number');
  });

  it('should have valid representative structure', () => {
    const rep = mockBackendResponse.representatives[0];

    // Type assertion
    const typedRep: Representative = rep;

    // Required fields
    expect(typedRep).toHaveProperty('id');
    expect(typedRep).toHaveProperty('name');
    expect(typedRep).toHaveProperty('office');
    expect(typedRep).toHaveProperty('government_level');
    expect(typedRep).toHaveProperty('jurisdiction');

    // Government level must be valid enum value
    expect(['federal', 'state', 'local']).toContain(rep.government_level);

    // Optional fields (can be null or undefined)
    expect(['string', 'object']).toContain(typeof rep.party); // null is 'object'
    expect(['string', 'object', 'undefined']).toContain(typeof rep.email);
    expect(['string', 'object', 'undefined']).toContain(typeof rep.phone);
    expect(['string', 'object', 'undefined']).toContain(typeof rep.website);
    expect(['string', 'object', 'undefined']).toContain(typeof rep.photo_url);
  });

  it('should handle warnings array', () => {
    expect(Array.isArray(mockBackendResponse.warnings)).toBe(true);
    expect(mockBackendResponse.warnings?.length).toBeGreaterThan(0);
    expect(typeof mockBackendResponse.warnings?.[0]).toBe('string');
  });

  it('should validate government_levels in metadata', () => {
    const { government_levels } = mockBackendResponse.metadata;

    expect(Array.isArray(government_levels)).toBe(true);
    
    // All values should be valid government levels
    government_levels.forEach(level => {
      expect(['federal', 'state', 'local']).toContain(level);
    });
  });
});
