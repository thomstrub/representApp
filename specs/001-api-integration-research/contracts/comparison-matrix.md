# API Comparison Matrix

**Feature**: API Integration Research  
**Phase**: 1 - Design & Contracts  
**Date**: 2026-02-07

## Purpose

This matrix compares government APIs for representative information retrieval to guide primary API selection for MVP implementation.

## Comparison Criteria

**Priority Order**:
1. **Coverage** (Primary): Federal, state, and local representative data completeness
2. **Data Freshness** (Primary): Update frequency for elections and roster changes
3. **Rate Limits** (Secondary): Requests per day/second with free tier
4. **Pricing** (Secondary): Free tier availability and paid plan costs
5. **Authentication** (Secondary): Ease of setup and security

## API Provider Comparison

| Criteria | OpenStates.org API | Washington State Legislature API | Google Civic Information API | ProPublica Congress API |
|----------|-------------------|----------------------------------|----------------------------|-------------------------|
| **Coverage** | ⭐⭐⭐ State legislators only (all 50 states + territories) | ⭐⭐ Washington state only (state legislators) | ⭐⭐⭐⭐ Federal + state + local divisions (no rep details) | ⭐⭐⭐ Federal only (Congress, President) |
| **Government Levels** | State | State | Federal, State, Local (divisions only) | Federal |
| **Data Fields** | Name, party, district, contact, photo, social media, OCD-ID | Name, party, district, contact, photo, committee assignments | OCD-IDs and division names only | Name, party, district, contact, voting record, bills |
| **Update Frequency** | ⭐⭐⭐ Weekly (sessions), Monthly (off-season) | ⭐⭐⭐⭐ Real-time (state legislature site scraping) | ⭐⭐⭐⭐ Updated after redistricting (rarely) | ⭐⭐⭐⭐ Daily (voting records), Weekly (roster) |
| **Rate Limits** | 5,000 req/day, 10 req/sec (free) | Unknown (public site, no formal API) | 25,000 req/day (free) | 5,000 req/day (free) |
| **Pricing** | ✅ Free tier, $50/mo for higher limits | ✅ Free (public site) | ✅ Free tier (sufficient for MVP) | ✅ Free tier (sufficient for MVP) |
| **Authentication** | API Key (header) | None (public site) | API Key (query param) | API Key (header) |
| **Documentation** | ⭐⭐⭐⭐ Excellent (OpenAPI, examples) | ⭐ Minimal (no formal API docs) | ⭐⭐⭐⭐ Excellent (Google Docs, examples) | ⭐⭐⭐⭐ Excellent (interactive docs) |
| **Stability** | ⭐⭐⭐⭐ Production-ready, stable v3 API | ⭐⭐ Scraping required, fragile | ⭐⭐⭐⭐ Stable (Representatives endpoint deprecated) | ⭐⭐⭐⭐ Stable, maintained by ProPublica |
| **OCD-ID Support** | ✅ Native support (division_id field) | ❌ No OCD-ID support | ✅ Primary source for OCD-IDs | ✅ Uses OCD-IDs internally |
| **Address/Zip Lookup** | ❌ No (requires pre-resolved OCD-ID) | ❌ No (requires district number) | ✅ Yes (divisions endpoint) | ❌ No (requires district/state) |

## Decision Matrix

### Coverage Analysis

**Federal Representatives**:
- ❌ OpenStates: Not covered
- ❌ WA State: Not covered
- ❌ Google Civic: Divisions only, no rep details
- ✅ ProPublica: Full coverage (Congress, President)

**State Representatives**:
- ✅ OpenStates: All states covered
- ✅ WA State: Washington only
- ❌ Google Civic: Divisions only, no rep details
- ❌ ProPublica: Not covered

**Local Representatives**:
- ❌ OpenStates: Not covered
- ❌ WA State: Not covered
- ❌ Google Civic: Divisions only, no rep details
- ❌ ProPublica: Not covered

**Conclusion**: No single API provides complete federal + state + local coverage. Multi-API integration required.

### Data Freshness Analysis

| Provider | Update Frequency | Data Age Risk | Election Updates |
|----------|-----------------|---------------|------------------|
| OpenStates | Weekly (sessions), Monthly (off-season) | Medium | Good (post-election updates) |
| WA State | Real-time (scraping) | Low | Excellent (immediate) |
| Google Civic | Rare (post-redistricting) | Low (divisions stable) | N/A (divisions only) |
| ProPublica | Daily (votes), Weekly (roster) | Low | Excellent (immediate) |

**Conclusion**: OpenStates provides acceptable freshness for state legislators. Google Civic divisions are stable. ProPublica best for federal data.

### Integration Complexity

| Provider | Integration Effort | Dependencies | Caching Strategy |
|----------|-------------------|--------------|------------------|
| OpenStates | Low (REST API, clear docs) | None | 24-hour TTL for reps |
| WA State | High (scraping, no formal API) | BeautifulSoup, fragile selectors | 6-hour TTL (may break) |
| Google Civic | Low (REST API, clear docs) | Required for OCD-ID resolution | 7-day TTL for divisions |
| ProPublica | Low (REST API, clear docs) | None | 24-hour TTL for reps |

