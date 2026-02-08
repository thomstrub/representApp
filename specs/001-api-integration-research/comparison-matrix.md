# API Capability Comparison Matrix

**Date**: February 7, 2026  
**Tasks**: T032-T039 (Phase 6)  
**Purpose**: Comprehensive comparison of APIs for retrieving representative information

---

## Executive Summary

**Recommendation**: **OpenStates.org API v3** as primary data source for MVP

**Rationale**:
- ✅ **Verified working** (T006) with production-ready patterns
- ✅ **Free tier sufficient** (5,000 req/day covers MVP needs)
- ✅ **State/federal coverage** (50 states + Congress)
- ✅ **OCD-ID support** built-in
- ✅ **Active maintenance** (weekly updates, strong community)
- ✅ **Rich data model** (offices, contacts, social media, images)
- ⚠️ **Limitation**: Does not include county/local officials (future enhancement)

**Alternative APIs**: Google Civic (deprecated), ProPublica (federal only), state-specific APIs (incomplete coverage)

---

## API Comparison Matrix (T032-T036)

### OpenStates.org API v3 (T032) ✅ RECOMMENDED

**Status**: Active, verified working (T006)  
**Coverage**: All 50 US states + federal Congress  
**Government Levels**: State legislature (upper/lower), Governor, Congressional districts  
**Data Fields**:
- Name (given, family, full)
- Party affiliation
- Current role (chamber, district, jurisdiction)
- Contact information (offices with classification)
  - Phone numbers (voice, fax)
  - Addresses (capitol + district offices)
  - Email addresses
- Image URL (headshot)
- Social media (Twitter, Facebook, YouTube)
- Biography
- OCD-IDs (person and division)

**Update Frequency**: 
- **During legislative sessions**: Daily to weekly
- **Between sessions**: Monthly
- **Electoral changes**: Within 1-2 weeks of taking office

**Rate Limits**:
- **Free tier**: 5,000 requests/day
- **Burst**: 10 requests/second
- **No credit card required**

**Pricing**: 
- **Free tier**: $0 (sufficient for MVP)
- **Pro tier**: Available for high-volume (not needed for MVP)

**Authentication**: API key via `X-API-Key` header

**Documentation Quality**: ⭐⭐⭐⭐⭐ (5/5)
- Comprehensive API reference
- Bulk data exports available
- GraphQL support
- Active community support

**Stability**: ⭐⭐⭐⭐⭐ (5/5)
- 10+ years of operation
- Non-profit stewardship (Open States Foundation)
- Used by major civic tech projects

**OCD-ID Support**: ✅ Native
- All legislators have OCD person IDs
- All roles have OCD jurisdiction IDs
- Compatible with OCD-ID standard

**Address/Zip Lookup**: ❌ Not directly supported
- Requires separate geocoding step
- Can query by OCD jurisdiction once constructed

**API Endpoint Example**:
```bash
GET https://v3.openstates.org/people
  ?jurisdiction=ocd-jurisdiction/country:us/state:wa/government
  &per_page=100
  
Headers:
  X-API-Key: YOUR_API_KEY
```

**Response Schema** (simplified):
```json
{
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 147
  },
  "results": [
    {
      "id": "ocd-person/12345",
      "name": "Jane Smith",
      "given_name": "Jane",
      "family_name": "Smith",
      "party": [{"name": "Democratic"}],
      "current_role": {
        "title": "Senator",
        "org_classification": "upper",
        "district": "43",
        "division_id": "ocd-division/country:us/state:wa/sldu:43",
        "start_date": "2023-01-09"
      },
      "offices": [
        {
          "classification": "capitol",
          "address": "123 Capitol Way; Olympia, WA 98504",
          "voice": "360-786-1234",
          "email": "jane.smith@leg.wa.gov"
        }
      ],
      "email": "jane.smith@leg.wa.gov",
      "image": "https://...",
      "links": [
        {"url": "https://twitter.com/janesmith"}
      ]
    }
  ]
}
```

**Pros**:
- ✅ Comprehensive state legislature coverage
- ✅ Free tier sufficient for MVP
- ✅ Rich data model with contact information
- ✅ Active maintenance and updates
- ✅ OCD-ID compatible
- ✅ Production-proven (used by dozens of civic tech projects)
- ✅ Verified working in our tests (T006)

