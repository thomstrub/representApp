# representApp Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-07

## Active Technologies
- Python 3.9 (AWS Lambda runtime) + AWS Lambda Powertools (Logger, Tracer, Validator), boto3 (AWS SDK), requests (HTTP client) (003-address-lookup)
- N/A (no persistent storage in MVP; caching deferred to Phase 4) (003-address-lookup)

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
- 003-address-lookup: Added Python 3.9 (AWS Lambda runtime) + AWS Lambda Powertools (Logger, Tracer, Validator), boto3 (AWS SDK), requests (HTTP client)

- 001-api-integration-research: Added Python 3.9+ (backend), Documentation/Research (this feature) + GitHub search/API, Google Civic Information API (divisions endpoint), OpenStates.org API docs, Washington State Legislature API docs

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
