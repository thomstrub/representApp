# Phase 1: Data Model

**Feature**: 003-address-lookup  
**Date**: February 8, 2026  
**Status**: Design Complete

## Overview

This document defines the data entities used in the address-based representative lookup feature. These models represent the domain concepts extracted from the feature specification and align with external API response structures (Google Civic, OpenStates).

## Core Entities

### 1. Representative

**Description**: An elected official holding public office at federal, state, or local level.

**Attributes**:

| Field | Type | Required | Validation | Source | Notes |
|-------|------|----------|------------|--------|-------|
| `id` | string | Yes | Non-empty, unique | OpenStates `id` field | Primary key for deduplication |
| `name` | string | Yes | Non-empty, max 200 chars | OpenStates `name` field | Full legal name |
| `office` | string | Yes | Non-empty, max 100 chars | OpenStates `current_role.title` | e.g., "US Senator", "State Senator - District 12" |
| `party` | string | No | Enum: Democratic, Republican, Independent, etc. | OpenStates `current_role.party` | May be null for non-partisan offices |
| `email` | string | No | Valid email format or semicolon-separated emails | OpenStates `email` field | Semicolon-separated if multiple |
| `phone` | string | No | Format: XXX-XXX-XXXX | OpenStates `capitol_office.voice` | Normalized to consistent format |
| `address` | string | No | Max 500 chars | OpenStates `capitol_office.address` | Office mailing address |
| `website` | string | No | Valid URL format | OpenStates `links[type=url]` | Official website |
| `photo_url` | string | No | Valid URL format (not validated for accessibility) | OpenStates `image` field | May be null or broken link |
| `government_level` | string | Yes | Enum: federal, state, local | Derived from OCD-ID | See Government Level Categorization below |
| `jurisdiction` | string | Yes | Valid OCD-ID format | OpenStates `jurisdiction.name` or OCD-ID | Which district/state they represent |

**Validation Rules**:
- `id` MUST be unique within response (used for deduplication)
- `name` MUST be present and non-empty
- `office` MUST be present and describe the position held
- `government_level` MUST be one of: federal, state, local
- `phone` format validated as XXX-XXX-XXXX if present; rejected otherwise
- `email` validated as valid email format(s) if present; rejected otherwise
- `photo_url` passed through without validation (frontend handles broken links)

**Relationships**:
- Each Representative belongs to exactly one Office
- Each Representative serves in exactly one Division (jurisdiction)

**Example**:
```json
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
}
```

---

### 2. Division

**Description**: A political or administrative boundary defined by an OCD (Open Civic Data) identifier from Google Civic API.

**Attributes**:

| Field | Type | Required | Validation | Source | Notes |
|-------|------|----------|------------|--------|-------|
| `ocd_id` | string | Yes | Valid OCD-ID format: `ocd-division/country:us/...` | Google Civic `/divisions` response | Primary identifier |
| `name` | string | Yes | Non-empty, max 200 chars | Google Civic `name` field | Human-readable name |
| `government_level` | string | Yes | Enum: federal, state, county, city, congressional, state_legislative | Parsed from OCD-ID structure | See parsing rules below |
| `has_data` | boolean | Yes | true/false | Determined after OpenStates query | Indicates if OpenStates returned representatives |

**Validation Rules**:
- `ocd_id` MUST start with `ocd-division/country:us/`
- `ocd_id` MUST be well-formed hierarchical identifier (no spaces, lowercase)
- `government_level` MUST be derived using OCD-ID parsing rules

**Relationships**:
- Each Division may have zero or more Representatives
- Divisions are hierarchical (e.g., state contains counties, which contain cities)

**Example**:
```json
{
  "ocd_id": "ocd-division/country:us/state:ca/cd:12",
  "name": "California's 12th Congressional District",
  "government_level": "congressional",
  "has_data": true
}
```

---

### 3. Office

**Description**: A position of elected authority within government (e.g., "US Senator", "Governor", "State Representative - District 5").

**Attributes**:

