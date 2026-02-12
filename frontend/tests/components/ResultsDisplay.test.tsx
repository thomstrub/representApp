import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResultsDisplay } from '../../src/components/ResultsDisplay';

describe('ResultsDisplay', () => {
  // Tests for nested API response structure (US1 & US2)
  describe('with nested API response', () => {
    const mockApiResponse = {
      representatives: {
        federal: [
          {
            id: 'ocd-1',
            name: 'John Federal',
            office: 'Senator',
            party: 'Democratic',
            government_level: 'federal' as const,
            jurisdiction: 'United States',
          },
        ],
        state: [
          {
            id: 'ocd-2',
            name: 'Jane State',
            office: 'State Rep',
            party: 'Republican',
            government_level: 'state' as const,
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

    it('should display representatives grouped by level from API', () => {
      render(<ResultsDisplay data={mockApiResponse} />);

      // Check sections appear
      expect(screen.getByText('Federal Representatives')).toBeInTheDocument();
      expect(screen.getByText('State Representatives')).toBeInTheDocument();
      expect(screen.queryByText('Local Representatives')).not.toBeInTheDocument();

      // Check representatives appear
      expect(screen.getByText('John Federal')).toBeInTheDocument();
      expect(screen.getByText('Jane State')).toBeInTheDocument();
    });

    it('should display resolved address from metadata', () => {
      render(<ResultsDisplay data={mockApiResponse} />);

      expect(screen.getByText(/123 Main St, City, ST 12345/)).toBeInTheDocument();
    });

    it('should display total count from metadata', () => {
      render(<ResultsDisplay data={mockApiResponse} />);

      expect(screen.getByText(/Found 2 representative/i)).toBeInTheDocument();
    });

    it('should show helpful message when all levels are empty', () => {
      const emptyData = {
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

    it('should display warnings when present in response', () => {
      const dataWithWarnings = {
        ...mockApiResponse,
        warnings: ['Local representatives data may be incomplete', 'Data source may be outdated'],
      };

      render(<ResultsDisplay data={dataWithWarnings} />);

      expect(screen.getByText(/Local representatives data may be incomplete/i)).toBeInTheDocument();
      expect(screen.getByText(/Data source may be outdated/i)).toBeInTheDocument();
    });
  });
});
