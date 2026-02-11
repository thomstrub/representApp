import type { Representative } from './representative';

/**
 * Representatives grouped by government level
 */
export interface GovernmentLevelGroup {
  federal: Representative[];
  state: Representative[];
  local: Representative[];
}

/**
 * Geographic coordinates
 */
export interface Coordinates {
  latitude: number;
  longitude: number;
}

/**
 * Search metadata with context and statistics
 */
export interface Metadata {
  address: string;
  coordinates?: Coordinates;
  total_count: number;
  government_levels: string[];
  response_time_ms?: number;
}

/**
 * Success response from GET /representatives
 */
export interface ApiSuccessResponse {
  representatives: GovernmentLevelGroup;  // Nested structure
  metadata: Metadata;
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
