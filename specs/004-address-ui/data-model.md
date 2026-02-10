# Data Model: Address Lookup UI Components

**Date**: 2026-02-09  
**Purpose**: Define TypeScript types, interfaces, and component models for frontend  
**Input**: Feature spec key entities + backend API contract from feature 003

---

## Type Definitions

### 1. Representative Entity

Primary data model representing an elected official.

```typescript
/**
 * Elected representative information
 * Matches backend API response from feature 003-address-lookup
 */
export interface Representative {
  /** Unique identifier (format: {state}:{ocdId}:{name}) */
  id: string;
  
  /** Full name of the representative */
  name: string;
  
  /** Official title/office (e.g., "U.S. Senator", "State Representative") */
  office: string;
  
  /** Party affiliation (e.g., "Democratic", "Republican", "Independent") */
  party: string;
  
  /** Government level for categorization */
  governmentLevel: 'federal' | 'state' | 'local';
  
  /** Email address (optional) */
  email?: string;
  
  /** Phone number (optional) */
  phone?: string;
  
  /** Physical office address (optional) */
  physicalAddress?: string;
  
  /** Official website URL (optional) */
  website?: string;
  
  /** Photo URL (optional) */
  photoUrl?: string;
}
```

**Validation Rules**:
- `id`: Required, non-empty string
- `name`: Required, 1-200 characters
- `office`: Required, describes elected position
- `party`: Required, common values: "Democratic", "Republican", "Independent", "Nonpartisan"
- `governmentLevel`: Required, one of three values
- Optional fields: May be undefined or empty string in API response

**State Transitions**: None (immutable data from API)

---

### 2. Address Form Input

User input for address lookup.

```typescript
/**
 * Form data for address input
 * Used by React Hook Form
 */
export interface AddressFormData {
  /** User-entered address string */
  address: string;
  
  /** Optional zip code (5 or 9 digits) */
  zipCode?: string;
}

/**
 * Zod validation schema for address form
 */
export const addressSchema = z.object({
  address: z.string()
    .min(1, "Address is required")
    .max(200, "Address must be under 200 characters")
    .trim(),
  zipCode: z.string()
    .regex(/^\d{5}(-\d{4})?$/, "Invalid zip code format (use 12345 or 12345-6789)")
    .optional()
    .or(z.literal('')), // Allow empty string
});

// Infer TypeScript type from Zod schema
export type AddressFormData = z.infer<typeof addressSchema>;
```

**Validation Rules** (from spec FR-002):
- `address`: Required, non-empty string (simple format check)
- `zipCode`: Optional, if provided must match 5-digit or 9-digit with hyphen format
- Validation triggers: on field blur and on form submit

---

### 3. Application State

UI state management for loading, success, error flows.

```typescript
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
export const isLoadingState = (state: AppState): state is { status: 'loading' } => {
  return state.status === 'loading';
};

export const isSuccessState = (state: AppState): state is { status: 'success'; data: Representative[] } => {
  return state.status === 'success';
};

export const isErrorState = (state: AppState): state is { status: 'error'; message: string } => {
  return state.status === 'error';
};
```

**State Transitions**:
```
idle → loading (on form submit)
loading → success (API returns representatives)
loading → error (API fails or validation error)
success → loading (new search)
error → loading (retry)
success/error → idle (clear form)
```

---

### 4. API Response Types

Backend API contract types (from feature 003-address-lookup).

```typescript
/**
 * Success response from GET /api/representatives
 */
export interface ApiSuccessResponse {
  representatives: Representative[];
  address: string;
  timestamp: string; // ISO 8601 format
}

/**
 * Error response from backend API
 */
export interface ApiErrorResponse {
  error: string;
  message: string;
  statusCode: number;
}

/**
 * Type guard for API error response
 */
export const isApiErrorResponse = (data: unknown): data is ApiErrorResponse => {
  return (
    typeof data === 'object' &&
    data !== null &&
    'error' in data &&
    'message' in data
  );
};
```

---

### 5. Grouped Representatives

Data structure for organizing representatives by government level.

