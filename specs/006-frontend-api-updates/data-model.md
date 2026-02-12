# Data Model: Frontend API Integration Updates

**Feature**: Frontend API Integration Updates  
**Date**: 2026-02-10  
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data entities and relationships for the updated frontend API integration. The primary change is consuming a nested API response structure where representatives are pre-grouped by government level (federal, state, local) instead of receiving a flat array.

## Entities

### 1. Representative

**Description**: An elected or appointed government official representing a geographic area or constituency.

**Source**: Backend API (unchanged from previous implementation)

**Properties**:

| Field | Type | Required | Description | Validation Rules | Example |
|-------|------|----------|-------------|-----------------|---------|
| `id` | string | Yes | Unique identifier from Open Civic Data | Non-empty string, format: `ocd-*` | `"ocd-division/country:us/state:ca"` |
| `name` | string | Yes | Full legal name of representative | Non-empty string | `"Nancy Pelosi"` |
| `office` | string | Yes | Official title or office held | Non-empty string | `"U.S. Representative"` |
| `party` | string \| null | No | Political party affiliation | One of: "Democratic", "Republican", "Independent", null | `"Democratic"` |
| `government_level` | enum | Yes | Level of government | One of: `"federal"`, `"state"`, `"local"` | `"federal"` |
| `jurisdiction` | string | Yes | Geographic area or district served | Non-empty string | `"California's 11th District"` |
| `email` | string \| null | No | Official email address | Valid email format or null | `"contact@example.gov"` |
| `phone` | string \| null | No | Official phone number | Phone format or null | `"(202) 555-0100"` |
| `address` | string \| null | No | Physical office address | Address string or null | `"123 Capitol St, DC 20001"` |
| `website` | string \| null | No | Official website URL | Valid URL or null | `"https://example.gov"` |
| `photo_url` | string \| null | No | URL to official photo | Valid URL or null | `"https://cdn.example.com/photo.jpg"` |

**State Transitions**: None (immutable data from API)

**Relationships**:
- Belongs to one `GovernmentLevelGroup` (federal, state, or local)
- Associated with one `Metadata` object (via API response)

---

### 2. GovernmentLevelGroup

**Description**: A collection of representatives serving at the same government level (federal, state, or local). This is the new grouping structure provided by the backend API.

**Source**: Backend API (new nested structure)

**Properties**:

| Field | Type | Required | Description | Validation Rules | Example |
|-------|------|----------|-------------|-----------------|---------|
| `federal` | Representative[] | Yes | Array of federal representatives | Array (may be empty) | `[{...rep1}, {...rep2}]` |
| `state` | Representative[] | Yes | Array of state representatives | Array (may be empty) | `[{...rep3}, {...rep4}]` |
| `local` | Representative[] | Yes | Array of local representatives | Array (may be empty) | `[{...rep5}]` |

**Validation Rules**:
- All three arrays must be present (even if empty)
- Each array contains only `Representative` objects
- Representatives should not appear in multiple arrays (enforced by backend, assumed by frontend)

**Relationships**:
- Contains multiple `Representative` entities
- Part of `ApiSuccessResponse`

---

### 3. Metadata

**Description**: Contextual information about the representative search, including the resolved address, geographic coordinates, and summary statistics.

**Source**: Backend API (enhanced with new fields)

**Properties**:

| Field | Type | Required | Description | Validation Rules | Example |
|-------|------|----------|-------------|-----------------|---------|
| `address` | string | Yes | Normalized/resolved address that was searched | Non-empty string | `"1600 Pennsylvania Avenue NW, Washington, DC 20500"` |
| `coordinates` | Coordinates \| null | No | Geographic coordinates of the address | Valid lat/lng or null | `{latitude: 38.8977, longitude: -77.0365}` |
| `total_count` | number | Yes | Total number of representatives across all levels | Non-negative integer | `15` |
| `government_levels` | string[] | Yes | List of government levels with results | Array of strings (may be empty) | `["federal", "state"]` |
| `response_time_ms` | number | No | Backend processing time in milliseconds | Positive integer | `234` |

**Relationships**:
- Part of `ApiSuccessResponse`
- Associated with all `Representative` entities in the response

**Display Requirements**:
- `address` should be prominently displayed to confirm search location
- `total_count` should be shown in a summary (e.g., "Found 15 representatives")
- `government_levels` can be used to show which levels have results
- `coordinates` can be used for future map features (not MVP)

