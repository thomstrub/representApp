import { describe, it, expect } from 'vitest';
import { groupByGovernmentLevel } from '../../src/utils/grouping';
import { Representative } from '../../src/types/representative';

describe('groupByGovernmentLevel', () => {
  it('should group representatives by government level', () => {
    const representatives: Representative[] = [
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
        name: 'John Doe',
        office: 'State Senator',
        party: 'Republican',
        government_level: 'state',
        jurisdiction: 'California',
      },
      {
        id: '3',
        name: 'Alice Johnson',
        office: 'City Council Member',
        party: 'Independent',
        government_level: 'local',
        jurisdiction: 'Seattle',
      },
      {
        id: '4',
        name: 'Bob Wilson',
        office: 'US Representative',
        party: 'Democratic',
        government_level: 'federal',
        jurisdiction: 'United States',
      },
    ];

    const grouped = groupByGovernmentLevel(representatives);

    expect(grouped.federal).toHaveLength(2);
    expect(grouped.state).toHaveLength(1);
    expect(grouped.local).toHaveLength(1);
    expect(grouped.federal[0].name).toBe('Jane Smith');
    expect(grouped.federal[1].name).toBe('Bob Wilson');
    expect(grouped.state[0].name).toBe('John Doe');
    expect(grouped.local[0].name).toBe('Alice Johnson');
  });

  it('should return empty arrays when no representatives provided', () => {
    const grouped = groupByGovernmentLevel([]);

    expect(grouped.federal).toHaveLength(0);
    expect(grouped.state).toHaveLength(0);
    expect(grouped.local).toHaveLength(0);
  });

  it('should handle representatives with only one government level', () => {
    const representatives: Representative[] = [
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
        party: 'Democratic',
        government_level: 'federal',
        jurisdiction: 'United States',
      },
    ];

    const grouped = groupByGovernmentLevel(representatives);

    expect(grouped.federal).toHaveLength(2);
    expect(grouped.state).toHaveLength(0);
    expect(grouped.local).toHaveLength(0);
  });
});
