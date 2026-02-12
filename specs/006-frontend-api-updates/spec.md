# Feature Specification: Frontend API Integration Updates

**Feature Branch**: `006-frontend-api-updates`  
**Created**: February 10, 2026  
**Status**: Draft  
**Input**: User description: "Update the frontend to handle the backend implementation updates"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Representatives Grouped by Government Level (Priority: P1)

When a user searches for their address, they should see representatives organized by federal, state, and local government levels, making it clear which officials serve at each level.

**Why this priority**: This is the core functionality that delivers immediate value - users can see their representatives organized in a meaningful way. Without this, the frontend cannot display the new backend data structure.

**Independent Test**: Can be fully tested by entering an address and verifying that representatives appear under "Federal", "State", and "Local" headings, delivers organized view of political representation.

**Acceptance Scenarios**:

1. **Given** a user enters a valid address, **When** the API returns representatives at multiple government levels, **Then** representatives are displayed grouped under "Federal Representatives", "State Representatives", and "Local Representatives" headings
2. **Given** a user's address has only federal and state representatives, **When** the API returns no local representatives, **Then** only Federal and State sections are shown
3. **Given** a user views the results, **When** representatives are grouped by level, **Then** each representative card shows their name, office, party, jurisdiction, and photo

---

### User Story 2 - Display Search Context and Warnings (Priority: P2)

Users should see confirmation of what address was searched and be informed of any limitations in the data returned (such as missing local representatives).

**Why this priority**: This provides transparency and helps users understand the completeness of results and what address was actually resolved.

**Independent Test**: Can be tested by entering various addresses and verifying the resolved address displays correctly and any warnings appear prominently.

**Acceptance Scenarios**:

1. **Given** a user searches for an address, **When** results are returned, **Then** the normalized/resolved address is displayed prominently
2. **Given** the API returns warnings, **When** results are displayed, **Then** warning messages appear in a visually distinct callout above the representatives
3. **Given** the API returns metadata with total count, **When** results are displayed, **Then** a summary shows "Found X representatives across Y government levels"

---

### User Story 3 - View Representative Details with Jurisdiction (Priority: P3)

Users should be able to see which jurisdiction each representative serves (e.g., "District of Columbia", "United States") to understand their scope of authority.

**Why this priority**: This adds valuable context but is not essential for the MVP - users can still identify their representatives without jurisdiction labels.

**Independent Test**: Can be tested by viewing any representative and verifying their jurisdiction is clearly labeled.

**Acceptance Scenarios**:

1. **Given** a representative is displayed, **When** the user views the card, **Then** the jurisdiction name is shown (e.g., "District of Columbia")
2. **Given** multiple representatives are shown, **When** they serve different jurisdictions, **Then** each card clearly shows its respective jurisdiction

---

### Edge Cases

- When the API returns an empty array for all government levels, system displays a helpful message explaining no representatives were found and suggests checking the address
- When a representative has missing photo_url, system displays the representative's initials in a colored circle as an avatar fallback
- Representative contact information (email, phone, address, website) when available is displayed as clickable links/buttons with icons (email icon → mailto:, phone icon → tel:, etc.)
- What happens when a representative has missing data fields (no email, no phone)?
- What happens when the API returns warnings but still includes representative data?
- What happens when coordinates are missing from metadata?
- What happens when government_levels array in metadata is empty?
- How does the UI handle very long jurisdiction names?
- What happens if the resolved address differs significantly from the user's input?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse the new nested API response structure with `representatives`, `metadata`, and `warnings` top-level keys
- **FR-002**: System MUST display representatives grouped by government level (federal, state, local) in separate sections
- **FR-003**: System MUST display the resolved address from metadata.address to show users what location was actually searched
- **FR-004**: System MUST display warning messages from the warnings array when present
- **FR-005**: System MUST handle cases where one or more government level arrays are empty without breaking the UI
- **FR-006**: System MUST display representative jurisdiction information alongside other representative details
- **FR-007**: System MUST show representative contact information (email, phone, address, website) when available in the response as clickable links/buttons with icons (email icon → mailto:, phone icon → tel:, etc.)
- **FR-008**: System MUST gracefully handle missing optional fields (photo_url, email, phone, address, website) without showing "null" or "undefined"; when photo_url is missing, display representative's initials in a colored circle as avatar fallback
- **FR-009**: System MUST display metadata total_count and government_levels array information
- **FR-010**: System MUST update TypeScript type definitions to match the new API response structure
- **FR-011**: System MUST maintain backward compatibility for loading states and error handling
- **FR-012**: System MUST display representative party affiliation alongside name and office
- **FR-013**: System MUST display a helpful message when all government level arrays are empty, explaining no representatives were found and suggesting the user verify their address

### Key Entities

- **Representative**: An elected or appointed official with properties: id (OCD identifier), name, office title, party affiliation, contact details (email, phone, address, website), photo URL, government level, and jurisdiction
- **API Response**: The container structure with three main sections: representatives (grouped by level), metadata (search context), and warnings (data limitations)
- **Metadata**: Search context including normalized address, geographic coordinates, total representative count, and list of government levels present in results
- **Government Level Group**: A collection of representatives serving at the same level (federal, state, or local)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view representatives organized by government level within 1 second of API response
- **SC-002**: UI successfully displays representative data for addresses returning 1-50 representatives without performance degradation
- **SC-003**: Users can see the resolved address and understand what location was searched in 100% of successful queries
- **SC-004**: Warning messages are visible and clearly indicate data limitations when present
- **SC-005**: UI gracefully handles missing optional data fields without displaying technical errors or null values
- **SC-006**: All existing frontend tests continue to pass or are updated to reflect new API structure
- **SC-007**: Representative contact information is displayed as clickable, actionable links when available, with appropriate fallbacks for missing data
- **SC-008**: Users can distinguish between different jurisdictions when viewing multiple representatives

## Clarifications

### Session 2026-02-10

- Q: When the API returns zero representatives across all government levels (federal, state, and local arrays are all empty), how should the UI respond? → A: Show a helpful message explaining no representatives were found and suggest checking the address
- Q: When a representative's photo_url is null or missing, what should be displayed in the representative card? → A: Show the representative's initials in a colored circle (avatar fallback)
- Q: When representative contact information (email, phone, address, website) is available, how should this information be displayed in the representative card? → A: Show as clickable links/buttons with icons (email icon → mailto:, phone icon → tel:, etc.)
