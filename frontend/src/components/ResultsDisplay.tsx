import { Box, Typography, Alert } from '@mui/material';
import type { ApiSuccessResponse } from '../types/api';
import { RepresentativeCard } from './RepresentativeCard';

interface ResultsDisplayProps {
  data: ApiSuccessResponse;
}

export const ResultsDisplay = ({ data }: ResultsDisplayProps) => {
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

      {/* Warnings Display */}
      {warnings && warnings.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {warnings.map((warning, index) => (
            <Alert key={index} severity="warning" sx={{ mb: 1 }} role="alert">
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
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: 'repeat(1, 1fr)',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 2,
            }}
          >
            {reps.federal.map((rep) => (
              <RepresentativeCard key={rep.id} representative={rep} />
            ))}
          </Box>
        </Box>
      )}

      {/* State Representatives */}
      {reps.state.length > 0 && (
        <Box sx={{ mb: 4 }} role="region" aria-label="State Representatives">
          <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
            State Representatives
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: 'repeat(1, 1fr)',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 2,
            }}
          >
            {reps.state.map((rep) => (
              <RepresentativeCard key={rep.id} representative={rep} />
            ))}
          </Box>
        </Box>
      )}

      {/* Local Representatives */}
      {reps.local.length > 0 && (
        <Box sx={{ mb: 4 }} role="region" aria-label="Local Representatives">
          <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
            Local Representatives
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: 'repeat(1, 1fr)',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 2,
            }}
          >
            {reps.local.map((rep) => (
              <RepresentativeCard key={rep.id} representative={rep} />
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
};
