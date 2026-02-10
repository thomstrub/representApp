import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RepresentativeCard } from '../../src/components/RepresentativeCard';
import { Representative } from '../../src/types/representative';

describe('RepresentativeCard', () => {
  const mockRepresentative: Representative = {
    id: '1',
    name: 'Jane Smith',
    office: 'US Senator',
    party: 'Democratic',
    government_level: 'federal',
    jurisdiction: 'United States',
    email: 'senator.smith@senate.gov',
    phone: '202-555-0100',
    address: '123 Senate Office Building, Washington, DC 20510',
    website: 'https://smith.senate.gov',
    photo_url: 'https://example.com/photo.jpg',
  };

  it('should render representative name and office', () => {
    render(<RepresentativeCard representative={mockRepresentative} />);

    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('US Senator')).toBeInTheDocument();
  });

  it('should render party affiliation', () => {
    render(<RepresentativeCard representative={mockRepresentative} />);

    expect(screen.getByText(/democratic/i)).toBeInTheDocument();
  });

  it('should render contact information when available', () => {
    render(<RepresentativeCard representative={mockRepresentative} />);

    expect(screen.getByText(/senator.smith@senate.gov/i)).toBeInTheDocument();
    expect(screen.getByText(/202-555-0100/i)).toBeInTheDocument();
    expect(screen.getByText(/123 Senate Office Building/i)).toBeInTheDocument();
  });

  it('should render website link when available', () => {
    render(<RepresentativeCard representative={mockRepresentative} />);

    const websiteLink = screen.getByRole('link', { name: /website/i });
    expect(websiteLink).toBeInTheDocument();
    expect(websiteLink).toHaveAttribute('href', 'https://smith.senate.gov');
    expect(websiteLink).toHaveAttribute('target', '_blank');
    expect(websiteLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('should render photo when photo_url is provided', () => {
    render(<RepresentativeCard representative={mockRepresentative} />);

    const image = screen.getByRole('img', { name: /jane smith/i });
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'https://example.com/photo.jpg');
  });

  it('should render initials avatar when photo_url is not provided', () => {
    const repWithoutPhoto = { ...mockRepresentative, photo_url: null };
    render(<RepresentativeCard representative={repWithoutPhoto} />);

    expect(screen.getByText('JS')).toBeInTheDocument();
  });

  it('should handle null contact information gracefully', () => {
    const repWithNullContact: Representative = {
      id: '2',
      name: 'John Doe',
      office: 'State Senator',
      party: 'Republican',
      government_level: 'state',
      jurisdiction: 'California',
      email: null,
      phone: null,
      address: null,
      website: null,
      photo_url: null,
    };

    render(<RepresentativeCard representative={repWithNullContact} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('State Senator')).toBeInTheDocument();
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });

  it('should handle null party affiliation', () => {
    const repWithNullParty = { ...mockRepresentative, party: null };
    render(<RepresentativeCard representative={repWithNullParty} />);

    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    // Party section should either not render or show "Independent" or similar
  });
});
