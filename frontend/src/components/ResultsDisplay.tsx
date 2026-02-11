import { Box, Typography, Grid, Alert, AlertTitle } from '@mui/material';
import type { Representative } from '../types/representative';
import type { ApiSuccessResponse } from '../types/api';
import { RepresentativeCard } from './RepresentativeCard';
import { groupByGovernmentLevel } from '../utils/grouping';

interface ResultsDisplayProps {
  representatives?: Representative[];
  data?: ApiSuccessResponse;
}

export const ResultsDisplay = ({ representatives, data }: ResultsDisplayProps) => {
  // Support both legacy (representatives array) and new (data object) formats
  if (data) {
    const { representatives: reps, metadata, warnings } = data;
    const hasAnyRepresentatives = metadata.total_count > 0;

    return (
      <Box sx={{ mt: 4 }}>
        {/* Metadata: Resolved Address */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary">
            Showing representatives for:
          </Typography>
          <Typography variant="h6" component="address" sx={{ fontStyle: 'normal' }}>
            {metadata.address}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Found {metadata.total_count} representative{metadata.total_count !== 1 ? 's' : ''} 
            {metadata.government_levels.length > 0 && 
              ` across ${metadata.government_levels.length} government level${metadata.government_levels.length !== 1 ? 's' : ''}`
            }
          </Typography>
        </Box>

        {/* Warnings */}
        {warnings && warnings.length > 0 && (
          <Box sx={{ mb: 3 }}>
            {warnings.map((warning, index) => (
              <Alert severity="warning" key={index} role="alert" sx={{ mb: 1 }}>
                <AlertTitle>Note</AlertTitle>
                {warning}
              </Alert>
            ))}
          </Box>
        )}

        {/* Empty State */}
        {!hasAnyRepresentatives && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No representatives found for this address.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please check the address and try again.
            </Typography>
          </Box>
        )}

        {/* Federal Representatives */}
        {reps.federal.length > 0 && (
          <Box sx={{ mb: 4 }} role="region" aria-label="Federal Representatives">
            <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
              Federal Representatives
            </Typography>
            <Grid container spacing={2}>
              {reps.federal.map((rep) => (
                <Grid xs={12} sm={6} md={4} key={rep.id}>
                  <RepresentativeCard representative={rep} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* State Representatives */}
        {reps.state.length > 0 && (
          <Box sx={{ mb: 4 }} role="region" aria-label="State Representatives">
            <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
              State Representatives
            </Typography>
            <Grid container spacing={2}>
              {reps.state.map((rep) => (
                <Grid xs={12} sm={6} md={4} key={rep.id}>
                  <RepresentativeCard representative={rep} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Local Representatives */}
        {reps.local.length > 0 && (
          <Box sx={{ mb: 4 }} role="region" aria-label="Local Representatives">
            <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
              Local Representatives
            </Typography>
            <Grid container spacing={2}>
              {reps.local.map((rep) => (
                <Grid xs={12} sm={6} md={4} key={rep.id}>
                  <RepresentativeCard representative={rep} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Box>
    );
  }

  // Legacy format: flat array of representatives
  if (!representatives || representatives.length === 0) {
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
