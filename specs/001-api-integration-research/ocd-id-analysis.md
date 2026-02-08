# OCD-ID Integration Analysis - Phase 4 Research Results

**Date**: February 7, 2026  
**Tasks**: T015-T023  
**Status**: ⚠️ API Deprecation Discovered - Strategy Adjustment Required

## Critical Finding: Google Civic Representatives API Deprecated

### API Status Discovery

**Google Civic Information API Representatives Endpoint**:
- **Status**: ❌ DEPRECATED (Shut down April 2025)
- **Tested**: February 7, 2026  
- **Result**: All requests return 404 Not Found
- **Impact**: Cannot use for address-to-representative lookups

**Evidence**:
```bash
# All test addresses returned 404
404 Client Error: Not Found for url: https://www.googleapis.com/civicinfo/v2/representatives
```

**Google's Official Statement** (from research):
> "We will be turning down the Representatives API next year in April 2025. This API gives developers the ability to identify the elected representatives for a residential address or division. When we first launched the API 10 years ago, there was limited offering of political representation data in the civic information ecosystem. Today, there are alternate providers who are able to serve authoritative representation data directly to developers."

### What Still Works

✅ **Google Civic Information API `/divisions` endpoint**:
- **Status**: ACTIVE
- **Purpose**: Browse/search OCD division IDs
- **Limitation**: Returns ALL US divisions (~4,595), not address-specific
- **Use Case**: OCD-ID reference/lookup table

✅ **OpenStates.org API v3**:
- **Status**: ACTIVE (verified T005, T006)
- **Endpoint**: `https://v3.openstates.org/people`
- **Rate Limit**: 5,000 requests/day (free tier)
- **Capabilities**: Lookup legislators by OCD division ID

## Revised Integration Strategy

### Original Plan (Based on Pre-Deprecation Patterns)
1. User enters address → Google Civic API
2. Get OCD-IDs + representatives in one call
3. Display results

**Problem**: Step 2 no longer possible (API deprecated)

### Updated MVP Architecture

#### **Option A: OpenStates-First Approach** (Recommended)
```
1. User enters address or zip code
2. Frontend geocodes address → lat/long (Google Maps Geocoding API)
3. Determine state from geocoded result
4. Query OpenStates API with state filter
5. User selects their district from list (or we pre-filter if zip/district known)
6. Display representatives from OpenStates
```

**Pros**:
- Single API dependency (OpenStates)
- Clear API documentation
- Active community support
- 5,000 req/day sufficient for MVP

**Cons**:
- Requires district selection step (UX friction)
- No direct address-to-OCD-ID mapping
- Limited to state/federal (no county/local)

#### **Option B: Hybrid Geocoding + OpenStates**
```
1. User enters address
2. Google Maps Geocoding API → lat/long + address components
3. Extract state, county, city from geocoded result
4. Manual OCD-ID construction:
   - Federal: ocd-division/country:us
   - State: ocd-division/country:us/state:{state_abbr}
   - Lookup congressional district via census data or third-party API
5. Query OpenStates with constructed OCD-IDs
6. Display representatives
```

**Pros**:
- Better UX (no district selection needed if we can infer)
- Combines geocoding strength with OpenStates data
- More accurate than user selection

**Cons**:
- Complex OCD-ID construction logic
- Need congressional district lookup (Census API or separate service)
- Multiple API dependencies

#### **Option C: Pre-Built OCD-ID Mapping Database**
```
1. Build address → OCD-ID mapping from Census data + Google's OCD-ID spec
2. Store in DynamoDB with zip code index
3. User enters zip code → Lookup in DynamoDB
4. Query OpenStates with OCD-IDs
5. Display representatives
```

**Pros**:
- Fast lookups (DynamoDB)
- No runtime dependency on deprecated APIs
- Zip code-based search is simple UX

**Cons**:
- Requires initial data pipeline to build mappings
- Zip codes can span multiple districts
- Data maintenance burden

## OCD-ID Structure Documentation (From Research)

Based on analysis of 3 GitHub repositories and Google's OCD-ID specification:

### OCD-ID Format
```
ocd-division/country:{country}/state:{state}/{division_type}:{identifier}
```

### Components

| Component | Description | Example | Required |
|-----------|-------------|---------|----------|
| `country` | ISO 3166-1 alpha-2 country code | `us` | Yes |
| `state` | 2-letter state abbreviation (lowercase) | `wa` | For US |
| `division_type` | Type of division | `cd`, `sldl`, `sldu`, `county`, `place` | Optional |
| `identifier` | District number or name | `7`, `43`, `king`, `seattle` | With type |

