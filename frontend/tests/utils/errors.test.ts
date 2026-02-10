import { describe, it, expect } from 'vitest';
import { getErrorMessage } from '../../src/utils/errors';
import { ApiErrorResponse } from '../../src/types/api';

describe('getErrorMessage', () => {
  it('should return API error message when provided', () => {
    const errorData: ApiErrorResponse = {
      error: {
        code: 'ADDRESS_NOT_FOUND',
        message: 'Unable to find political divisions for the provided address',
        details: 'Google Civic API returned zero divisions',
      },
    };

    const message = getErrorMessage(404, errorData);
    expect(message).toBe('Unable to find political divisions for the provided address');
  });

  it('should return user-friendly message for 400 status', () => {
    const message = getErrorMessage(400);
    expect(message).toBe('Invalid address format. Please check your address and try again.');
  });

  it('should return user-friendly message for 404 status', () => {
    const message = getErrorMessage(404);
    expect(message).toBe('No representatives found for this address. Please verify the address and try again.');
  });

  it('should return user-friendly message for 500 status', () => {
    const message = getErrorMessage(500);
    expect(message).toBe('Our service is temporarily unavailable. Please try again later.');
  });

  it('should return user-friendly message for 503 status', () => {
    const message = getErrorMessage(503);
    expect(message).toBe('Our service is temporarily unavailable due to external issues. Please try again in a few minutes.');
  });

  it('should return generic message for unknown status codes', () => {
    const message = getErrorMessage(418);
    expect(message).toBe('An unexpected error occurred. Please try again.');
  });

  it('should prefer API message over status code fallback', () => {
    const errorData: ApiErrorResponse = {
      error: {
        code: 'CUSTOM_ERROR',
        message: 'Custom API error message',
      },
    };

    const message = getErrorMessage(500, errorData);
    expect(message).toBe('Custom API error message');
  });
});