**Conclusion**: OpenStates, Google Civic, and ProPublica are low-effort integrations. Avoid WA State scraping for MVP.

## Recommended Architecture

### Primary APIs (MVP)

1. **Google Civic Information API (Divisions Endpoint)**: 
   - **Purpose**: Address/zip code → OCD-ID resolution
   - **Coverage**: All U.S. addresses, federal + state + local divisions
   - **Caching**: 7-day TTL (divisions rarely change)
   - **Justification**: Only API supporting address/zip lookup with OCD-ID output

2. **OpenStates.org API**:
   - **Purpose**: State representative details (name, contact, party, district)
   - **Coverage**: All 50 states + territories
   - **Caching**: 24-hour TTL for representative data
   - **Justification**: Best coverage for state legislators, stable API, OCD-ID support

3. **ProPublica Congress API** (Post-MVP):
   - **Purpose**: Federal representative details (Congress, President)
   - **Coverage**: Federal level only
   - **Caching**: 24-hour TTL for representative data
   - **Justification**: Best coverage for federal legislators, voting record data

### Fallback/Future APIs

- **Washington State Legislature API**: Enhance WA state data with real-time updates (if formal API available)
- **Local Government APIs**: City/county-specific APIs as needed (post-MVP)

### Integration Flow

```text
User Input: Address or Zip Code
        ↓
Google Civic API (Divisions)
        ↓
OCD-IDs: Federal, State, Local
        ↓
    ┌───┴───┐
    ↓       ↓
Federal    State
OCD-IDs    OCD-IDs
    ↓       ↓
ProPublica  OpenStates
Congress    API
API         ↓
(Post-MVP)  State Reps
    ↓       ↓
    └───┬───┘
        ↓
Combined Results
```

## Coverage Gaps (MVP)

**Uncovered**:
- Local representatives (mayors, city council, county commissioners)
- Reason: No comprehensive local government API available
- Mitigation: Document gap, implement in post-MVP with city/county-specific integrations

**Partial Coverage**:
- Federal representatives (covered post-MVP with ProPublica)
- Reason: MVP focuses on state legislators per Phase 2 priorities
- Mitigation: Design extensible data model to add federal reps later

## Rate Limit Strategy

| API | Free Tier Limit | Estimated MVP Usage | Caching Impact | Risk Level |
|-----|----------------|---------------------|----------------|------------|
| Google Civic | 25,000 req/day | ~100 req/day (7-day cache) | High reduction | Low |
| OpenStates | 5,000 req/day | ~200 req/day (24-hour cache) | High reduction | Low |
| ProPublica | 5,000 req/day | ~50 req/day (24-hour cache, post-MVP) | High reduction | Low |

**Conclusion**: Free tiers sufficient for MVP with multi-layer caching strategy.

## Cost Analysis

| API | Free Tier | Paid Plans | Projected MVP Cost |
|-----|-----------|------------|-------------------|
| Google Civic | 25,000 req/day | N/A (sufficient) | $0/month |
| OpenStates | 5,000 req/day | $50/mo (100K req/day) | $0/month (free tier sufficient) |
| ProPublica | 5,000 req/day | N/A (sufficient) | $0/month |

**Total Projected Cost**: $0/month for MVP

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Google Civic divisions endpoint deprecated | High | Low | Monitor Google announcements, plan migration to OCD-ID service if needed |
| OpenStates rate limit exceeded | Medium | Low | Implement aggressive caching (24-hour TTL), upgrade to paid plan if needed |
| OpenStates data staleness | Medium | Medium | Display data freshness timestamp, implement manual refresh endpoint |
| Missing local representative data | High | High (known gap) | Document limitation clearly, roadmap for post-MVP city/county integrations |

## Recommendation

**Primary API for MVP**: **OpenStates.org API** for state representative details  
**Supporting API**: **Google Civic Information API (Divisions)** for address/zip → OCD-ID resolution  
**Post-MVP Addition**: **ProPublica Congress API** for federal representative details

**Justification**:
1. **Coverage**: OpenStates covers all state legislators (MVP focus), Google Civic provides address/zip lookup
2. **Data Freshness**: OpenStates updates weekly during sessions, sufficient for MVP
3. **Rate Limits**: Free tiers sufficient with caching (24-hour reps, 7-day divisions)
4. **Pricing**: Both free tier, $0/month cost
5. **Integration Effort**: Low (both have stable REST APIs, clear docs, OCD-ID support)

**Next Steps**:
1. Register API keys for Google Civic and OpenStates
2. Implement OCD-ID resolution with Google Civic divisions endpoint
3. Implement state representative lookup with OpenStates API
4. Test with 6-10 diverse addresses (urban, rural, military, PO Box, etc.)
5. Validate coverage and data quality
6. Document any limitations discovered during testing
