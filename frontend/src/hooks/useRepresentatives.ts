import { useState } from 'react';
import type { AppState } from '../types/state';
import type { ApiSuccessResponse, ApiErrorResponse } from '../types/api';
import { getErrorMessage } from '../utils/errors';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const useRepresentatives = () => {
  const [appState, setAppState] = useState<AppState>({ status: 'idle' });

  const fetchByAddress = async (address: string) => {
    setAppState({ status: 'loading' });

    try {
      const url = `${API_BASE_URL}/representatives?address=${encodeURIComponent(address)}`;
      const response = await fetch(url);

      if (!response.ok) {
        const errorData: ApiErrorResponse = await response.json();
        throw new Error(getErrorMessage(response.status, errorData));
      }

      const apiResponse: ApiSuccessResponse = await response.json();
      
      // Log warnings if present (for debugging)
      if (apiResponse.warnings) {
        console.warn('API warnings:', apiResponse.warnings);
      }

      // Flatten the nested structure into a single array for backward compatibility
      const representatives = [
        ...apiResponse.representatives.federal,
        ...apiResponse.representatives.state,
        ...apiResponse.representatives.local,
      ];

      setAppState({ 
        status: 'success', 
        data: representatives,
        metadata: apiResponse.metadata,
        warnings: apiResponse.warnings,
      });
    } catch (error) {
      const message = error instanceof Error 
        ? error.message 
        : 'An unexpected error occurred. Please try again.';
      setAppState({ status: 'error', message });
    }
  };

  const clearResults = () => {
    setAppState({ status: 'idle' });
  };

  return {
    appState,
    fetchByAddress,
    clearResults,
  };
};