| Field | Type | Required | Validation | Source | Notes |
|-------|------|----------|------------|--------|-------|
| `title` | string | Yes | Non-empty, max 100 chars | OpenStates `current_role.title` | Official position title |
| `government_level` | string | Yes | Enum: federal, state, local | Derived from division or role type | Category for UI grouping |
| `division` | string | Yes | Valid OCD-ID | Associated Division OCD-ID | Which jurisdiction this office represents |

**Validation Rules**:
- `title` MUST be non-empty and descriptive
- `government_level` MUST match the division's government level

**Relationships**:
- Each Office exists within exactly one Division
- Each Office may be held by exactly one Representative at a time

**Example**:
```json
{
  "title": "State Senator - District 12",
  "government_level": "state",
  "division": "ocd-division/country:us/state:ca/sldl:12"
}
```

---

### 4. AddressLookupRequest

**Description**: Input payload for address-based representative lookup.

**Attributes**:

| Field | Type | Required | Validation | Source | Notes |
|-------|------|----------|------------|--------|-------|
| `address` | string | Yes | Non-empty, max 500 chars | Query parameter `?address={address}` | Full US street address |

**Validation Rules**:
- `address` MUST be present (return 400 if missing)
- `address` MUST be non-empty after trimming whitespace (return 400 if empty)
- `address` MUST NOT exceed 500 characters (return 400 if too long)
- Special characters sanitized before passing to Google Civic API

**Example**:
```
GET /representatives?address=1600 Pennsylvania Ave NW, Washington, DC 20500
```

---

### 5. AddressLookupResponse

**Description**: Successful response containing representatives for a given address.

**Attributes**:

| Field | Type | Required | Validation | Source | Notes |
|-------|------|----------|------------|--------|-------|
| `representatives` | array of Representative | Yes | May be empty array | Aggregated from OpenStates | Deduplicated by `id` |
| `metadata` | object | Yes | Non-null | Constructed by handler | Request context and performance data |
| `warnings` | array of string | No | May be absent or empty | Constructed by handler | Coverage gaps or missing divisions |

**Metadata Object**:

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `address` | string | Yes | Echoes input address | For user confirmation |
| `government_levels` | array of string | Yes | Subset of: federal, state, local | Which levels are included in response |
| `response_time_ms` | integer | No | Positive integer | End-to-end processing time (optional) |

**Validation Rules**:
- `representatives` array MUST be present (even if empty)
- `metadata` MUST include `address` echoing user input
- `warnings` array included only when divisions have missing data

**Example**:
```json
{
  "representatives": [
    {
      "id": "ocd-person/12345",
      "name": "John Doe",
      "office": "US Senator",
      "party": "Republican",
      "email": "senator.doe@senate.gov",
      "phone": "202-555-0200",
      "address": "456 Senate Office Building, Washington, DC 20510",
      "website": "https://doe.senate.gov",
      "photo_url": "https://openstates.org/static/images/doe.jpg",
      "government_level": "federal",
      "jurisdiction": "United States"
    }
  ],
  "metadata": {
    "address": "1600 Pennsylvania Ave NW, Washington, DC 20500",
    "government_levels": ["federal", "state"]
  },
  "warnings": [
    "No data available for: ocd-division/country:us/state:dc/county:district_of_columbia"
  ]
}
```

---

### 6. ErrorResponse

**Description**: Error response for failed requests.

**Attributes**:

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `error` | object | Yes | Non-null | Single error object (not array) |

**Error Object**:

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `code` | string | Yes | Uppercase snake_case (e.g., INVALID_ADDRESS) | Machine-readable error code |
| `message` | string | Yes | Non-empty, user-friendly | Human-readable error description |
| `details` | string | No | Optional context | Additional debugging information |

**Error Codes**:
- `MISSING_PARAMETER`: Required parameter missing
- `INVALID_ADDRESS`: Address validation failed
- `ADDRESS_NOT_FOUND`: Google Civic couldn't resolve address
- `EXTERNAL_SERVICE_ERROR`: Google Civic or OpenStates API unavailable
- `RATE_LIMIT_EXCEEDED`: API rate limits reached
- `INTERNAL_ERROR`: Uncaught exception or unexpected failure

**HTTP Status Code Mapping**:
- 400 → `MISSING_PARAMETER`, `INVALID_ADDRESS`
- 404 → `ADDRESS_NOT_FOUND`
- 503 → `EXTERNAL_SERVICE_ERROR`, `RATE_LIMIT_EXCEEDED`
- 500 → `INTERNAL_ERROR`

