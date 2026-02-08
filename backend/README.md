# Represent App Backend

Python Lambda-based backend for the Represent App using AWS Powertools.

## Architecture

- **Lambda Functions**: Python 3.9 handlers using AWS Lambda Powertools
- **API Gateway**: HTTP API (v2) with Lambda proxy integration
- **Database**: DynamoDB for data persistence
- **Infrastructure**: AWS CDK for Infrastructure as Code

## Project Structure

```
backend/
├── src/
│   ├── handlers/      # Lambda handler functions
│   │   └── api.py     # Main API handler with routing
│   ├── models/        # Data models and business logic
│   │   ├── base.py    # Base response and error models
│   │   ├── domain.py  # Domain-specific models (Representative)
│   │   └── store.py   # DynamoDB persistence layer
│   └── utils/         # Utility functions
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
└── requirements.txt   # Python dependencies

infrastructure/
├── stacks/
│   └── backend_stack.py  # CDK stack definition
├── app.py                # CDK app entry point
└── requirements.txt      # CDK dependencies
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 16+ (for AWS CDK)
- AWS CLI configured
- AWS CDK CLI installed: `npm install -g aws-cdk`

### Installation

1. **Install Python dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Install CDK dependencies**:
```bash
cd infrastructure
pip install -r requirements.txt
```

3. **Create environment file**:
```bash
cp .env.example .env
# Edit .env with your AWS account details
```

## Development

### Running Tests

```bash
cd backend
pytest
```

### Running Tests with Coverage

```bash
cd backend
pytest --cov=src --cov-report=html
```

### Local Testing with SAM

```bash
# Install AWS SAM CLI first
brew tap aws/tap
brew install aws-sam-cli

# Start local API
sam local start-api
```

## Deployment

### First Time Setup

```bash
# Bootstrap CDK (only needed once per account/region)
cd infrastructure
cdk bootstrap
```

### Deploy to AWS

```bash
cd infrastructure
cdk deploy
```

### View Stack Outputs

After deployment, you'll see outputs including:
- API Gateway URL
- DynamoDB Table Name
- Lambda Function ARN

## API Endpoints

### Representatives

- **GET** `/api/representatives` - List all representatives
- **GET** `/api/representatives/{id}` - Get a specific representative
- **POST** `/api/representatives` - Create a new representative
- **PUT/PATCH** `/api/representatives/{id}` - Update a representative
- **DELETE** `/api/representatives/{id}` - Delete a representative

### Example Request

**Create Representative:**
```bash
curl -X POST https://your-api-url/api/representatives \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "position": "Senator",
    "state": "NY",
    "party": "Democratic"
  }'
```

**List Representatives:**
```bash
curl https://your-api-url/api/representatives
```

## Environment Variables

- `DDB_TABLE_NAME`: DynamoDB table name
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `POWERTOOLS_SERVICE_NAME`: Service name for logging/metrics
- `AWS_REGION`: AWS region

## Features

- ✅ RESTful API with CRUD operations
- ✅ AWS Lambda Powertools integration
  - Logger with structured logging
  - Event parsing and validation
  - Error handling
- ✅ DynamoDB persistence layer
- ✅ Comprehensive unit tests with moto
- ✅ Type hints and Pydantic models
- ✅ HTTP API Gateway v2
- ✅ Infrastructure as Code with CDK
- ✅ X-Ray tracing enabled

## Next Steps

1. Add authentication/authorization (Cognito, JWT)
2. Implement rate limiting
3. Add caching layer (ElastiCache/DAX)
4. Set up CI/CD pipeline
5. Add API documentation (OpenAPI/Swagger)
6. Implement monitoring and alarms
7. Add additional endpoints based on requirements

## Resources

- [AWS Lambda Powertools Documentation](https://awslabs.github.io/aws-lambda-powertools-python/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [API Gateway V2 Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