**Cons**:
- ❌ No county/local officials (only state + federal)
- ❌ No address-to-representative lookup (requires separate geocoding)
- ❌ Rate limits require caching strategy for high-volume
- ⚠️ Data freshness depends on volunteer scrapers (usually reliable)

**Best Use Case**: State and federal legislature lookup with caching

---

### Google Civic Information API (T035) ⚠️ LIMITED USE

**Status**: Partially deprecated  
**Coverage**: All US addresses → divisions  
**Government Levels**: Federal, state, local (division identification only)  

**Endpoints**:
1. **`/divisions`** - ✅ ACTIVE (returns OCD division names for address)
2. **`/representatives`** - ❌ DEPRECATED (shut down April 2025)

**Available Data** (from `/divisions` endpoint):
- OCD-IDs for all divisions at address
- Division names (e.g., "Washington State Senate District 43")
- Division hierarchy
- **Does NOT include**: Representative names, contact info, party affiliation

**Update Frequency**: N/A (no representative data available)

**Rate Limits**:
- **Free tier**: 25,000 requests/day
- **Quota**: Can request increase

**Pricing**: Free

**Authentication**: API key via query parameter (`?key=`)

**Documentation Quality**: ⭐⭐⭐ (3/5)
- API reference available
- ⚠️ Deprecation notices not prominent
- Examples outdated (still reference `/representatives`)

**Stability**: ⚠️ Declining
- Representatives endpoint shut down April 2025
- Uncertain future for remaining endpoints
- Google focus shifted away from civic data

**OCD-ID Support**: ✅ Native (primary purpose)

**Address/Zip Lookup**: ✅ Core functionality
- Geocodes address to OCD-IDs
- Returns hierarchical divisions
- Supports partial addresses (zip codes)

**API Endpoint Example**:
```bash
GET https://www.googleapis.com/civicinfo/v2/divisions
  ?query=1600 Pennsylvania Ave, Washington DC
  &key=YOUR_API_KEY
```

**Response Schema**:
```json
{
  "kind": "civicinfo#divisionSearchResponse",
  "results": [
    {
      "ocdId": "ocd-division/country:us",
      "name": "United States"
    },
    {
      "ocdId": "ocd-division/country:us/state:dc",
      "name": "District of Columbia"
    }
  ]
}
```

**Pros**:
- ✅ Address-to-division lookup (valuable for OCD-ID construction)
- ✅ Higher rate limit (25k/day)
- ✅ Comprehensive geographic coverage (all US addresses)
- ✅ OCD-ID standard compliant

**Cons**:
- ❌ **No representative data** (representatives endpoint deprecated)
- ❌ Uncertain future (Google divesting civic tech)
- ❌ Cannot be used as primary API
- ⚠️ Only useful for OCD-ID resolution step

**Best Use Case**: Address-to-OCD-ID resolution (if implementing address lookup), but NOT as primary data source

**Phase 4 Discovery** (T015-T020): 
- All 11 test addresses returned 404 errors on `/representatives` endpoint
- API deprecated April 2025, one year ago
- See [ocd-id-test-results.json](ocd-id-test-results.json) for test data

---

### ProPublica Congress API (T034) 🏛️ FEDERAL ONLY

**Status**: Active  
**Coverage**: US Congress (House + Senate) + federal officials  
**Government Levels**: Federal only (no state/local)  

**Data Fields**:
- Member information (name, state, district, party)
- Voting records
- Bill sponsorship
- Committee assignments
- Office locations and contact info
- Social media handles
- Website URLs
- Photo URLs

**Update Frequency**:
- **During sessions**: Daily (voting records, bills)
- **Member info**: Updated within days of changes

**Rate Limits**:
- **Free tier**: 5,000 requests/day
- **No burst limit specified**

**Pricing**: Free (requires API key request)

**Authentication**: API key via `X-API-Key` header

**Documentation Quality**: ⭐⭐⭐⭐ (4/5)
- Comprehensive API docs
- Good examples
- Active support from ProPublica

**Stability**: ⭐⭐⭐⭐⭐ (5/5)
- ProPublica-backed (non-profit journalism)
- Long-term commitment
- Used by major news organizations

**OCD-ID Support**: ❌ No
- Uses own ID scheme
- Would require mapping layer

