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
    const mockRepresentatives = [
      {
        id: '1',
        name: 'Jane Smith',
        office: 'US Senator',
        party: 'Democratic',
        government_level: 'federal' as const,
        jurisdiction: 'United States',
      },
    ];

    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        representatives: mockRepresentatives,
        metadata: {
          address: '123 Main St',
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
        representatives: [],
        metadata: {
          address: '123 Main St',
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
});
