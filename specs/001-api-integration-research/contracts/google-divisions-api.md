# API Contract: Google Civic Information API (Divisions Endpoint)

**Provider**: Google Civic Information API  
**Version**: v2  
**Documentation**: https://developers.google.com/civic-information/docs/v2  
**Base URL**: `https://www.googleapis.com/civicinfo/v2`

**Note**: The Representatives By Address endpoint is deprecated (April 2025). This contract documents ONLY the divisions endpoint for OCD-ID resolution.

## Authentication

**Method**: API Key (Query Parameter)

```http
GET /divisions?key=YOUR_API_KEY_HERE
```

**Registration**: Free tier available at Google Cloud Console

## Endpoints

### 1. Get Divisions (OCD-ID Resolution)

**Purpose**: Query for political geography and Open Civic Data divisions by latitude/longitude or query string

```http
GET /divisions?query={query}&key={api_key}
```

**Query Parameters**:
- `query` (optional): Address or location string (e.g., "1600 Pennsylvania Ave, Washington, DC")
- `key` (required): Google API key

**Request Example** (By Address):
```http
GET https://www.googleapis.com/civicinfo/v2/divisions?query=340+N+Escondido+Blvd%2C+Escondido%2C+CA+92025&key=YOUR_API_KEY_HERE
```

**Response Example** (200 OK):
```json
{
  "kind": "civicinfo#divisionSearchResponse",
  "results": [
    {
      "ocdId": "ocd-division/country:us",
      "name": "United States",
      "aliases": ["USA"]
    },
    {
      "ocdId": "ocd-division/country:us/state:ca",
      "name": "California",
      "aliases": ["CA", "State of California"]
    },
    {
      "ocdId": "ocd-division/country:us/state:ca/cd:49",
      "name": "California's 49th Congressional District"
    },
    {
      "ocdId": "ocd-division/country:us/state:ca/sldl:76",
      "name": "California State Assembly District 76"
    },
    {
      "ocdId": "ocd-division/country:us/state:ca/sldu:38",
      "name": "California State Senate District 38"
    },
    {
      "ocdId": "ocd-division/country:us/state:ca/county:san_diego",
      "name": "San Diego County"
    },
    {
      "ocdId": "ocd-division/country:us/state:ca/place:escondido",
      "name": "Escondido city"
    }
  ]
}
```

**Request Example** (By Zip Code):
```http
GET https://www.googleapis.com/civicinfo/v2/divisions?query=98101&key=YOUR_API_KEY_HERE
```

**Response Example** (200 OK):
```json
{
  "kind": "civicinfo#divisionSearchResponse",
  "results": [
    {
      "ocdId": "ocd-division/country:us",
      "name": "United States"
    },
    {
      "ocdId": "ocd-division/country:us/state:wa",
      "name": "Washington"
    },
    {
      "ocdId": "ocd-division/country:us/state:wa/cd:7",
      "name": "Washington's 7th Congressional District"
    },
    {
      "ocdId": "ocd-division/country:us/state:wa/sldl:43",
      "name": "Washington State House District 43"
    },
    {
      "ocdId": "ocd-division/country:us/state:wa/sldu:43",
      "name": "Washington State Senate District 43"
    },
    {
      "ocdId": "ocd-division/country:us/state:wa/county:king",
      "name": "King County"
    },
    {
      "ocdId": "ocd-division/country:us/state:wa/place:seattle",
      "name": "Seattle city"
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid query parameter or missing address
- `403 Forbidden`: Invalid API key or quota exceeded
- `404 Not Found`: No divisions found for query
- `500 Internal Server Error`: Server error

## OCD-ID Format

**Structure**: `ocd-division/country:{country}/state:{state}/[...hierarchy]`

**Examples**:
- Federal: `ocd-division/country:us`
- State: `ocd-division/country:us/state:wa`
- Congressional District: `ocd-division/country:us/state:wa/cd:7`
- State Senate District: `ocd-division/country:us/state:wa/sldu:43`
- State House District: `ocd-division/country:us/state:wa/sldl:43`
- County: `ocd-division/country:us/state:wa/county:king`
- City/Place: `ocd-division/country:us/state:wa/place:seattle`

**Parsing Rules**:
- Split by `/` to get hierarchy levels
- Extract `state:{code}` to determine state abbreviation
- Identify government level from type suffix:
  - `cd:{num}` = Congressional District (federal)
  - `sldu:{num}` = State Senate District (upper chamber, state)
  - `sldl:{num}` = State House/Assembly District (lower chamber, state)
  - `county:{name}` = County (local)
  - `place:{name}` = City/Municipality (local)

## Rate Limits

**Free Tier**: 25,000 requests per day

**Handling**:
- Cache divisions responses for 7 days (districts rarely change)
- Implement exponential backoff on 403 responses
- Monitor quota usage in Google Cloud Console

## Coverage

- **Geographic**: All U.S. addresses and zip codes
- **Government Levels**: Federal, state, county, city (hierarchical)
- **Data Fields**: OCD-ID, division name, aliases
- **Update Frequency**: Updated after redistricting or boundary changes

## Data Quality

**Strengths**:
- Comprehensive geographic coverage
- Hierarchical jurisdiction data
- Standardized OCD-ID format
- Free tier sufficient for MVP
- Stable data (changes rarely)

**Limitations**:
- Does NOT provide representative information (names, contacts, etc.)
- Zip code queries may be ambiguous (cover multiple districts)
- Requires secondary API calls to get representative details
- Divisions endpoint returns geographic divisions only, not officials

## Integration Notes

**Purpose in MVP**: 
The divisions endpoint serves as the **address/zip code to OCD-ID resolver**. It translates user input into standardized OCD Division IDs, which are then used to query other APIs (OpenStates, WA State Legislature) for representative details.

**Workflow**:
1. User enters address or zip code
2. Call Google divisions endpoint → get list of OCD-IDs
3. Parse OCD-IDs to identify government levels (federal, state, local)
4. For state-level OCD-IDs → query OpenStates API
5. For WA state → query WA State Legislature API (if available)
6. Cache divisions response for 7 days (TTL: 604800 seconds)

**Caching Strategy**:
- Cache key: `"divisions:{normalized_address}"` or `"divisions:{zipcode}"`
- TTL: 7 days (districts change rarely, only after redistricting)
- Invalidation: Manual or automatic after redistricting events

**Edge Cases**:
- Military addresses (APO/FPO): May return limited divisions
- PO Box addresses: May return city/county only, not specific district
- Zip codes spanning multiple districts: Returns all possible divisions
- Rural areas: May have incomplete local divisions

**Error Handling**:
- 404 response: Return error "Unable to determine divisions for address"
- Invalid address: Prompt user to verify address format
- Quota exceeded: Return cached data or error message to retry later