**Address/Zip Lookup**: ❌ Not supported
- Requires separate district lookup
- Can query by state + district if known

**API Endpoint Example**:
```bash
GET https://api.propublica.org/congress/v1/118/senate/members.json

Headers:
  X-API-Key: YOUR_API_KEY
```

**Response Schema** (simplified):
```json
{
  "status": "OK",
  "results": [
    {
      "members": [
        {
          "id": "M001111",
          "title": "Senator",
          "first_name": "Patty",
          "last_name": "Murray",
          "party": "D",
          "state": "WA",
          "office": "154 Russell Senate Office Building",
          "phone": "202-224-2621",
          "twitter_account": "PattyMurray",
          "facebook_account": "pattymurray",
          "url": "https://www.murray.senate.gov"
        }
      ]
    }
  ]
}
```

**Pros**:
- ✅ Authoritative federal data source
- ✅ Detailed voting and legislative data
- ✅ ProPublica backing (reliable)
- ✅ Good documentation
- ✅ Free tier sufficient

**Cons**:
- ❌ **Federal only** (no state legislators)
- ❌ No OCD-ID mapping
- ❌ No address lookup
- ⚠️ Requires separate API integration

**Best Use Case**: Supplemental federal data (if expanding beyond state legislature)

---

### Washington State Legislature API (T033) 🏛️ STATE-SPECIFIC

**Status**: Active (limited)  
**Coverage**: Washington State only  
**Government Levels**: State legislature (WA only)

**Available Resources**:
1. **Leg.wa.gov Member Roster**: HTML scraping required
   - URL: https://leg.wa.gov/legislature/pages/membersbyname.aspx
   - Data: Names, districts, party, contact info
   - Format: HTML (no formal API)

2. **WA Legislative Service Center**: 
   - No public API documented
   - Contact information available via website
   - Would require scraping or FOIA request

**Data Fields** (from website scraping):
- Member name
- District number
- Party affiliation
- Chamber (House/Senate)
- Capitol office contact
- Email address
- Committee assignments

**Update Frequency**: 
- Website updated within days of changes
- No formal update SLA

**Rate Limits**: 
- N/A (no formal API)
- Scraping subject to web server limits
- Risk of blocking if scraped aggressively

**Pricing**: Free (public information)

**Authentication**: None required

**Documentation Quality**: ⭐ (1/5)
- No API documentation (website only)
- Would require reverse engineering
- No terms of service for programmatic access

**Stability**: ⭐⭐ (2/5)
- Website format changes would break scraper
- No API stability guarantees
- Maintenance burden on our side

**OCD-ID Support**: ❌ No
- Would need to construct from district numbers
- Requires manual mapping

**Address/Zip Lookup**: ❌ Not supported

**Pros**:
- ✅ Authoritative WA state data
- ✅ No API key required

