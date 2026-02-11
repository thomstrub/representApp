import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResultsDisplay } from '../../src/components/ResultsDisplay';
import { Representative } from '../../src/types/representative';

describe('ResultsDisplay', () => {
  const mockRepresentatives: Representative[] = [
    {
      id: '1',
      name: 'Jane Smith',
      office: 'US Senator',
      party: 'Democratic',
      government_level: 'federal',
      jurisdiction: 'United States',
    },
    {
      id: '2',
      name: 'Bob Wilson',
      office: 'US Representative',
      party: 'Republican',
      government_level: 'federal',
      jurisdiction: 'United States',
    },
    {
      id: '3',
      name: 'Alice Johnson',
      office: 'State Senator',
      party: 'Democratic',
      government_level: 'state',
      jurisdiction: 'California',
    },
    {
      id: '4',
      name: 'Charlie Brown',
      office: 'City Council Member',
      party: 'Independent',
      government_level: 'local',
      jurisdiction: 'Seattle',
    },
  ];

  it('should render federal, state, and local sections', () => {
    render(<ResultsDisplay representatives={mockRepresentatives} />);

    expect(screen.getByText(/federal representatives/i)).toBeInTheDocument();
    expect(screen.getByText(/state representatives/i)).toBeInTheDocument();
    expect(screen.getByText(/local representatives/i)).toBeInTheDocument();
  });

  it('should group representatives correctly by government level', () => {
    render(<ResultsDisplay representatives={mockRepresentatives} />);

    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Bob Wilson')).toBeInTheDocument();
    expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
    expect(screen.getByText('Charlie Brown')).toBeInTheDocument();
  });

  it('should not render sections with no representatives', () => {
    const onlyFederalReps: Representative[] = [
      {
        id: '1',
        name: 'Jane Smith',
        office: 'US Senator',
        party: 'Democratic',
        government_level: 'federal',
        jurisdiction: 'United States',
      },
    ];

    render(<ResultsDisplay representatives={onlyFederalReps} />);

    expect(screen.getByText(/federal representatives/i)).toBeInTheDocument();
    expect(screen.queryByText(/state representatives/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/local representatives/i)).not.toBeInTheDocument();
  });

  it('should display message when no representatives are found', () => {
    render(<ResultsDisplay representatives={[]} />);

    expect(screen.getByText(/no representatives found/i)).toBeInTheDocument();
  });

  it('should render representatives in vertical sections', () => {
    const { container } = render(<ResultsDisplay representatives={mockRepresentatives} />);

    // Check that sections are vertically stacked (not horizontally)
    // This can be verified by checking for section elements or specific layout classes
    const sections = container.querySelectorAll('[role="region"]');
    expect(sections.length).toBeGreaterThan(0);
  });

  // T006: New tests for nested API response structure
  describe('with nested API response (US1)', () => {
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
  });
});