**Example**:
```json
{
  "error": {
    "code": "ADDRESS_NOT_FOUND",
    "message": "Unable to find political divisions for the provided address",
    "details": "Google Civic API returned zero divisions for address: '123 Fake Street'"
  }
}
```

---

## Government Level Categorization

**Purpose**: Map OCD-IDs to human-readable government level categories for UI grouping and filtering.

**Parsing Rules**:

| OCD-ID Pattern | Example | Government Level | Notes |
|----------------|---------|------------------|-------|
| `/country:us$` | `ocd-division/country:us` | `federal` | US Senators, President |
| `/state:[a-z]{2}$` | `ocd-division/country:us/state:ca` | `state` | Governors, state-level officials |
| `/cd:\d+` | `ocd-division/country:us/state:ca/cd:12` | `federal` | US House Congressional districts |
| `/sldl:\d+` | `ocd-division/country:us/state:ca/sldl:15` | `state` | State house/assembly districts |
| `/sldu:\d+` | `ocd-division/country:us/state:ca/sldu:8` | `state` | State senate districts |
| `/county:[a-z_]+` | `ocd-division/country:us/state:ca/county:alameda` | `local` | County-level officials (limited OpenStates data) |
| `/place:[a-z_]+` | `ocd-division/country:us/state:ca/place:san_francisco` | `local` | City-level officials (limited OpenStates data) |

**Implementation Note**: Use regex patterns to match OCD-ID suffixes and map to categories. Default to `local` for unmatched patterns.

---

## Data Transformation Flow

### Google Civic API → Internal Models

**Input**: Google Civic `/divisions` response
```json
{
  "divisions": {
    "ocd-division/country:us": {
      "name": "United States"
    },
    "ocd-division/country:us/state:ca": {
      "name": "California"
    },
    "ocd-division/country:us/state:ca/cd:12": {
      "name": "California's 12th Congressional District"
    }
  }
}
```

**Transformation**:
```python
divisions = []
for ocd_id, division_data in response['divisions'].items():
    divisions.append({
        "ocd_id": ocd_id,
        "name": division_data['name'],
        "government_level": parse_government_level(ocd_id),
        "has_data": False  # Updated after OpenStates query
    })
```

### OpenStates API → Internal Models

**Input**: OpenStates `/people` response
```json
{
  "results": [
    {
      "id": "ocd-person/12345",
      "name": "Jane Smith",
      "current_role": {
        "title": "Senator",
        "party": "Democratic",
        "district": "12"
      },
      "email": "jane.smith@example.gov",
      "capitol_office": {
        "voice": "202-555-0100",
        "address": "123 Capitol Building"
      },
      "image": "https://example.com/smith.jpg",
      "jurisdiction": {
        "name": "California"
      }
    }
  ]
}
```

**Transformation**:
```python
representative = {
    "id": person['id'],
    "name": person['name'],
    "office": person['current_role']['title'],
    "party": person['current_role'].get('party'),
    "email": person.get('email'),
    "phone": normalize_phone(person.get('capitol_office', {}).get('voice')),
    "address": person.get('capitol_office', {}).get('address'),
    "website": extract_website(person.get('links', [])),
    "photo_url": person.get('image'),
    "government_level": derive_from_jurisdiction(person['jurisdiction']),
    "jurisdiction": person['jurisdiction']['name']
}
```

---

## Validation Summary

| Entity | Primary Key | Uniqueness Constraint | Required Fields |
|--------|-------------|----------------------|-----------------|
| Representative | `id` | OpenStates person ID | id, name, office, government_level, jurisdiction |
| Division | `ocd_id` | OCD-ID string | ocd_id, name, government_level |
| Office | `title` + `division` | Composite | title, government_level, division |
| AddressLookupRequest | N/A | N/A | address |
| AddressLookupResponse | N/A | N/A | representatives, metadata |
| ErrorResponse | N/A | N/A | error.code, error.message |

---

## Next Phase

Proceed to **API Contracts** (OpenAPI schema) and **Quickstart Guide** to complete Phase 1 design.
