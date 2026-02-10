import { ApiErrorResponse } from '../types/api';

/**
 * Map HTTP status codes and API errors to user-friendly messages
 * @param statusCode - HTTP status code
 * @param errorData - Optional error response from API
 * @returns User-friendly error message
 */
export const getErrorMessage = (
  statusCode: number,
  errorData?: ApiErrorResponse
): string => {
  // Use API message if available
  if (errorData?.error?.message) {
    return errorData.error.message;
  }

  // Fallback to status code mapping
  switch (statusCode) {
    case 400:
      return 'Invalid address format. Please check your address and try again.';
    case 404:
      return 'No representatives found for this address. Please verify the address and try again.';
    case 500:
      return 'Our service is temporarily unavailable. Please try again later.';
    case 503:
      return 'Our service is temporarily unavailable due to external issues. Please try again in a few minutes.';
    default:
      return 'An unexpected error occurred. Please try again.';
  }
};