```typescript
/**
 * Representatives grouped by government level
 * Used by ResultsDisplay component
 */
export interface GroupedRepresentatives {
  federal: Representative[];
  state: Representative[];
  local: Representative[];
}

/**
 * Helper function to group representatives
 */
export const groupByGovernmentLevel = (representatives: Representative[]): GroupedRepresentatives => {
  return {
    federal: representatives.filter(r => r.governmentLevel === 'federal'),
    state: representatives.filter(r => r.governmentLevel === 'state'),
    local: representatives.filter(r => r.governmentLevel === 'local'),
  };
};

/**
 * Get non-empty sections for display
 */
export const getNonEmptySections = (grouped: GroupedRepresentatives): Array<{
  title: string;
  level: keyof GroupedRepresentatives;
  representatives: Representative[];
}> => {
  return [
    { title: 'Federal Representatives', level: 'federal', representatives: grouped.federal },
    { title: 'State Representatives', level: 'state', representatives: grouped.state },
    { title: 'Local Representatives', level: 'local', representatives: grouped.local },
  ].filter(section => section.representatives.length > 0);
};
```

---

## Component Models

### HomePage Component

**Purpose**: Main application page containing form and results

**Props**: None (root component)

**State**:
```typescript
interface HomePageState {
  appState: AppState;
  submittedAddress: string | null; // For displaying "Results for: [address]"
}
```

**Children**:
- `AddressForm` component
- `LoadingIndicator` component (conditional)
- `ErrorMessage` component (conditional)
- `ResultsDisplay` component (conditional)

---

### AddressForm Component

**Purpose**: Form for address input and submission

**Props**:
```typescript
interface AddressFormProps {
  onSubmit: (data: AddressFormData) => void;
  disabled?: boolean; // Disable during loading
  initialValues?: AddressFormData; // For prefilling
}
```

**Internal State**:
- Managed by React Hook Form: `useForm<AddressFormData>()`
- Validation errors from Zod schema

**Events**:
- `onSubmit`: Fired when form passes validation
- Form validation: on blur and on submit

---

### RepresentativeCard Component

**Purpose**: Display single representative's information

**Props**:
```typescript
interface RepresentativeCardProps {
  representative: Representative;
  elevation?: number; // Material UI Card elevation (default: 2)
}
```

**Conditional Rendering**:
- Photo: Display if `photoUrl` exists, else show initials placeholder
- Contact info: Display if `email`, `phone`, `physicalAddress` exist
- Website: Display if `website` exists as external link

**Accessibility**:
- Card is focusable (keyboard navigation)
- Links have `rel="noopener noreferrer"` for security
- Alt text for images: `{name} - {office}`
- ARIA label for card: `region` with label `{name}, {office}`

---

### ResultsDisplay Component

**Purpose**: Display representatives grouped by government level

**Props**:
```typescript
interface ResultsDisplayProps {
  representatives: Representative[];
  address: string; // Display "Results for: {address}"
}
```

**Layout**:
- Vertically stacked sections (Federal, State, Local)
- Each section: Header (`<Typography variant="h5">`) + Divider + Card grid
- Responsive grid: 12 cols mobile, 6 cols tablet, 4 cols desktop

**Empty State Handling**:
- If section has 0 representatives, don't render that section
- If all sections empty, display: "No representatives found for this address"

---

### ErrorMessage Component

**Purpose**: Display user-friendly error messages

**Props**:
```typescript
interface ErrorMessageProps {
  message: string;
  onRetry?: () => void; // Optional retry button
  onClear?: () => void; // Optional clear button
}
```

**Error Message Mapping**:
```typescript
export const getErrorMessage = (error: unknown): string => {
  if (isApiErrorResponse(error)) {
    // Map API errors to user-friendly messages
    switch (error.statusCode) {
      case 400:
        return 'Please enter a valid US address.';
      case 404:
        return 'No representatives found for this address. Please verify the address and try again.';
      case 500:
        return 'Our service is temporarily unavailable. Please try again later.';
      default:
        return error.message;
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred. Please try again.';
};
```

---

### LoadingIndicator Component

**Purpose**: Display loading state during API call

**Props**:
```typescript
interface LoadingIndicatorProps {
  message?: string; // Default: "Loading representatives..."
  size?: 'small' | 'medium' | 'large'; // CircularProgress size
}
```

**Rendering**:
- Material UI `CircularProgress` component
- Centered on page with message
- Appears within 100ms of state change (per spec SC-008)

