import { Box, CircularProgress, Typography } from '@mui/material';

export const LoadingIndicator = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
      }}
    >
      <CircularProgress />
      <Typography variant="body1" sx={{ mt: 2 }}>
        Loading representatives...
      </Typography>
    </Box>
  );
};
