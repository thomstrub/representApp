import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useRepresentatives } from '../../src/hooks/useRepresentatives';

// Mock fetch globally
global.fetch = vi.fn();

describe('useRepresentatives', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should start in idle state', () => {
    const { result } = renderHook(() => useRepresentatives());
    expect(result.current.appState.status).toBe('idle');
  });

  it('should transition to loading state when fetchByAddress is called', async () => {
    const mockFetch = vi.mocked(fetch);
    let resolvePromise: () => void;
    mockFetch.mockImplementationOnce(() => 
      new Promise((resolve) => {
        resolvePromise = () => resolve({
          ok: true,
          json: async () => ({ representatives: [], metadata: { address: '', government_levels: [] } })
        } as Response);
      })
    );

    const { result } = renderHook(() => useRepresentatives());
    
    await waitFor(() => {
      result.current.fetchByAddress('123 Main St');
    });
    
    await waitFor(() => {
      expect(result.current.appState.status).toBe('loading');
    });
  });

  it('should transition to success state with data when API returns representatives', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        representatives: {
          federal: [
            {
              id: '1',
              name: 'Jane Smith',
              office: 'US Senator',
              party: 'Democratic',
              government_level: 'federal' as const,
              jurisdiction: 'United States',
            },
          ],
          state: [],
          local: [],
        },
        metadata: {
          address: '123 Main St',
          total_count: 1,
          government_levels: ['federal'],
        },
      }),
    } as Response);

    const { result } = renderHook(() => useRepresentatives());
    
    result.current.fetchByAddress('123 Main St');

    await waitFor(() => {
      expect(result.current.appState.status).toBe('success');
    });

    if (result.current.appState.status === 'success') {
      expect(result.current.appState.data).toHaveLength(1);
      expect(result.current.appState.data[0].name).toBe('Jane Smith');
    }
  });

  it('should transition to error state when API returns 404', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({
        error: {
          code: 'ADDRESS_NOT_FOUND',
          message: 'No representatives found',
        },
      }),
    } as Response);

    const { result } = renderHook(() => useRepresentatives());
    
    result.current.fetchByAddress('123 Fake St');

    await waitFor(() => {
      expect(result.current.appState.status).toBe('error');
    });

    if (result.current.appState.status === 'error') {
      expect(result.current.appState.message).toContain('No representatives found');
    }
  });

  it('should transition to error state when API returns 500', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({
        error: {
          code: 'INTERNAL_ERROR',
          message: 'Internal server error',
        },
      }),
    } as Response);

    const { result } = renderHook(() => useRepresentatives());
    
    result.current.fetchByAddress('123 Main St');

    await waitFor(() => {
      expect(result.current.appState.status).toBe('error');
    });

    if (result.current.appState.status === 'error') {
      expect(result.current.appState.message).toBeTruthy();
    }
  });

  it('should handle network errors', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useRepresentatives());
    
    result.current.fetchByAddress('123 Main St');

    await waitFor(() => {
      expect(result.current.appState.status).toBe('error');
    });

    if (result.current.appState.status === 'error') {
      expect(result.current.appState.message).toContain('Network error');
    }
  });

  it('should have clearResults function that resets to idle state', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        representatives: { federal: [], state: [], local: [] },
        metadata: {
          address: '123 Main St',
          total_count: 0,
          government_levels: [],
        },
      }),
    } as Response);

    const { result } = renderHook(() => useRepresentatives());
    
    await waitFor(() => {
      result.current.fetchByAddress('123 Main St');
    });

    await waitFor(() => {
      expect(result.current.appState.status).toBe('success');
    });

    await waitFor(() => {
      result.current.clearResults();
    });

    await waitFor(() => {
      expect(result.current.appState.status).toBe('idle');
    });
  });

  // T005: New tests for nested API response structure
  describe('nested API response structure (US1)', () => {
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

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const { result } = renderHook(() => useRepresentatives());
      
      result.current.fetchByAddress('123 Main St');

      await waitFor(() => {
        expect(result.current.appState.status).toBe('success');
      });

      // Expect the data structure to include grouped representatives
      if (result.current.appState.status === 'success') {
        // Check if data contains the nested structure
        expect(result.current.appState.data).toBeDefined();
      }
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

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const { result } = renderHook(() => useRepresentatives());
      
      result.current.fetchByAddress('123 Main St');

      await waitFor(() => {
        expect(result.current.appState.status).toBe('success');
      });

      // Warnings should be accessible in the success state
      if (result.current.appState.status === 'success') {
        expect(result.current.appState.warnings).toBeDefined();
        expect(result.current.appState.warnings).toHaveLength(1);
        expect(result.current.appState.warnings?.[0]).toContain('incomplete');
      }
    });

    it('should store metadata with total_count and government_levels', async () => {
      const mockResponse = {
        representatives: {
          federal: [{ id: 'ocd-1', name: 'Test', office: 'Senator', government_level: 'federal', jurisdiction: 'US' }],
          state: [],
          local: [],
        },
        metadata: {
          address: '123 Main St, City, ST 12345',
          total_count: 1,
          government_levels: ['federal'],
        },
      };

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const { result } = renderHook(() => useRepresentatives());
      
      result.current.fetchByAddress('123 Main St');

      await waitFor(() => {
        expect(result.current.appState.status).toBe('success');
      });

      // Metadata should be accessible
      if (result.current.appState.status === 'success') {
        expect(result.current.appState.metadata).toBeDefined();
        expect(result.current.appState.metadata?.total_count).toBe(1);
        expect(result.current.appState.metadata?.government_levels).toEqual(['federal']);
        expect(result.current.appState.metadata?.address).toBe('123 Main St, City, ST 12345');
      }
    });
  });
});