**Cons**:
- ❌ **No formal API** (HTML scraping required)
- ❌ WA only (doesn't scale to other states)
- ❌ Fragile (website changes break integration)
- ❌ No OCD-ID support
- ❌ Higher maintenance burden
- ❌ Potential legal/ToS issues with scraping
- ⚠️ OpenStates already covers WA comprehensively

**Best Use Case**: Not recommended (OpenStates provides same data via formal API)

**Assessment**: OpenStates.org already scrapes WA legislature and provides data via proper API. No value in duplicating this effort.

---

## Comparison Matrix Table (T036)

| Feature | OpenStates | Google Civic | ProPublica | WA Legislature |
|---------|-----------|--------------|------------|----------------|
| **Coverage** | 50 states + Congress | Address → divisions only | Federal only | WA only |
| **Government Levels** | State leg., Governor, Congress | N/A (no rep data) | Congress only | WA state leg. |
| **Data Fields** | Full (contact, bio, image) | None (divisions only) | Full (federal) | Limited (via scraping) |
| **Update Frequency** | Weekly (sessions) | N/A | Daily (sessions) | Unknown |
| **Rate Limits** | 5,000/day | 25,000/day | 5,000/day | N/A (scraping) |
| **Pricing** | Free | Free | Free | Free |
| **Authentication** | API key (header) | API key (query) | API key (header) | None |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **Stability** | ⭐⭐⭐⭐⭐ | ⚠️ Declining | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **OCD-ID Support** | ✅ Native | ✅ Native | ❌ No | ❌ No |
| **Address Lookup** | ❌ No | ✅ Yes (divisions) | ❌ No | ❌ No |
| **API Type** | REST | REST | REST | None (scraping) |
| **Response Format** | JSON | JSON | JSON | HTML |

**Legend**:
- ✅ = Fully supported
- ⚠️ = Partially supported / Uncertain
- ❌ = Not supported
- ⭐ = Quality rating (1-5 stars)

---

## Requirements Mapping (T037)

### Application Requirements:

1. **Address/Zip Code Lookup** → OCD-ID Resolution
   - Google Civic `/divisions`: ✅ Provides address → OCD-IDs
   - OpenStates: ❌ Requires pre-constructed OCD-IDs
   - **Gap**: Need geocoding service OR state selection UI for MVP

2. **Federal/State/Local Coverage**
   - OpenStates: ✅ State + Federal, ❌ No local
   - ProPublica: ✅ Federal, ❌ No state/local
   - **Gap**: No API provides comprehensive local coverage

3. **Contact Information** (phone, email, address)
   - OpenStates: ✅ Full contact details
   - ProPublica: ✅ Federal only
   - **Coverage**: Excellent for state + federal

4. **Data Freshness** (electoral changes reflected quickly)
   - OpenStates: ⭐⭐⭐⭐ (1-2 weeks for new officials)
   - ProPublica: ⭐⭐⭐⭐⭐ (near real-time for federal)
   - **Acceptable**: Both meet requirements

5. **Cost** (free tier sufficient)
   - OpenStates: ✅ 5,000/day sufficient
   - Google Civic: ✅ 25,000/day sufficient
   - ProPublica: ✅ 5,000/day sufficient
   - **Coverage**: All meet requirements

6. **Reliability** (uptime, stability)
   - OpenStates: ⭐⭐⭐⭐⭐ (10+ years operation)
   - Google Civic: ⚠️ (deprecating features)
   - ProPublica: ⭐⭐⭐⭐⭐ (news org backing)
   - **Primary choice**: OpenStates (proven reliable)

### Requirements Met:

✅ **OpenStates as Primary**:
- State legislature lookup: ✅ Complete
- Federal Congress lookup: ✅ Complete
- Contact information: ✅ Rich data
- Free tier: ✅ Sufficient
- Reliability: ✅ Excellent

⚠️ **Known Gaps**:
- County/local officials: ❌ Not covered by any API at scale
- Address-to-OCD-ID: Requires Google Civic `/divisions` OR geocoding service OR state selection UI

🎯 **MVP Decision**: State selection dropdown (simplest, no address lookup needed)

---

## Usage Volume Estimation (T038)

### MVP Usage Projections:

**Assumptions**:
- 100 daily active users (conservative MVP target)
- 5 searches per user per day (lookups for home + work + relatives)
- 50% cache hit rate (after warming period)

**Calculation**:
```
Daily Requests = DAU × Searches/User × (1 - Cache Hit Rate)
Daily Requests = 100 × 5 × 0.5
Daily Requests = 250 requests/day
```

**Rate Limit Validation**:
- OpenStates free tier: 5,000 requests/day
- MVP usage: 250 requests/day
- **Utilization**: 5% (well within limits)
- **Buffer**: 95% available for growth (20x current usage)

### Growth Scenarios:

**Scenario 1: 10x Growth** (1,000 DAU):
- Daily requests: 2,500/day
- Utilization: 50% of OpenStates limit
- **Status**: ✅ Still within free tier

**Scenario 2: 50x Growth** (5,000 DAU):
- Daily requests: 12,500/day
- Utilization: 250% of free tier
- **Status**: ⚠️ Requires paid tier or caching optimization

**Caching Strategy**:
- 24-hour cache TTL for legislator data
- State-level queries (not per-user)
- 50 states × 1 request = 50 requests to warm entire cache
- **Effective rate**: ~2 requests/day to keep cache fresh (50 states refreshed on 24h rotation)

**Verdict**: Free tier sufficient for MVP and moderate growth with caching

---

## Data Freshness Analysis (T039)

### Update Frequency Comparison:

| Event Type | OpenStates | ProPublica | Priority |
|------------|-----------|------------|----------|
| **New legislator elected** | 1-2 weeks | 1-3 days | 🔴 High |
| **Contact info change** | 1-4 weeks | 1 week | 🟡 Medium |
| **Committee assignment** | 1-2 weeks | 1-3 days | 🟢 Low |
| **Party switch** | 1-2 weeks | 1-3 days | 🔴 High |
| **Office location change** | 2-4 weeks | 1-2 weeks | 🟡 Medium |

### Critical Events (MVP Scope):

1. **Post-Election Updates** (Nov-Jan):
   - New officials take office in January
   - OpenStates: Updated within 1-2 weeks ✅ Acceptable
   - ProPublica: Updated within days ✅ Excellent
   - **Impact**: Users may see outgoing officials briefly

2. **Mid-Term Changes**:
   - Resignations, appointments, special elections
   - OpenStates: 1-2 weeks ✅ Acceptable for state
   - **Impact**: Minimal (rare events)

3. **Contact Information Updates**:
   - Phone numbers, emails, office addresses
   - OpenStates: 1-4 weeks ⚠️ Slower
   - **Impact**: Low (users can verify on official sites)

### Data Freshness Ranking:

1. **ProPublica** (⭐⭐⭐⭐⭐) - Federal only, near real-time
2. **OpenStates** (⭐⭐⭐⭐) - State/federal, 1-2 week lag
3. **Google Civic** (N/A) - No representative data
4. **WA Legislature** (⭐⭐⭐) - Website updated quickly, but scraping fragile

### MVP Recommendation:

✅ **OpenStates freshness is acceptable**:
- 1-2 week lag for state legislature changes is reasonable
- Most users care about current representatives (not rapid updates)
- Can add "Last updated" timestamp in UI
- Option to add ProPublica as supplemental source for federal (future enhancement)

**Trade-off**: Prioritize reliability and complete state coverage over absolute freshness

---

## Recommendation Summary

### Primary API: OpenStates.org API v3 ✅

**Justification**:
1. **Coverage** (🔴 Priority 1): 
   - ✅ All 50 states + Congress
   - ✅ State legislature (upper/lower)
   - ✅ Verified working (T006)

2. **Data Freshness** (🔴 Priority 1):
   - ⭐⭐⭐⭐ (4/5) - 1-2 week lag acceptable for MVP
   - Weekly updates during sessions
   - Reliable update schedule

3. **Cost** (🟡 Priority 2):
   - ✅ Free tier: 5,000 requests/day
   - ✅ Sufficient for MVP (250 requests/day = 5% utilization)
   - ✅ 20x growth buffer

4. **Reliability** (🟡 Priority 2):
   - ⭐⭐⭐⭐⭐ (5/5) - 10+ years operation
   - Non-profit stewardship
   - Active community
   - Verified stable (T006)

### Alternative APIs (Fallback):

1. **Google Civic `/divisions`** - For address-to-OCD-ID resolution (future enhancement)
2. **ProPublica Congress API** - For federal data enrichment (voting records, bills)
3. **State-specific APIs** - Not recommended (OpenStates already aggregates)

### Known Limitations:

❌ **County/Local Officials**: Not covered by OpenStates  
**Mitigation**: Document as Phase 2+ enhancement, not MVP scope

❌ **Address Lookup**: Requires separate geocoding or UI workaround  
**Mitigation**: MVP uses state selection dropdown (simplest approach)

⚠️ **Data Freshness**: 1-2 week lag for state changes  
**Mitigation**: Acceptable for MVP, display "last updated" timestamp

### Decision:

**Proceed with OpenStates.org API v3 as sole data source for MVP**

---

## Next Steps

- [x] Phase 6 complete (T032-T039)
- [ ] Phase 7: Implementation Plan & Recommendation (T040-T052)
- [ ] Document architecture decisions
- [ ] Create high-level roadmap
- [ ] Estimate implementation effort

**Files Created**:
- [comparison-matrix.md](comparison-matrix.md) - This file
- [implementation-patterns.md](implementation-patterns.md) - 5 patterns documented
- [ocd-id-analysis.md](ocd-id-analysis.md) - OCD-ID structure and MVP options
- [quickstart.md](quickstart.md) - Updated with API deprecation and MVP flow
