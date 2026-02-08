# Project Overview

## Mission

The overall goal of this project is to help bridge the gap between political infrastructure and the day-to-day lives of constituents. Represent App aims to provide citizens with the same knowledge and access to their representatives that lobbyists have, making political information easily digestible and actionable.

## Introduction

Represent App is a full-stack serverless application for managing information about political representatives. The application uses a modern cloud-native architecture with a React frontend and Python Lambda backend, designed to help users easily find, contact, and track their local, state, and federal representatives.

## Architecture

The application follows a serverless architecture pattern:

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │────────▶│  API Gateway │────────▶│   Lambda    │
│  Frontend   │         │   (HTTP v2)  │         │   Handler   │
└─────────────┘         └──────────────┘         └──────┬──────┘
                                                         │
                                                         ▼
                                                  ┌─────────────┐
                                                  │  DynamoDB   │
                                                  │    Table    │
                                                  └─────────────┘
```

### Components

- **Frontend**: React-based SPA with map-based interface (future) served via S3/CloudFront
- **API Gateway**: HTTP API v2 for RESTful endpoints
- **Lambda Functions**: Python 3.9 handlers using AWS Lambda Powertools
- **DynamoDB**: NoSQL database for data persistence with multi-tenancy support
- **Infrastructure**: AWS CDK for Infrastructure as Code
- **Location Services**: Location-based queries (zip code) for finding representatives

### Key Design Principles

- **Location-Based**: Uses location data to help users find their representatives and relevant issues
- **Multi-Tenancy**: Leverages AWS Lambda's tenant isolation mode for secure state/county data separation
  - Each state or county operates as an isolated tenant
  - Execution environments are never shared across tenants
  - Tenant-specific data cached in memory remains isolated
  - Simplified architecture compared to function-per-state approach
- **Data Aggregation**: Backend system aggregates and analyzes political data from multiple sources
- **Accessibility**: Makes political information easily digestible without dense legal language

### Multi-Tenant Architecture

The application uses AWS Lambda's new tenant isolation mode (announced November 2025) to achieve secure multi-tenancy:

- **Tenant Model**: Each state or county is treated as a separate tenant
- **Compute Isolation**: Lambda automatically isolates execution environments per tenant
- **Performance**: Maintains warm execution environment benefits while ensuring isolation
- **Security**: Prevents cross-tenant data access without custom isolation logic
- **Observability**: Built-in tenant-aware logging with CloudWatch integration

This approach eliminates the need for:
- Separate Lambda functions per state/county
- Custom tenant isolation frameworks
- Complex operational management of thousands of functions

## Technology Stack

### Frontend

- React
- React DOM
- Material UI (MUI) for components
- CSS for styling
- Jest for testing

### Backend

- **Runtime**: Python 3.9
- **Framework**: AWS Lambda Powertools
  - Logger with structured logging
  - Event parsing and validation (Pydantic)
  - X-Ray tracing
- **API**: HTTP API Gateway v2 with Lambda proxy integration
- **Database**: DynamoDB with on-demand billing
- **Infrastructure**: AWS CDK (Python)
- **Testing**: pytest, moto, pytest-cov
- **Multi-Tenancy**: Lambda tenant isolation mode
  - Per-tenant execution environment isolation
  - Tenant ID passed via `X-Amz-Tenant-Id` header
  - State/county identifiers used as tenant IDs

### AWS Services

- AWS Lambda
- Amazon API Gateway (HTTP API v2)
- Amazon DynamoDB
- AWS CloudWatch (logging and monitoring)
- AWS X-Ray (tracing)

## Getting Started

### Prerequisites

**Backend:**
- Python 3.9 or higher
- AWS CLI configured
- AWS CDK CLI: `npm install -g aws-cdk`
- AWS account with appropriate permissions

**Frontend:**
- Node.js (v16 or higher)
- npm (v7 or higher)

### Installation

**Backend Setup:**
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install infrastructure dependencies
cd ../infrastructure
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your AWS account details
```

**Frontend Setup:**
```bash
# To be implemented
```

## Development Workflow

### Backend Development

1. **Make code changes** in `backend/src/`
2. **Run tests**: `cd backend && pytest`
3. **Test locally** (optional): `sam local start-api`
4. **Deploy**: `cd infrastructure && cdk deploy`

