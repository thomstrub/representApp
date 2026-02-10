import type { Representative } from './representative';

/**
 * Success response from GET /representatives
 */
export interface ApiSuccessResponse {
  representatives: Representative[];
  metadata: {
    address: string;
    government_levels: string[];
    response_time_ms?: number;
  };
  warnings?: string[];
}

/**
 * Error response from backend API
 */
export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: string;
  };
}

/**
 * Type guard for API error response
 */
export const isApiErrorResponse = (data: unknown): data is ApiErrorResponse => {
  return (
    typeof data === 'object' &&
    data !== null &&
    'error' in data &&
    typeof (data as { error: unknown }).error === 'object' &&
    (data as { error: unknown }).error !== null &&
    'code' in (data as { error: { code?: unknown } }).error &&
    'message' in (data as { error: { message?: unknown } }).error
  );
};