### Division Types

| Type | Meaning | Example | Level |
|------|---------|---------|-------|
| `cd` | Congressional District | `ocd-division/country:us/state:wa/cd:7` | Federal |
| `sldu` | State Legislature Upper (Senate) | `ocd-division/country:us/state:wa/sldu:43` | State |
| `sldl` | State Legislature Lower (House) | `ocd-division/country:us/state:wa/sldl:43` | State |
| `county` | County | `ocd-division/country:us/state:wa/county:king` | County |
| `place` | City/Town | `ocd-division/country:us/state:wa/place:seattle` | Local |
| *(none)* | State-wide | `ocd-division/country:us/state:wa` | State |
| *(none)* | Federal | `ocd-division/country:us` | Federal |

### Parsing Rules (Python Implementation)

```python
import re
from typing import Dict, Optional

def parse_ocd_id(ocd_id: str) -> Dict[str, Optional[str]]:
    """
    Parse OCD-ID into components
    
    Args:
        ocd_id: OCD division identifier
        
    Returns:
        Dictionary with parsed components:
        - country: Country code (e.g., 'us')
        - state: State abbreviation (e.g., 'wa')
        - division_type: Type of division ('cd', 'sldu', 'sldl', 'county', 'place')
        - identifier: District number or name
        - level: Government level ('federal', 'state', 'state_legislature', 
                 'federal_congress', 'county', 'local')
    """
    if not ocd_id.startswith('ocd-division/'):
        raise ValueError(f"Invalid OCD-ID format: {ocd_id}")
    
    # Remove prefix
    parts = ocd_id.replace('ocd-division/', '').split('/')
    
    components = {}
    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            components[key] = value
    
    # Determine government level
    if 'place' in components:
        components['level'] = 'local'
    elif 'county' in components:
        components['level'] = 'county'
    elif 'sldl' in components or 'sldu' in components:
        components['level'] = 'state_legislature'
        components['division_type'] = 'sldl' if 'sldl' in components else 'sldu'
        components['identifier'] = components.get('sldl') or components.get('sldu')
    elif 'cd' in components:
        components['level'] = 'federal_congress'
        components['division_type'] = 'cd'
        components['identifier'] = components['cd']
    elif 'state' in components and len(components) == 2:
        components['level'] = 'state'
    elif len(components) == 1:
        components['level'] = 'federal'
    else:
        components['level'] = 'other'
    
    return components

# Example usage
examples = [
    "ocd-division/country:us",
    "ocd-division/country:us/state:wa",
    "ocd-division/country:us/state:wa/cd:7",
    "ocd-division/country:us/state:wa/sldu:43",
    "ocd-division/country:us/state:wa/sldl:43",
    "ocd-division/country:us/state:wa/county:king",
    "ocd-division/country:us/state:wa/place:seattle",
]

for ocd_id in examples:
    parsed = parse_ocd_id(ocd_id)
    print(f"{ocd_id}")
    print(f"  → Level: {parsed['level']}")
    print(f"  → State: {parsed.get('state', 'N/A')}")
    if 'division_type' in parsed:
        print(f"  → Type: {parsed['division_type']}, ID: {parsed['identifier']}")
    print()
```

### OCD-ID Construction (For Option B)

```python
def construct_cd_ocd_id(state_abbr: str, district: int) -> str:
    """
    Construct Congressional District OCD-ID
    
    Args:
        state_abbr: 2-letter state code (lowercase)
        district: District number (1-based)
        
    Returns:
        OCD-ID string
        
    Example:
        >>> construct_cd_ocd_id('wa', 7)
        'ocd-division/country:us/state:wa/cd:7'
    """
    return f"ocd-division/country:us/state:{state_abbr.lower()}/cd:{district}"

def construct_state_leg_ocd_id(state_abbr: str, chamber: str, district: int) -> str:
    """
    Construct State Legislature OCD-ID
    
    Args:
        state_abbr: 2-letter state code (lowercase)
        chamber: 'upper' (Senate) or 'lower' (House)
        district: District number
        
    Returns:
        OCD-ID string
        
    Example:
        >>> construct_state_leg_ocd_id('wa', 'upper', 43)
        'ocd-division/country:us/state:wa/sldu:43'
    """
    chamber_code = 'sldu' if chamber == 'upper' else 'sldl'
    return f"ocd-division/country:us/state:{state_abbr.lower()}/{chamber_code}:{district}"

def construct_county_ocd_id(state_abbr: str, county_name: str) -> str:
    """
    Construct County OCD-ID
    
    Args:
        state_abbr: 2-letter state code (lowercase)
        county_name: County name (lowercase, underscores for spaces)
        
    Returns:
        OCD-ID string
        
    Example:
        >>> construct_county_ocd_id('wa', 'king')
        'ocd-division/country:us/state:wa/county:king'
    """
    normalized_name = county_name.lower().replace(' ', '_')
    return f"ocd-division/country:us/state:{state_abbr.lower()}/county:{normalized_name}"
```

