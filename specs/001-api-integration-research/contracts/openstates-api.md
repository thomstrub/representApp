# API Contract: OpenStates.org API

**Provider**: OpenStates.org  
**Version**: v3  
**Documentation**: https://docs.openstates.org/api-v3/  
**Base URL**: `https://v3.openstates.org`

## Authentication

**Method**: API Key (Header)

```http
X-API-Key: YOUR_API_KEY_HERE
```

**Registration**: Free tier available at https://openstates.org/accounts/signup/

## Endpoints

### 1. Get People (Representatives) by Jurisdiction

**Purpose**: Retrieve all representatives for a given jurisdiction (state, district, etc.)

```http
GET /people?jurisdiction={jurisdiction_id}&per_page={limit}
```

**Query Parameters**:
- `jurisdiction` (required): State abbreviation or jurisdiction ID (e.g., "wa", "ocd-division/country:us/state:wa")
- `per_page` (optional): Number of results (default: 100, max: 100)
- `page` (optional): Page number for pagination

**Request Example**:
```http
GET https://v3.openstates.org/people?jurisdiction=wa&per_page=100
X-API-Key: YOUR_API_KEY_HERE
```

**Response Example** (200 OK):
```json
{
  "results": [
    {
      "id": "ocd-person/12345",
      "name": "Jane Doe",
      "given_name": "Jane",
      "family_name": "Doe",
      "party": [
        {
          "name": "Democratic"
        }
      ],
      "current_role": {
        "title": "Senator",
        "district": "42",
        "division_id": "ocd-division/country:us/state:wa/sldu:42",
        "org_classification": "upper"
      },
      "email": "jane.doe@leg.wa.gov",
      "capitol_office": {
        "voice": "360-786-7600",
        "address": "123 Legislative Building, Olympia, WA 98504"
      },
      "links": [
        {
          "url": "https://www.leg.wa.gov/Senate/Senators/Pages/default.aspx"
        }
      ],
      "image": "https://example.com/photos/jane-doe.jpg",
      "extras": {
        "twitter": "@SenatorJaneDoe"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 147
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid jurisdiction parameter
- `401 Unauthorized`: Missing or invalid API key
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### 2. Get Person by ID

**Purpose**: Retrieve detailed information for a specific representative

```http
GET /people/{person_id}
```

**Path Parameters**:
- `person_id` (required): OCD Person ID (e.g., "ocd-person/12345")

**Request Example**:
```http
GET https://v3.openstates.org/people/ocd-person/12345
X-API-Key: YOUR_API_KEY_HERE
```

**Response Example** (200 OK):
```json
{
  "id": "ocd-person/12345",
  "name": "Jane Doe",
  "given_name": "Jane",
  "family_name": "Doe",
  "party": [
    {
      "name": "Democratic",
      "start_date": "2019-01-01",
      "end_date": null
    }
  ],
  "current_role": {
    "title": "Senator",
    "district": "42",
    "division_id": "ocd-division/country:us/state:wa/sldu:42",
    "org_classification": "upper",
    "start_date": "2019-01-14",
    "end_date": null
  },
  "email": "jane.doe@leg.wa.gov",
  "capitol_office": {
    "voice": "360-786-7600",
    "fax": "360-786-1999",
    "address": "123 Legislative Building, Olympia, WA 98504"
  },
  "district_office": {
    "voice": "206-555-1234",
    "address": "456 Main St, Seattle, WA 98101"
  },
  "links": [
    {
      "url": "https://www.leg.wa.gov/Senate/Senators/Pages/default.aspx",
      "note": "Official Website"
    }
  ],
  "sources": [
    {
      "url": "https://www.leg.wa.gov/...",
      "note": "Washington State Legislature"
    }
  ],
  "image": "https://example.com/photos/jane-doe.jpg",
  "extras": {
    "twitter": "@SenatorJaneDoe",
    "facebook": "facebook.com/janedoe"
  }
}
```

**Error Responses**:
- `404 Not Found`: Person ID does not exist
- `401 Unauthorized`: Missing or invalid API key
- `500 Internal Server Error`: Server error

## Rate Limits

**Free Tier**: 5,000 requests per day, 10 requests per second

**Handling**:
- Monitor `X-RateLimit-Remaining` response header
- Implement exponential backoff on 429 responses
- Cache responses for 24 hours to reduce API calls

## Coverage

- **Geographic**: All 50 U.S. states + D.C., Puerto Rico, U.S. territories
- **Government Levels**: State legislators only (no federal or local)
- **Data Fields**: Name, party, district, contact info, photo, social media
- **Update Frequency**: Updated weekly during legislative sessions, monthly otherwise

## Data Quality

**Strengths**:
- Comprehensive state legislative coverage
- Structured OCD-ID format for divisions
- Regular updates during sessions
- Free tier suitable for MVP

**Limitations**:
- No federal representatives (Congress, President)
- No local representatives (mayors, city council, county)
- Contact info completeness varies by state
- Social media fields often missing

## Integration Notes

- Use `division_id` field to match with Google Civic divisions endpoint
- Parse `current_role.org_classification` to determine chamber (upper/lower/executive)
- Normalize party names: "Democratic" → "D", "Republican" → "R"
- Handle pagination for states with many legislators
- Implement caching with 24-hour TTL for representative data
- Monitor rate limits in production
