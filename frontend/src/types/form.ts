import { z } from 'zod';

/**
 * Zod validation schema for address form
 */
export const addressSchema = z.object({
  address: z.string()
    .min(1, "Address is required")
    .max(200, "Address must be under 200 characters")
    .trim(),
});

/**
 * Form data for address input
 * Inferred from Zod schema
 */
export type AddressFormData = z.infer<typeof addressSchema>;