---

### 4. Coordinates

**Description**: Geographic coordinates (latitude/longitude) for the searched address.

**Source**: Backend API metadata

**Properties**:

| Field | Type | Required | Description | Validation Rules | Example |
|-------|------|----------|-------------|-----------------|---------|
| `latitude` | number | Yes | Latitude coordinate | -90 to 90 | `38.8977` |
| `longitude` | number | Yes | Longitude coordinate | -180 to 180 | `-77.0365` |

**Usage**: Future enhancement for map-based interface (not MVP)

---

### 5. Warning

**Description**: A message indicating data limitations or incomplete results from the backend.

**Source**: Backend API warnings array

**Properties**:

| Field | Type | Required | Description | Validation Rules | Example |
|-------|------|----------|-------------|-----------------|---------|
| (array item) | string | N/A | Plain text warning message | Non-empty string | `"Local representatives data may be incomplete for this address"` |

**Display Requirements**:
- Must be shown in a visually distinct component (Material UI Alert with severity="warning")
- Should appear above the representative results to ensure visibility
- Multiple warnings should be displayed as separate alert items

---

### 6. ApiSuccessResponse

**Description**: The top-level successful response structure from the backend API.

**Source**: Backend API

**Structure**:

```typescript
interface ApiSuccessResponse {
  representatives: GovernmentLevelGroup;  // Nested structure
  metadata: Metadata;
  warnings?: string[];  // Optional array
}
```

**Properties**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `representatives` | GovernmentLevelGroup | Yes | Representatives grouped by government level |
| `metadata` | Metadata | Yes | Search context and statistics |
| `warnings` | string[] | No | Data limitation messages (if any) |

**Validation Rules**:
- All required fields must be present
- `representatives` object must have all three level arrays (federal, state, local) even if empty
- `metadata.total_count` should equal the sum of representatives across all levels (backend guarantees this)
- If `warnings` is present, it must be a non-empty array

---

### 7. ApiErrorResponse

**Description**: Error response structure from the backend API (unchanged).

**Source**: Backend API

**Structure**:

```typescript
interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: string;
  };
}
```

**Properties**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `error.code` | string | Yes | Error code identifier | `"INVALID_ADDRESS"` |
| `error.message` | string | Yes | User-friendly error message | `"Could not find representatives for this address"` |
| `error.details` | string | No | Technical details for debugging | `"Geocoding failed: address not found"` |

**Type Guard**: Use `isApiErrorResponse(data)` to differentiate from success response.

---

## Entity Relationships

```
ApiSuccessResponse
├── representatives: GovernmentLevelGroup
│   ├── federal: Representative[]
│   ├── state: Representative[]
│   └── local: Representative[]
├── metadata: Metadata
│   └── coordinates?: Coordinates
└── warnings?: string[]
```

**Key Relationships**:
1. **One-to-One**: ApiSuccessResponse → Metadata (every response has exactly one metadata object)
2. **One-to-One**: ApiSuccessResponse → GovernmentLevelGroup (every response has exactly one grouping object)
3. **One-to-Many**: GovernmentLevelGroup → Representative (groups contain 0 or more representatives per level)
4. **One-to-Zero-or-One**: Metadata → Coordinates (coordinates may be absent)
5. **One-to-Zero-or-Many**: ApiSuccessResponse → Warning (0 or more warnings per response)

---

## Data Flow

### 1. API Request → Response

```
User enters address
    ↓
Frontend sends GET /representatives?address=...
    ↓
Backend returns ApiSuccessResponse | ApiErrorResponse
    ↓
Frontend parses response with type guards
    ↓
useRepresentatives hook stores data in state
    ↓
ResultsDisplay component renders grouped data
```

### 2. State Management

**Current State** (React useState in `useRepresentatives` hook):

```typescript
const [data, setData] = useState<ApiSuccessResponse | null>(null);
const [loading, setLoading] = useState<boolean>(false);
const [error, setError] = useState<string | null>(null);
```

**Data Transformations**:
- **Before**: API response (flat array) → `groupByGovernmentLevel()` → grouped data → render
- **After**: API response (pre-grouped) → direct render (no transformation needed)

---

## Validation Strategy

### Compile-Time Validation (TypeScript)
- Strict mode enabled (`strict: true` in tsconfig.json)
- All interfaces defined with exact required/optional fields
- Type guards for error responses: `isApiErrorResponse(data)`
- No `any` types allowed

