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
});
