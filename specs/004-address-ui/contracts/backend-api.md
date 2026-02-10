# Backend API Contract: Address Lookup

**Version**: 1.0.0  
**Date**: 2026-02-09  
**Source**: Feature 003-address-lookup OpenAPI specification  
**Audience**: Frontend developers integrating with backend API

---

## Overview

The backend API provides a single endpoint to look up elected representatives by street address. The API integrates with Google Civic Information API and OpenStates.org to resolve addresses and retrieve representative data.

**Base URL**: Set via environment variable `VITE_API_BASE_URL`
- Development: `http://localhost:3000` (local testing)
- Production: TBD (will be API Gateway endpoint)

---

## Endpoint: GET /representatives

### Description

Returns all federal and state representatives for a given US street address.

### Request

**Method**: `GET`

**URL**: `/representatives?address={address}`

**Query Parameters**:
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `address` | string | Yes | Full US residential street address including street number, street name, city, state, and ZIP code | `123 Main St, Seattle, WA 98101` |

**Validation**:
- Must be non-empty after trimming whitespace
- Maximum length: 500 characters
- URL encoding required (use `encodeURIComponent()`)

**Example Request**:
```typescript
const address = "1600 Pennsylvania Ave NW, Washington, DC 20500";
const response = await fetch(
  `${API_BASE_URL}/representatives?address=${encodeURIComponent(address)}`
);
```

---

### Response: Success (200 OK)

**Content-Type**: `application/json`

**Schema**:
```typescript
interface ApiSuccessResponse {
  representatives: Representative[];
  metadata: {
    address: string;              // Echoed input address
    government_levels: string[];  // ['federal', 'state', 'local']
    response_time_ms?: number;    // Optional processing time
  };
  warnings?: string[];            // Optional warnings about missing data
}

interface Representative {
  id: string;                     // Unique OpenStates ID
  name: string;                   // Full name
  office: string;                 // Official title (e.g., "US Senator")
  party: string | null;           // Party affiliation or null
  email: string | null;           // Official email or null
  phone: string | null;           // Phone number or null
  address: string | null;         // Office address or null
  website: string | null;         // Official website URL or null
  photo_url: string | null;       // Photo URL or null (may be broken)
  government_level: 'federal' | 'state' | 'local';
  jurisdiction: string;           // Human-readable district
}
```

**Example Response**:
```json
{
  "representatives": [
    {
      "id": "ocd-person/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "Jane Smith",
      "office": "US Senator",
      "party": "Democratic",
      "email": "senator.smith@senate.gov",
      "phone": "202-555-0100",
      "address": "123 Senate Office Building, Washington, DC 20510",
      "website": "https://smith.senate.gov",
      "photo_url": "https://openstates.org/static/images/smith.jpg",
      "government_level": "federal",
      "jurisdiction": "United States"
    },
    {
      "id": "ocd-person/b2c3d4e5-f6g7-8901-bcde-fg2345678901",
      "name": "John Doe",
      "office": "State Senator - District 12",
      "party": "Republican",
      "email": "john.doe@statehouse.gov",
      "phone": "916-555-0200",
      "address": "State Capitol, Sacramento, CA 95814",
      "website": "https://doe.statehouse.gov",
      "photo_url": null,
      "government_level": "state",
      "jurisdiction": "California State Senate District 12"
    }
  ],
  "metadata": {
    "address": "1600 Pennsylvania Ave NW, Washington, DC 20500",
    "government_levels": ["federal", "state"]
  }
}
```

**Notes**:
- `representatives` array may be empty if no representatives found
- `warnings` array present when some divisions have missing data
- All fields except `id`, `name`, `office`, `government_level`, `jurisdiction` are nullable

---

### Response: Client Error (400 Bad Request)

**When**: Invalid or missing address parameter

**Schema**:
```typescript
interface ApiErrorResponse {
  error: {
    code: string;    // Machine-readable error code
    message: string; // User-friendly error message
    details?: string;// Optional debugging context
  };
}
```

**Error Codes**:
- `MISSING_PARAMETER`: Address parameter not provided
- `INVALID_ADDRESS`: Address exceeds 500 characters or invalid format

**Example Response**:
```json
{
  "error": {
    "code": "MISSING_PARAMETER",
    "message": "Missing required parameter: address",
    "details": "The 'address' query parameter must be provided"
  }
}
```

**Frontend Handling**:
- Display validation error to user
- This should be prevented by client-side validation

---

### Response: Not Found (404)

**When**: Google Civic API could not resolve the address to political divisions

**Example Response**:
```json
{
  "error": {
    "code": "ADDRESS_NOT_FOUND",
    "message": "Unable to find political divisions for the provided address",
    "details": "Google Civic API returned zero divisions for address: '123 Nonexistent St'"
  }
}
```

**Frontend Handling**:
- Display: "No representatives found for this address. Please verify the address and try again."

---

### Response: Internal Server Error (500)

**When**: Unexpected backend error