### Running Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=src --cov-report=html
```

### Local Development

Use AWS SAM CLI for local testing:
```bash
sam local start-api
```

## Deployment

### First Time Setup

```bash
# Bootstrap CDK (once per AWS account/region)
cd infrastructure
cdk bootstrap
```

### Deploy Backend

```bash
cd infrastructure
cdk deploy
```

This will create:
- DynamoDB table
- Lambda function
- API Gateway
- CloudWatch log groups
- All necessary IAM roles and permissions

### Outputs

After deployment, note the following outputs:
- **ApiUrl**: The HTTP API Gateway endpoint
- **TableName**: The DynamoDB table name
- **LambdaArn**: The Lambda function ARN

## Project Structure

```
representApp/
├── backend/
│   ├── src/
│   │   ├── handlers/       # Lambda handlers
│   │   ├── models/         # Data models
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── infrastructure/
│   ├── stacks/             # CDK stacks
│   ├── app.py              # CDK entry point
│   └── requirements.txt
├── docs/                   # Documentation
└── Makefile                # Build automation
```

## API Endpoints

### MVP Endpoints
- `GET /api/representatives?zip={zipcode}` - Get representatives for a zip code
- `GET /api/health` - Health check endpoint

### Future Endpoints (Post-MVP)
- `GET /api/representatives/{id}/votes` - Get voting record for a representative
- `GET /api/issues` - Get tracked issues
- Local data management CRUD endpoints (if needed)

## Useful Commands

```bash
# Install all dependencies
make install

# Run tests
make test

# Deploy to AWS
make deploy

# View differences
make diff

# Clean up
make clean

# See all available commands
make help
```

## Next Steps

### Current Phase - Phase 2: Design Research Implementation

**Goal**: Implement patterns and approaches from analyzed civic tech repositories to build MVP functionality.

See [docs/design-research.md](design-research.md) for detailed implementation instructions.

**Phase 2 Priorities** (Execute in Order):
1. 🔲 Implement Google Civic Information API Integration
   - Register API key and store in Parameter Store
   - Add API request handling in Lambda
   - Implement error handling and retry logic
2. 🔲 Design and Implement DynamoDB Schema
   - Multi-tenant table structure (state-based partitions)
   - GSI for zip code lookups
   - TTL configuration for cache expiration
3. 🔲 Implement OCD Division ID Parsing
   - Create utility module with regex patterns
   - Add government level categorization
   - Support filtering by level
4. 🔲 Implement Multi-Layer Caching Strategy
   - Lambda memory cache (warm environment)
   - DynamoDB persistent cache (24-hour TTL)
   - Cache metrics and monitoring
5. 🔲 Add comprehensive tests and validation
   - Unit tests for all components
   - Integration tests for API flow
   - Performance testing (<3s cache miss, <500ms hit)

**Previous Phases**:
1. ✅ Phase 1: Set up Python Lambda backend with Powertools
2. ✅ Phase 1: Create CDK infrastructure

### Upcoming Phases

**Phase 3: Frontend Development**
7. 🔲 Implement React frontend with zip code input
8. 🔲 Display representatives by government level
9. 🔲 Add responsive design with Material UI

**Phase 4: Documentation & Deployment**
10. 🔲 Add API documentation (OpenAPI)
11. 🔲 Set up monitoring and alarms for API performance
12. 🔲 Deploy to production and test with real zip codes

### Post-MVP Features

- Local data storage and CRUD operations for representative information
- Representative voting record tracking (integrate with ProPublica Congress API)
- Issue tracking and alerts
- Map-based interface to visualize political data
- Map-based zooming that integrates political boundaries with location data
- Advanced search and filtering capabilities
- User authentication (Cognito)
- CI/CD pipeline
- Additional government API integrations for more comprehensive data

## User Stories

### End Users
- As a user, I want to know who my local, state, and federal representatives are, what they stand for, and how to contact them easily
- As a user, I want to see how my representatives have voted on issues that matter to me
- As a user, I want to easily digest political information without sifting through dense legal language
- As a user, I want the same knowledge and access with my representatives that lobbyists have

### Developers
- As a developer, I want to easily deploy and manage the application infrastructure using code
- As a developer, my first priority is a backend that provides information based on location (zip code)
- As a developer, I want a frontend interface to interact with the backend that will evolve into an interactive map-based interface
2. ✅ Implement CRUD API endpoints
3. ✅ Create DynamoDB data layer
4. ✅ Add comprehensive tests
5. ✅ Create CDK infrastructure
6. 🔲 Implement React frontend
7. 🔲 Add authentication (Cognito)
8. 🔲 Set up CI/CD pipeline
9. 🔲 Add API documentation (OpenAPI)
10. 🔲 Implement monitoring and alarms


