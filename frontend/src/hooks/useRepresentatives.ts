import { useState } from 'react';
import { AppState } from '../types/state';
import { ApiSuccessResponse, ApiErrorResponse } from '../types/api';
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

      const data: ApiSuccessResponse = await response.json();
      
      // Log warnings if present (for debugging)
      if (data.warnings) {
        console.warn('API warnings:', data.warnings);
      }

      setAppState({ status: 'success', data: data.representatives });
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
