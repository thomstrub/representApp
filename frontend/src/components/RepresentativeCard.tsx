import { 
  Card, 
  CardContent, 
  CardActions,
  Typography, 
  Avatar, 
  Box,
  Link,
  Chip
} from '@mui/material';
import { Email, Phone, LocationOn, Language } from '@mui/icons-material';
import { Representative } from '../types/representative';

interface RepresentativeCardProps {
  representative: Representative;
}

export const RepresentativeCard = ({ representative }: RepresentativeCardProps) => {
  const getInitials = (name: string): string => {
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar
            src={representative.photo_url || undefined}
            alt={representative.name}
            sx={{ width: 64, height: 64, mr: 2 }}
          >
            {!representative.photo_url && getInitials(representative.name)}
          </Avatar>
          <Box>
            <Typography variant="h6" component="h3">
              {representative.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {representative.office}
            </Typography>
          </Box>
        </Box>

        {representative.party && (
          <Chip 
            label={representative.party} 
            size="small" 
            sx={{ mb: 2 }}
          />
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {representative.email && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Email fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {representative.email}
              </Typography>
            </Box>
          )}

          {representative.phone && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Phone fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {representative.phone}
              </Typography>
            </Box>
          )}

          {representative.address && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <LocationOn fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {representative.address}
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>

      {representative.website && (
        <CardActions>
          <Link
            href={representative.website}
            target="_blank"
            rel="noopener noreferrer"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <Language fontSize="small" />
            <Typography variant="body2">Website</Typography>
          </Link>
        </CardActions>
      )}
    </Card>
  );
};
