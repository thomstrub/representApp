# representApp Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-07

## Active Technologies
- Python 3.9 (AWS Lambda runtime) + AWS Lambda Powertools (Logger, Tracer, Validator), boto3 (AWS SDK), requests (HTTP client) (003-address-lookup)
- N/A (no persistent storage in MVP; caching deferred to Phase 4) (003-address-lookup)
- React 18+ with TypeScript (modern JSX syntax) (004-address-ui)
- N/A (frontend state management only - React hooks: useState, useEffect; no persistent storage in browser) (004-address-ui)
- Python 3.9 (AWS Lambda runtime) + AWS Lambda Powertools 2.30.0, googlemaps Python library, boto3, requests (005-geolocation-lookup)
- DynamoDB (not used in MVP - direct API calls only), AWS Systems Manager Parameter Store (API keys) (005-geolocation-lookup)

- Python 3.9+ (backend), Documentation/Research (this feature) + GitHub search/API, Google Civic Information API (divisions endpoint), OpenStates.org API docs, Washington State Legislature API docs (001-api-integration-research)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.9+ (backend), Documentation/Research (this feature): Follow standard conventions

## Recent Changes
- 005-geolocation-lookup: Added Python 3.9 (AWS Lambda runtime) + AWS Lambda Powertools 2.30.0, googlemaps Python library, boto3, requests
- 004-address-ui: Added React 18+ with TypeScript (modern JSX syntax)
- 003-address-lookup: Added Python 3.9 (AWS Lambda runtime) + AWS Lambda Powertools (Logger, Tracer, Validator), boto3 (AWS SDK), requests (HTTP client)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
