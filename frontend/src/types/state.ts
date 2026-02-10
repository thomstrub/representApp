import { Representative } from './representative';

/**
 * Application state for representative lookup flow
 */
export type AppState = 
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: Representative[] }
  | { status: 'error'; message: string };

/**
 * Type guards for state discrimination
 */
export const isIdleState = (state: AppState): state is { status: 'idle' } => {
  return state.status === 'idle';
};

export const isLoadingState = (state: AppState): state is { status: 'loading' } => {
  return state.status === 'loading';
};

export const isSuccessState = (state: AppState): state is { status: 'success'; data: Representative[] } => {
  return state.status === 'success';
};

export const isErrorState = (state: AppState): state is { status: 'error'; message: string } => {
  return state.status === 'error';
};
