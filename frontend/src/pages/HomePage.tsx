import { Container, Typography, Box, Paper } from '@mui/material';
import { AddressForm } from '../components/AddressForm';
import { LoadingIndicator } from '../components/LoadingIndicator';
import { ResultsDisplay } from '../components/ResultsDisplay';
import { useRepresentatives } from '../hooks/useRepresentatives';
import type { AddressFormData } from '../types/form';
import type { ApiSuccessResponse } from '../types/api';
import { groupByGovernmentLevel } from '../utils/grouping';

export const HomePage = () => {
  const { appState, fetchByAddress } = useRepresentatives();

  const handleSubmit = (data: AddressFormData) => {
    fetchByAddress(data.address);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Find Your Representatives
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph align="center">
          Enter your address to find your elected representatives at the federal, state, and local levels.
        </Typography>

        <Box sx={{ maxWidth: 600, mx: 'auto', mt: 3 }}>
          <AddressForm
            onSubmit={handleSubmit}
            disabled={appState.status === 'loading'}
          />
        </Box>

        {appState.status === 'error' && (
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="error">
              {appState.message}
            </Typography>
          </Box>
        )}
      </Paper>

      {appState.status === 'loading' && <LoadingIndicator />}

      {appState.status === 'success' && (() => {
        // If we have metadata and warnings, construct the full API response
        if (appState.metadata) {
          const grouped = groupByGovernmentLevel(appState.data);
          const apiResponse: ApiSuccessResponse = {
            representatives: grouped,
            metadata: appState.metadata,
            warnings: appState.warnings,
          };
          return <ResultsDisplay data={apiResponse} />;
        }
        
        // Fallback to legacy format for backward compatibility
        return <ResultsDisplay representatives={appState.data} />;
      })()}
    </Container>
  );
};