---

## Custom Hooks

### useRepresentatives Hook

**Purpose**: Manage API calls for fetching representatives

```typescript
interface UseRepresentativesReturn {
  appState: AppState;
  fetchByAddress: (address: string) => Promise<void>;
  clearResults: () => void;
}

export const useRepresentatives = (): UseRepresentativesReturn => {
  const [appState, setAppState] = useState<AppState>({ status: 'idle' });
  
  const fetchByAddress = async (address: string) => {
    setAppState({ status: 'loading' });
    
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/representatives?address=${encodeURIComponent(address)}`
      );
      
      if (!response.ok) {
        const error: ApiErrorResponse = await response.json();
        throw error;
      }
      
      const data: ApiSuccessResponse = await response.json();
      setAppState({ status: 'success', data: data.representatives });
    } catch (error) {
      const message = getErrorMessage(error);
      setAppState({ status: 'error', message });
    }
  };
  
  const clearResults = () => {
    setAppState({ status: 'idle' });
  };
  
  return { appState, fetchByAddress, clearResults };
};
```

**Error Handling**:
- Network errors: "Unable to connect. Please check your internet connection."
- HTTP errors: Mapped via `getErrorMessage` function
- Timeout: 30 seconds (via AbortController, optional enhancement)

---

## File Organization

```
frontend/src/
├── types/
│   ├── representative.ts      # Representative interface
│   ├── form.ts                # AddressFormData, validation schema
│   ├── state.ts               # AppState, type guards
│   └── api.ts                 # API response types
├── components/
│   ├── AddressForm.tsx        # Form component
│   ├── RepresentativeCard.tsx # Card component
│   ├── ResultsDisplay.tsx     # Results grouping component
│   ├── ErrorMessage.tsx       # Error display component
│   └── LoadingIndicator.tsx   # Loading spinner component
├── pages/
│   └── HomePage.tsx           # Main page component
├── hooks/
│   └── useRepresentatives.ts  # API hook
└── utils/
    ├── grouping.ts            # groupByGovernmentLevel helper
    └── errors.ts              # getErrorMessage helper
```

---

## Relationships

```
HomePage
├── AddressForm (onSubmit → fetchByAddress)
├── LoadingIndicator (if appState.status === 'loading')
├── ErrorMessage (if appState.status === 'error')
└── ResultsDisplay (if appState.status === 'success')
    └── RepresentativeCard[] (foreach representative)

useRepresentatives hook
├── fetch API call → Backend API (feature 003)
└── appState management → HomePage component
```

---

## Testing Models

### Unit Test Coverage

**Components**:
1. `AddressForm`: Test validation, submit handling, disabled state
2. `RepresentativeCard`: Test with/without optional fields, photo fallback (initials)
3. `ResultsDisplay`: Test grouping, empty sections, responsive grid
4. `ErrorMessage`: Test different error types, retry button
5. `LoadingIndicator`: Test rendering, message display

**Hooks**:
1. `useRepresentatives`: Mock fetch, test loading/success/error states

**Utilities**:
1. `groupByGovernmentLevel`: Test with various representative arrays
2. `getErrorMessage`: Test with various error types
3. `addressSchema`: Test validation with valid/invalid inputs

### Integration Test Coverage

1. **Complete Flow**: Form submit → Loading → Results display
2. **Error Flow**: Form submit → Loading → Error message → Retry
3. **Clear Flow**: Results display → Clear button → Form reset
4. **Responsive Layout**: Test grid at different breakpoints

---

## Dependencies Summary

**Runtime Dependencies**:
- `@mui/material` `@emotion/react` `@emotion/styled` - UI components
- `@mui/icons-material` - Icons for cards
- `react-hook-form` - Form state management
- `@hookform/resolvers` - Zod integration
- `zod` - Schema validation

**Dev Dependencies**:
- `@testing-library/react` - Component testing
- `@testing-library/jest-dom` - DOM matchers
- `@testing-library/user-event` - User interaction testing
- `vitest` - Test runner
- `jsdom` - DOM environment

---

## Next Steps

1. → Generate contracts/ (backend API contract documentation)
2. → Generate quickstart.md (setup instructions, component usage examples)
3. → Update agent context with React + TypeScript patterns
