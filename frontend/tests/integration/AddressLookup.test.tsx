import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HomePage } from '../../src/pages/HomePage';

// Mock fetch globally
global.fetch = vi.fn();

describe('AddressLookup Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should complete full flow: form submission → loading → results display', async () => {
    const mockRepresentatives = [
      {
        id: '1',
        name: 'Jane Smith',
        office: 'US Senator',
        party: 'Democratic',
        government_level: 'federal',
        jurisdiction: 'United States',
        email: 'senator.smith@senate.gov',
      },
      {
        id: '2',
        name: 'John Doe',
        office: 'State Senator',
        party: 'Republican',
        government_level: 'state',
        jurisdiction: 'California',
      },
    ];

    const mockFetch = vi.mocked(fetch);
    mockFetch.mockImplementationOnce(() => 
      new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            ok: true,
            json: async () => ({
              representatives: mockRepresentatives,
              metadata: {
                address: '123 Main St, Seattle, WA 98101',
                government_levels: ['federal', 'state'],
              },
            }),
          } as Response);
        }, 100); // Add delay to allow loading state to be observed
      })
    );

    const user = userEvent.setup();
    render(<HomePage />);

    // Initially, form should be visible
    const input = screen.getByLabelText(/enter your address/i);
    const button = screen.getByRole('button', { name: /find my representatives/i });

    expect(input).toBeInTheDocument();
    expect(button).toBeInTheDocument();

    // Enter address and submit
    await user.type(input, '123 Main St, Seattle, WA 98101');
    await user.click(button);

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
    
    // Form should be disabled during loading
    await waitFor(() => {
      expect(input).toBeDisabled();
      expect(button).toBeDisabled();
    });

    // Wait for results to appear
    await waitFor(() => {
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    }, { timeout: 3000 });

    // Verify representatives are displayed
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('US Senator')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('State Senator')).toBeInTheDocument();

    // Verify grouped by government level
    expect(screen.getByText(/federal representatives/i)).toBeInTheDocument();
    expect(screen.getByText(/state representatives/i)).toBeInTheDocument();
  });

  it('should show error message when API returns error', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({
        error: {
          code: 'ADDRESS_NOT_FOUND',
          message: 'No representatives found for this address',
        },
      }),
    } as Response);

    const user = userEvent.setup();
    render(<HomePage />);

    const input = screen.getByLabelText(/enter your address/i);
    const button = screen.getByRole('button', { name: /find my representatives/i });

    await user.type(input, '123 Fake St');
    await user.click(button);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/no representatives found/i)).toBeInTheDocument();
    });

    // Form should be re-enabled for retry
    expect(input).not.toBeDisabled();
    expect(button).not.toBeDisabled();
  });

  it('should handle validation errors before API call', async () => {
    const mockFetch = vi.mocked(fetch);
    const user = userEvent.setup();
    
    render(<HomePage />);

    const button = screen.getByRole('button', { name: /find my representatives/i });

    // Submit without entering address
    await user.click(button);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/address is required/i)).toBeInTheDocument();
    });

    // Should NOT call API
    expect(mockFetch).not.toHaveBeenCalled();
  });

  it('should allow user to search again after successful results', async () => {
    const mockFetch = vi.mocked(fetch);
    
    // First search
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        representatives: [
          {
            id: '1',
            name: 'Jane Smith',
            office: 'US Senator',
            party: 'Democratic',
            government_level: 'federal',
            jurisdiction: 'United States',
          },
        ],
        metadata: {
          address: '123 Main St',
          government_levels: ['federal'],
        },
      }),
    } as Response);

    const user = userEvent.setup();
    render(<HomePage />);

    // First search
    await user.type(screen.getByLabelText(/enter your address/i), '123 Main St');
    await user.click(screen.getByRole('button', { name: /find my representatives/i }));

    await waitFor(() => {
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    // Second search - clear and search again
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        representatives: [
          {
            id: '2',
            name: 'John Doe',
            office: 'State Senator',
            party: 'Republican',
            government_level: 'state',
            jurisdiction: 'California',
          },
        ],
        metadata: {
          address: '456 Oak Ave',
          government_levels: ['state'],
        },
      }),
    } as Response);

    const input = screen.getByLabelText(/enter your address/i);
    await user.clear(input);
    await user.type(input, '456 Oak Ave');
    await user.click(screen.getByRole('button', { name: /find my representatives/i }));

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Old results should be replaced
    expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
  });
});