**Example Response**:
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred while processing your request",
    "details": "NoneType object has no attribute 'get'"
  }
}
```

**Frontend Handling**:
- Display: "Our service is temporarily unavailable. Please try again later."
- Log error details for debugging

---

### Response: Service Unavailable (503)

**When**: External API (Google Civic or OpenStates) is down or rate-limited

**Example Response**:
```json
{
  "error": {
    "code": "EXTERNAL_SERVICE_ERROR",
    "message": "Google Civic API is currently unavailable",
    "details": "Connection timeout after 10 seconds"
  }
}
```

**Frontend Handling**:
- Display: "Our service is temporarily unavailable due to external issues. Please try again in a few minutes."

---

## Integration Example

### Complete useRepresentatives Hook

```typescript
import { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

interface Representative {
  id: string;
  name: string;
  office: string;
  party: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  website: string | null;
  photo_url: string | null;
  government_level: 'federal' | 'state' | 'local';
  jurisdiction: string;
}

interface ApiSuccessResponse {
  representatives: Representative[];
  metadata: {
    address: string;
    government_levels: string[];
    response_time_ms?: number;
  };
  warnings?: string[];
}

interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: string;
  };
}

type AppState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: Representative[] }
  | { status: 'error'; message: string };

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

  return { appState, fetchByAddress, clearResults };
};

// Helper: Map HTTP status + error code to user-friendly messages
const getErrorMessage = (status: number, errorData: ApiErrorResponse): string => {
  const { code, message } = errorData.error;

  switch (status) {
    case 400:
      return 'Please enter a valid US address.';
    case 404:
      return 'No representatives found for this address. Please verify the address and try again.';
    case 500:
      return 'Our service is temporarily unavailable. Please try again later.';
    case 503:
      if (code === 'RATE_LIMIT_EXCEEDED') {
        return 'Service temporarily unavailable due to high demand. Please try again in a few minutes.';
      }
      return 'Our service is experiencing issues. Please try again later.';
    default:
      return message || 'An unexpected error occurred. Please try again.';
  }
};
```

---

## CORS Configuration

**Required for Development**:
- Frontend (localhost:5173 via Vite) must be able to call backend API
- Backend API Gateway must include CORS headers:
  - `Access-Control-Allow-Origin: *` (MVP) or specific origin (production)
  - `Access-Control-Allow-Methods: GET, OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type`

**Production**:
- Update `Access-Control-Allow-Origin` to production frontend domain

---

## Environment Variables

**Frontend (.env file)**:
```bash
# Development
VITE_API_BASE_URL=http://localhost:3000

# Production (example)
VITE_API_BASE_URL=https://api.representapp.example.com
```

**Access in code**:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
```

**Note**: Vite requires `VITE_` prefix for environment variables to be exposed to client code.

---

## Testing

### Test Addresses

Use these addresses for testing various scenarios:

**Success Cases**:
- `1600 Pennsylvania Ave NW, Washington, DC 20500` (White House - federal + DC officials)
- `123 Main Street, Seattle, WA 98101` (Urban area - federal + state + local)
- `456 Oak Avenue, Springfield, IL 62701` (State capital - federal + state)

**Edge Cases**:
- `123 Rural Road, Ruralville, WY 82001` (Rural area - may have warnings for local)
- Very long address (499 characters)
- Address with special characters: `123 O'Malley St, Apt #5-B, City, ST 12345`

**Error Cases**:
- Empty string → 400 MISSING_PARAMETER (should be caught by client validation)
- `123 Fake St` → 404 ADDRESS_NOT_FOUND
- Address > 500 chars → 400 INVALID_ADDRESS (should be caught by client validation)

---

## Rate Limits

**External API Limits** (backend responsibility):
- Google Civic API: 25,000 requests/day
- OpenStates API: 5,000 requests/day

**Frontend Impact**:
- If rate limit exceeded, backend returns 503 with `RATE_LIMIT_EXCEEDED` code
- Display: "Service temporarily unavailable due to high demand. Please try again in a few minutes."

**No client-side rate limiting required in MVP**

---

## Performance Expectations

| Metric | Target | Notes |
|--------|--------|-------|
| Response time (p95) | <3 seconds | Includes Google Civic + OpenStates API calls |
| Response time (cache hit) | <500ms | Not implemented in MVP (no caching) |
| Network timeout | 30 seconds | Recommended client-side timeout |

**Frontend Implementation**:
```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000);

try {
  const response = await fetch(url, { signal: controller.signal });
  clearTimeout(timeoutId);
  // ... handle response
} catch (error) {
  if (error.name === 'AbortError') {
    throw new Error('Request timed out. Please try again.');
  }
  throw error;
}
```

---

## Security Notes

**No Authentication Required** (MVP):
- API is publicly accessible
- No API key or token required
- Rate limiting delegated to external APIs (Google, OpenStates)

**Input Sanitization**:
- Backend sanitizes address parameter before external API calls
- Frontend should still validate and encode properly

**HTTPS**:
- Production API must use HTTPS
- Development may use HTTP (localhost)

---

## Support & Troubleshooting

**Common Issues**:

1. **CORS errors**: Ensure backend CORS headers are configured correctly
2. **404 errors**: Address may not be recognized by Google Civic API (international addresses not supported)
3. **Empty representatives array**: Valid response, display "No representatives found"
4. **Null fields**: Always check for null before displaying (especially `photo_url`, `email`, `phone`)

**Debugging**:
- Check `metadata.response_time_ms` for performance issues
- Log `warnings` array for data coverage gaps
- Verify `VITE_API_BASE_URL` environment variable is set correctly

---

## Related Documentation

- Backend OpenAPI Spec: `/specs/003-address-lookup/contracts/openapi.yaml`
- Backend Feature Spec: `/specs/003-address-lookup/spec.md`
- Frontend Data Model: `/specs/004-address-ui/data-model.md`