## Integration Testing Results (T015-T020)

### Test Execution Summary

| Task | Address Type | Status | Notes |
|------|--------------|--------|-------|
| T015 | Urban Seattle | ❌ 404 | Representatives API deprecated |
| T016 | Rural Spokane | ❌ 404 | Representatives API deprecated |
| T017 | Zip Code Only | ❌ 404 | Representatives API deprecated |
| T018 | Military APO | ❌ 404 | Representatives API deprecated |
| T019 | PO Box | ❌ 404 | Representatives API deprecated |
| T020 | Multi-state (4 addresses) | ❌ 404 | Representatives API deprecated |

**Conclusion**: Cannot test address-to-OCD-ID mapping with Google Civic API. Must use alternative approach.

### Alternative Testing via OpenStates

Since Google Civic Representatives API is deprecated, we can verify OCD-ID structure using OpenStates API:

```bash
# Test: Get all Washington state legislators
curl "https://v3.openstates.org/people?jurisdiction=ocd-jurisdiction/country:us/state:wa/government&per_page=10" \
  -H "X-API-Key: YOUR_KEY"

# Expected response includes OCD-IDs for each person:
# {
#   "id": "ocd-person/...",
#   "name": "Senator Name",
#   "current_role": {
#     "division_id": "ocd-division/country:us/state:wa/sldu:43",
#     "title": "Senator",
#     "district": "43"
#   }
# }
```

## Recommendations for MVP

### Immediate Actions (Updated Tasks)

1. **T015-T020 Status**: ⚠️ **Cannot Complete as Originally Specified**
   - Reason: Google Civic Representatives API deprecated
   - Alternative: Use OpenStates API patterns from research (already documented)

2. **T021-T023 (OCD-ID Analysis)**:   - ✅ Can complete using research from repositories
   - Document OCD-ID structure (completed above)
   - Document parsing rules (completed above)
   - Document integration patterns with OpenStates (from repo analysis)

### Updated MVP Implementation Plan

**Phase 1: MVP with State Selection (Simplest)**
```
User Flow:
1. User selects state from dropdown (WA)
2. App queries OpenStates: GET /people?jurisdiction=ocd-jurisdiction/country:us/state:wa/government
3. Display all state legislators grouped by chamber and district
4. User can filter by district if desired
```

**Phase 2: Add Zip Code Lookup (Enhanced)**
```
User Flow:
1. User enters zip code (98101)
2. Backend uses zip→district mapping (pre-built from Census data)
3. Query OpenStates with specific OCD-IDs
4. Display representatives for that district
```

**Phase 3: Full Address Lookup (Future)**
```
User Flow:
1. User enters full address
2. Geocode to lat/long
3. Reverse lookup district from geometry (requires Census API integration)
4. Query OpenStates
5. Display representatives
```

### Required Changes to Spec

1. **Update spec.md**: Remove reliance on Google Civic Representatives API
2. **Primary API**: OpenStates.org API v3 (already registered and verified)
3. **Address-to-District**: Defer to Phase 2/3, use state selection for MVP
4. **OCD-ID Source**: Use OpenStates API response (includes division_id)

## Conclusion

**T015-T020 Assessment**: ✅ Research complete, but approach adjusted due to API deprecation  
**T021-T023 Status**: ✅ Can complete with existing research and OpenStates patterns  
**Impact**: MVP architecture must use OpenStates-first approach, not Google Civic  
**Decision Point**: Choose Option A (simplest), Option B (better UX), or Option C (best UX, more work)

**Next Steps**:
1. Update spec.md with revised architecture (Option A recommended for MVP)
2. Document OpenStates integration patterns (T021-T023)
3. Create prototype API handler using OpenStates
4. Test with Washington state data
