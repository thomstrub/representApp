# Quickstart Guide: Address Lookup API

**Feature**: 003-address-lookup  
**Audience**: Developers setting up local development environment  
**Last Updated**: February 8, 2026

## Prerequisites

Before starting, ensure you have:

- **Python 3.9+** installed (`python --version`)
- **AWS CLI** configured with credentials (`aws configure`)
- **AWS CDK** installed (`npm install -g aws-cdk`)
- **Git** for version control
- **API Keys**:
  - Google Civic Information API key (register at https://console.cloud.google.com/)
  - OpenStates API key (register at https://openstates.org/accounts/signup/)

## Quick Setup (5 minutes)

### 1. Clone and Navigate

```bash
git clone https://github.com/thomstrub/representApp.git
cd representApp
git checkout 003-address-lookup
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Store API Keys in AWS Parameter Store

```bash
# Google Civic API Key
aws ssm put-parameter \
    --name "/represent-app/google-civic-api-key" \
    --value "YOUR_GOOGLE_CIVIC_API_KEY_HERE" \
    --type "SecureString" \
    --overwrite

# OpenStates API Key
aws ssm put-parameter \
    --name "/represent-app/openstates-api-key" \
    --value "YOUR_OPENSTATES_API_KEY_HERE" \
    --type "SecureString" \
    --overwrite
```

**Note**: Replace `YOUR_*_API_KEY_HERE` with actual API keys. Never commit keys to version control.

### 4. Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires API keys in Parameter Store)
pytest tests/integration/ -v

# All tests with coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### 5. Deploy Infrastructure

```bash
cd ../infrastructure
cdk deploy
```

This deploys:
- Lambda function with address lookup handler
- API Gateway HTTP API v2 endpoint
- CloudWatch log groups
- X-Ray tracing configuration
- IAM roles with Parameter Store permissions

**Deployment Output**:
```
Outputs:
BackendStack.ApiEndpoint = https://abc123xyz.execute-api.us-west-2.amazonaws.com
```

## Local Development Workflow

### Running Lint Checks

```bash
cd backend

# Check code style
pylint src/ tests/

# Auto-format code
black src/ tests/

# Run both
make lint
```

### Running Tests (TDD Workflow)

Follow the Red-Green-Refactor cycle:

```bash
# 1. RED: Write failing test
# (Edit tests/unit/test_address_lookup.py)

# 2. Run test and verify it fails
pytest tests/unit/test_address_lookup.py::test_valid_address -v

# 3. GREEN: Implement minimal code to pass
# (Edit src/handlers/api.py or src/services/google_civic.py)

# 4. Run test and verify it passes
pytest tests/unit/test_address_lookup.py::test_valid_address -v

# 5. REFACTOR: Improve code while keeping tests green
# (Refactor without changing behavior)

# 6. Re-run all tests
pytest tests/unit/ -v
```

### Manual API Testing

Once deployed, test the API endpoint:

```bash
# Set API endpoint from CDK output
API_ENDPOINT="https://abc123xyz.execute-api.us-west-2.amazonaws.com"

# Test valid address
curl "${API_ENDPOINT}/representatives?address=1600+Pennsylvania+Ave+NW,+Washington,+DC+20500" | jq .

# Test invalid address (missing parameter)
curl "${API_ENDPOINT}/representatives" | jq .

# Test address not found
curl "${API_ENDPOINT}/representatives?address=123+Fake+Street" | jq .
```

### Viewing Logs

```bash
# Tail Lambda logs in real-time
aws logs tail /aws/lambda/representApp-backend --follow

# Query logs for errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/representApp-backend \
    --filter-pattern "ERROR"
```

## Project Structure

```
backend/
├── src/
│   ├── handlers/
│   │   └── api.py                    # Lambda handler with /representatives route
│   ├── models/
│   │   └── base.py                   # Representative, Division, etc. entities
│   ├── services/
│   │   ├── google_civic.py           # Google Civic API client
│   │   ├── openstates.py             # OpenStates API client
│   │   └── parameter_store.py        # API key retrieval
│   └── utils/
│       ├── validators.py             # Address validation logic
│       └── ocd_parser.py             # OCD-ID parsing and categorization
└── tests/
    ├── unit/                         # Unit tests for all modules
    └── integration/                  # API Gateway → Lambda → External API tests
```

## Common Tasks

### Add a New Test

```bash
# Create test file
touch backend/tests/unit/test_new_feature.py

# Write test following existing patterns
cat > backend/tests/unit/test_new_feature.py << 'EOF'
import pytest
from src.services.google_civic import GoogleCivicClient

def test_google_civic_client_initialization():
    client = GoogleCivicClient(api_key="test_key")
    assert client.api_key == "test_key"

def test_google_civic_address_lookup():
    # Arrange
    client = GoogleCivicClient(api_key="test_key")
    address = "1600 Pennsylvania Ave NW, Washington, DC 20500"
    
    # Act
    divisions = client.lookup_divisions(address)
    
    # Assert
    assert len(divisions) > 0
    assert divisions[0]['ocd_id'].startswith('ocd-division/country:us')
EOF

# Run new test
pytest backend/tests/unit/test_new_feature.py -v
```

### Add a New Service Method

```bash
# Edit service file
vim backend/src/services/openstates.py

# Add method with docstring
def get_representatives_by_division(self, ocd_id: str) -> list:
    """
    Retrieve representatives for a given OCD division ID.
    
    Args:
        ocd_id: OCD division identifier (e.g., "ocd-division/country:us/state:ca")
    
    Returns:
        List of representative dictionaries with id, name, office, etc.
    
    Raises:
        ValueError: If ocd_id is invalid format
        RequestException: If OpenStates API call fails
    """
    # Implementation here
    pass

# Write test FIRST (TDD)
vim backend/tests/unit/test_openstates.py

# Run test (RED)
pytest backend/tests/unit/test_openstates.py::test_get_representatives_by_division -v

# Implement method (GREEN)
# Refactor if needed
```

### Update API Contract

```bash
# Edit OpenAPI schema
vim specs/003-address-lookup/contracts/openapi.yaml

# Validate schema
npx @apidevtools/swagger-cli validate specs/003-address-lookup/contracts/openapi.yaml

# Generate API documentation
npx @redocly/cli build-docs specs/003-address-lookup/contracts/openapi.yaml -o docs/api.html
open docs/api.html
```

### Deploy After Changes

```bash
# Run full test suite
cd backend
make test

# Run lint checks
make lint

# Deploy infrastructure
cd ../infrastructure
cdk deploy

# Verify deployment
curl "${API_ENDPOINT}/representatives?address=1600+Pennsylvania+Ave+NW,+Washington,+DC+20500" | jq .
```

## Troubleshooting

### Issue: ImportError when running tests

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure PYTHONPATH includes backend/src
export PYTHONPATH="${PWD}/backend:${PYTHONPATH}"

# Or install package in development mode
cd backend
pip install -e .
```

### Issue: Parameter Store access denied

**Problem**: `AccessDeniedException: User is not authorized to perform: ssm:GetParameter`

**Solution**:
```bash
# Check IAM permissions for your AWS profile
aws iam get-user

# Ensure Lambda execution role has ssm:GetParameter permissions
# (CDK should create this automatically; check infrastructure/stacks/backend_stack.py)
```

### Issue: API returns 503 Service Unavailable

**Problem**: External API (Google Civic or OpenStates) is down or rate-limited

**Solution**:
```bash
# Check CloudWatch logs for specific error
aws logs tail /aws/lambda/representApp-backend --follow

# Look for EXTERNAL_SERVICE_ERROR or RATE_LIMIT_EXCEEDED errors

# Verify API keys are valid
aws ssm get-parameter --name "/represent-app/google-civic-api-key" --with-decryption
aws ssm get-parameter --name "/represent-app/openstates-api-key" --with-decryption

# Test external APIs directly
curl "https://www.googleapis.com/civicinfo/v2/divisions?key=YOUR_KEY"
curl "https://v3.openstates.org/people?jurisdiction=ca&apikey=YOUR_KEY"
```

### Issue: Tests fail with moto mock errors

**Problem**: `ValueError: Attempted to mock AWS service but moto not installed`

**Solution**:
```bash
# Reinstall test dependencies
cd backend
pip install -r requirements.txt
pip install moto[all]

# Verify moto installation
python -c "import moto; print(moto.__version__)"
```

## Performance Testing

### Load Test with Apache Bench

```bash
# Install ab (Apache Bench)
# macOS: brew install httpd
# Linux: apt-get install apache2-utils

# Run 100 requests with 10 concurrent
ab -n 100 -c 10 \
   "${API_ENDPOINT}/representatives?address=1600+Pennsylvania+Ave+NW,+Washington,+DC+20500"

# Target: <3 seconds p95 latency
```

### Monitor Lambda Metrics

```bash
# View Lambda metrics in CloudWatch
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=representApp-backend \
    --start-time 2026-02-08T00:00:00Z \
    --end-time 2026-02-08T23:59:59Z \
    --period 3600 \
    --statistics Average,Maximum
```

## Next Steps

After completing local setup:

1. **Read the Spec**: Review [spec.md](spec.md) for complete feature requirements
2. **Understand Data Models**: See [data-model.md](data-model.md) for entity definitions
3. **Review API Contract**: Check [contracts/openapi.yaml](contracts/openapi.yaml) for endpoint details
4. **Follow TDD**: Write tests first (Red), implement code (Green), refactor (Refactor)
5. **Commit Frequently**: Use conventional commits (e.g., `feat(api): add address validation`)

## Resources

- **OpenStates API Docs**: https://docs.openstates.org/api-v3/
- **Google Civic API Docs**: https://developers.google.com/civic-information
- **AWS Lambda Powertools**: https://docs.powertools.aws.dev/lambda/python/
- **pytest Documentation**: https://docs.pytest.org/
- **CDK Python Guide**: https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html

## Support

For issues or questions:
- **Spec Issues**: File issue in GitHub with label `003-address-lookup`
- **Infrastructure**: Check `infrastructure/README.md`
- **Testing**: See `docs/testing-guidelines.md`
