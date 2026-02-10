import { Box, Typography, Grid } from '@mui/material';
import { Representative } from '../types/representative';
import { RepresentativeCard } from './RepresentativeCard';
import { groupByGovernmentLevel } from '../utils/grouping';

interface ResultsDisplayProps {
  representatives: Representative[];
}

export const ResultsDisplay = ({ representatives }: ResultsDisplayProps) => {
  if (representatives.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          No representatives found for this address.
        </Typography>
      </Box>
    );
  }

  const grouped = groupByGovernmentLevel(representatives);

  return (
    <Box sx={{ mt: 4 }}>
      {grouped.federal.length > 0 && (
        <Box sx={{ mb: 4 }} role="region" aria-label="Federal Representatives">
          <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
            Federal Representatives
          </Typography>
          <Grid container spacing={2}>
            {grouped.federal.map((rep) => (
              <Grid xs={12} sm={6} md={4} key={rep.id}>
                <RepresentativeCard representative={rep} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {grouped.state.length > 0 && (
        <Box sx={{ mb: 4 }} role="region" aria-label="State Representatives">
          <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
            State Representatives
          </Typography>
          <Grid container spacing={2}>
            {grouped.state.map((rep) => (
              <Grid xs={12} sm={6} md={4} key={rep.id}>
                <RepresentativeCard representative={rep} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {grouped.local.length > 0 && (
        <Box sx={{ mb: 4 }} role="region" aria-label="Local Representatives">
          <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
            Local Representatives
          </Typography>
          <Grid container spacing={2}>
            {grouped.local.map((rep) => (
              <Grid xs={12} sm={6} md={4} key={rep.id}>
                <RepresentativeCard representative={rep} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
};
