import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { TextField, Button, Box } from '@mui/material';
import { addressSchema, AddressFormData } from '../types/form';

interface AddressFormProps {
  onSubmit: (data: AddressFormData) => void;
  disabled?: boolean;
}

export const AddressForm = ({ onSubmit, disabled = false }: AddressFormProps) => {
  const { 
    register, 
    handleSubmit, 
    formState: { errors } 
  } = useForm<AddressFormData>({
    resolver: zodResolver(addressSchema),
    mode: 'onBlur',
  });

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate sx={{ width: '100%' }}>
      <TextField
        {...register('address')}
        label="Enter your address"
        placeholder="123 Main St, City, State ZIP"
        error={!!errors.address}
        helperText={errors.address?.message}
        disabled={disabled}
        fullWidth
        autoFocus
        sx={{ mb: 2 }}
      />
      <Button
        type="submit"
        variant="contained"
        disabled={disabled}
        fullWidth
      >
        Find My Representatives
      </Button>
    </Box>
  );
};