### Runtime Validation (Optional)
- Could use Zod schemas for API response validation (currently only used for form validation)
- Not strictly necessary due to backend contract guarantees
- Consider adding if API stability is a concern

### UI Validation
- Empty arrays: Show "No {level} representatives found" message per level
- Null fields: Conditional rendering (`{field && <Component />}`)
- Missing photo: Fallback to initials avatar
- Missing contact info: Don't render contact section

---

## Migration from Old Structure

### Old API Response Structure (Before)

```typescript
interface OldApiResponse {
  address: string;  // Top-level address field
  representatives: Representative[];  // Flat array
  metadata: {
    address: string;
    division_count: number;
    representative_count: number;
    government_levels: string[];
    response_time_ms?: number;
  };
  warnings?: string[];
}
```

### New API Response Structure (After)

```typescript
interface NewApiResponse {
  representatives: {  // Nested object
    federal: Representative[];
    state: Representative[];
    local: Representative[];
  };
  metadata: {
    address: string;
    coordinates?: { latitude: number; longitude: number };  // New field
    total_count: number;  // Renamed from representative_count
    government_levels: string[];
    response_time_ms?: number;
  };
  warnings?: string[];
}
```

### Key Differences

| Aspect | Old Structure | New Structure | Impact |
|--------|---------------|---------------|--------|
| Representatives | Flat array | Nested by level | Remove client-side grouping |
| Top-level address | `response.address` | Removed | Use `metadata.address` instead |
| Representative count | `metadata.representative_count` | `metadata.total_count` | Update field access |
| Division count | `metadata.division_count` | Removed | No longer needed (can derive from representatives) |
| Coordinates | Not present | `metadata.coordinates` | New feature opportunity |

---

## Testing Data Requirements

### Test Fixtures Needed

1. **Full Response** (all three levels populated):
```typescript
{
  representatives: {
    federal: [rep1, rep2],
    state: [rep3, rep4, rep5],
    local: [rep6]
  },
  metadata: {...},
  warnings: []
}
```

2. **Partial Response** (only federal and state):
```typescript
{
  representatives: {
    federal: [rep1],
    state: [rep2],
    local: []  // Empty array
  },
  metadata: {...}
  // No warnings
}
```

3. **Empty Response** (no representatives):
```typescript
{
  representatives: {
    federal: [],
    state: [],
    local: []
  },
  metadata: {
    address: "123 Main St",
    total_count: 0,
    government_levels: []
  },
  warnings: ["Could not find representatives for this address"]
}
```

4. **Error Response**:
```typescript
{
  error: {
    code: "INVALID_ADDRESS",
    message: "Invalid address format"
  }
}
```

5. **Representative with Missing Optional Fields**:
```typescript
{
  id: "ocd-...",
  name: "John Doe",
  office: "State Senator",
  party: null,  // No party
  government_level: "state",
  jurisdiction: "District 5",
  // All contact fields omitted (or null)
}
```

---

## Performance Considerations

### Data Size Estimates
- **Typical response**: 10-50 representatives (~20KB JSON)
- **Large response**: 100+ representatives (~100KB JSON)
- **Parsing time**: <10ms for typical responses
- **Render time**: <100ms for typical responses (with pre-grouped data)

### Optimization Opportunities
- **Memoization**: Use `React.useMemo` for expensive calculations (e.g., counting representatives if not using metadata.total_count)
- **Lazy loading**: Not needed for MVP (single-page display)
- **Virtualization**: Not needed for MVP (representative count typically <50)

---

## Future Enhancements

### Near-Term (Post-MVP)
1. **Map Interface**: Use `metadata.coordinates` to display representatives on an interactive map
2. **Filtering**: Allow users to filter by party, office type, or jurisdiction
3. **Sorting**: Sort representatives by name, office, or party within each level
4. **Search**: Search representatives by name within results

### Long-Term
1. **Representative Details Page**: Click representative → full profile with voting record, bills sponsored, etc.
2. **Comparison View**: Compare multiple representatives side-by-side
3. **Contact Tracking**: Track when users contact representatives (requires backend updates)

---

## References

- [Feature Specification](spec.md)
- [Research Document](research.md)
- [API Contract Schema](contracts/api-response.schema.json)
- [Backend Implementation](../../backend/README.md)
