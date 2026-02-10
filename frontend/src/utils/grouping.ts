import { Representative } from '../types/representative';

/**
 * Representatives grouped by government level
 */
export interface GroupedRepresentatives {
  federal: Representative[];
  state: Representative[];
  local: Representative[];
}

/**
 * Group representatives by government level
 * @param representatives - Array of representatives to group
 * @returns Representatives organized by federal, state, and local levels
 */
export const groupByGovernmentLevel = (
  representatives: Representative[]
): GroupedRepresentatives => {
  return representatives.reduce<GroupedRepresentatives>(
    (acc, rep) => {
      const level = rep.government_level;
      if (level === 'federal' || level === 'state' || level === 'local') {
        acc[level].push(rep);
      }
      return acc;
    },
    { federal: [], state: [], local: [] }
  );
};
