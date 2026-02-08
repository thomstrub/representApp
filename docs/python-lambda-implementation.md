# Python Lambda Implementation Guide

This document provides a comprehensive guide for implementing a Python Lambda-based backend using AWS Powertools with multi-tenant isolation, based on the [rbogle/example_api_lambda_powertools](https://github.com/rbogle/example_api_lambda_powertools) repository.

## Multi-Tenant Architecture Overview

This implementation leverages **AWS Lambda's tenant isolation mode** (launched November 2025) to provide secure multi-tenancy across states and counties:

### Why Multi-Tenancy for Represent App?

1. **Varying Data Structures**: Different states and counties have different political structures, data formats, and rules
2. **Data Isolation**: Sensitive representative and constituent data must remain isolated per jurisdiction
3. **Simplified Operations**: Single Lambda function handles all states/counties without operational sprawl
4. **Performance**: Tenant-specific caching of state rules and data with guaranteed isolation

### How Lambda Tenant Isolation Works

- **Tenant Definition**: Each state or county is a tenant (e.g., "CA", "NY-Albany", "TX-Harris")
- **Execution Environment Isolation**: Lambda creates separate environments per tenant
- **Request Routing**: Tenant ID included in each request routes to correct isolated environment
- **Memory/Disk Isolation**: Data cached in memory or written to /tmp is never shared across tenants
- **Observability**: CloudWatch logs automatically include tenant ID for debugging

### Benefits Over Alternatives

| Approach | Pros | Cons |
|----------|------|------|
| **Function per State** | Strongest isolation | 50+ functions to manage, operational complexity |
| **Custom Framework** | Full control | Bug-prone, requires ongoing maintenance |
| **Lambda Tenant Isolation** | Built-in isolation, simple ops, performant | Slightly more cold starts per tenant |

### Trade-offs

- **More Cold Starts**: Each tenant gets its own execution environment, so expect more cold starts
- **Pricing**: Small fee per tenant-specific execution environment created
- **Configuration Immutable**: Tenant isolation must be enabled at function creation time
- **Shared IAM Role**: All tenants share the function's execution role (can be mitigated with scoped credentials)

## Phase 1: Investigation & Analysis (COMPLETED)

### Repository Analysis Summary

**Source Repository:** `rbogle/example_api_lambda_powertools`

**Key Components Identified:**

1. **Lambda Handler Structure** (`src/api.py`)
   - Uses AWS Lambda Powertools Logger, Parser, and Data Classes
   - Implements APIGatewayProxyEventV2 for event handling
   - Route-based request handling (POST, GET, PATCH, DELETE)
   - Integrates with ModelStore for DynamoDB operations

2. **Data Models** (`src/models.py`)
   - `Model`: Domain object with UUID, name, metadata
   - `ModelStore`: DynamoDB persistence layer with CRUD operations
   - `Response`: Structured HTTP response with error handling
   - `ModelError`: RFC-compliant error schema
   - `ModelEventDetail` & `ModelChangeEvent`: EventBridge integration

3. **Infrastructure (CDK)** (`infra/infra_stack.py`)
   - DynamoDB table with streams enabled
   - Lambda functions with layers for dependencies
   - HTTP API Gateway v2 with Lambda proxy integration
   - EventBridge for domain events
   - CloudWatch logging

4. **Dependencies** (`requirements.txt`)
   ```
   aws-lambda-powertools[pydantic]
   dynamodb-json
   boto3
   pytest, pytest-cov, moto (testing)
   ```

5. **Project Structure**
   ```
   /src/              # Lambda function code
   /infra/            # CDK infrastructure code
   /layers/           # Lambda layers (dependencies)
   /tests/unit/       # Unit tests
   /docs/             # Documentation
   app.py             # CDK app entry point
   requirements.txt   # Python dependencies
   Makefile          # Build and deployment automation
   ```

## Phase 2: Setup Backend Structure

### Agent Instructions for Implementation

**Objective:** Transform the representApp repository into a Python Lambda-based backend following the example repository's patterns.

### Step 1: Create Directory Structure

```bash
# Create backend directory structure
mkdir -p backend/src/{handlers,models,utils}
mkdir -p backend/tests/{unit,integration}
mkdir -p backend/layers
mkdir -p infrastructure
mkdir -p .aws-sam
```

**Expected Outcome:**
```
backend/
├── src/
│   ├── handlers/      # Lambda handler functions
│   ├── models/        # Data models and DynamoDB logic
│   └── utils/         # Utility functions
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
└── layers/            # Lambda layers for dependencies

infrastructure/        # CDK or SAM infrastructure code
```

### Step 2: Copy and Create Core Files

Create the following files in your repository:

#### `backend/requirements.txt`
```python
# AWS Lambda Powertools - core functionality
aws-lambda-powertools[pydantic]==2.30.0

# AWS SDK
boto3>=1.34.0
botocore>=1.34.0

# DynamoDB JSON utilities
dynamodb-json>=1.3

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
moto[dynamodb]>=4.2.0

# Development
python-dotenv>=1.0.0
```

#### `backend/src/__init__.py`
```python
"""
Represent App Backend - Lambda Functions
"""
__version__ = "0.1.0"
```

### Step 3: Implement Base Models

Create `backend/src/models/base.py` with foundational models:

```python
"""
Base models for API responses and errors
"""
from typing import List, Dict, Any, Optional
from aws_lambda_powertools.utilities.parser import BaseModel, Field
from botocore.exceptions import ClientError


class APIError(BaseModel):
    """RFC-compliant error structure"""
    type: str = ""
    title: str = ""
    status: int = 400
    detail: str = ""
    instance: str = ""


class ResponseBody(BaseModel):
    """HTTP response body structure"""
    errors: List[APIError] = Field(default_factory=list)
    data: Optional[Any] = None


class Response(BaseModel):
    """Complete HTTP response structure for Lambda"""
    statusCode: int = 200
    headers: dict = {"Content-Type": "application/json"}
    isBase64Encoded: bool = False
    body: ResponseBody = Field(default_factory=ResponseBody)

    def add_error(self, error: APIError):
        self.statusCode = error.status
        self.body.errors.append(error)

    def add_boto_error(self, error: ClientError):
        err = APIError(
            title=error.response['Error']['Code'],
            detail=error.response['Error']['Message'],
            status=error.response['ResponseMetadata']['HTTPStatusCode']
        )
        self.add_error(err)

    def dump(self) -> Dict:
        """Return properly formatted response for Lambda"""
        result = self.dict(exclude={'body'})
        result['body'] = self.body.json() if self.body else ''
        return result
```

### Step 4: Implement Domain Models

Create `backend/src/models/domain.py` for your app-specific models:

```python
"""
Domain models for Represent App
"""
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from aws_lambda_powertools.utilities.parser import BaseModel, Field, validator


class Representative(BaseModel):
    """Model for a political representative"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    position: str  # e.g., "Senator", "Representative"
    district: Optional[str] = None
    state: str
    party: Optional[str] = None
    contact_info: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('id')
    def validate_id(cls, v: str) -> str:
        """Validate UUID format"""
        try:
            UUID(v)
        except ValueError:
            v = str(uuid4())
        return v


# Add more domain models as needed for your app
```

### Step 5: Implement Data Store Layer

Create `backend/src/models/store.py`:

```python
"""
DynamoDB persistence layer
"""
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from typing import List, Optional
from .domain import Representative
from .base import Response, APIError


class RepresentativeStore:
    """DynamoDB operations for Representatives"""
    
    def __init__(self, table_name: str, region: str = "us-east-1"):
        self.table_name = table_name
        self.region = region
        self.conn = boto3.resource('dynamodb', region_name=region)
        self.table = self.conn.Table(table_name)
        self.logger = Logger(child=True)

    def create(self, representative: Representative) -> Response:
        """Create a new representative"""
        response = Response()
        item = representative.dict()
        
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=Attr('id').not_exists()
            )
            response.body.data = [representative.dict()]
        except ClientError as e:
            self.logger.error(f"Error creating representative: {e}")
            response.add_boto_error(e)
        
        return response

    def get(self, rep_id: str) -> Response:
        """Get a representative by ID"""
        response = Response()
        
        try:
            result = self.table.get_item(Key={"id": rep_id})
            item = result.get('Item')
            
            if item:
                response.body.data = [Representative(**item).dict()]
            else:
                error = APIError(
                    status=404,
                    title="Not Found",
                    detail=f"Representative with ID {rep_id} not found"
                )
                response.add_error(error)
        except ClientError as e:
            self.logger.error(f"Error getting representative: {e}")
            response.add_boto_error(e)
        
        return response

    def list_all(self) -> Response:
        """Get all representatives"""
        response = Response()
        items = []
        
        try:
            result = self.table.scan()
            items.extend(result.get('Items', []))
            
            # Handle pagination
            while 'LastEvaluatedKey' in result:
                result = self.table.scan(
                    ExclusiveStartKey=result['LastEvaluatedKey']
                )
                items.extend(result.get('Items', []))
            
            representatives = [Representative(**item).dict() for item in items]
            response.body.data = representatives
            
        except ClientError as e:
            self.logger.error(f"Error listing representatives: {e}")
            response.add_boto_error(e)
        
        return response

    def update(self, representative: Representative) -> Response:
        """Update an existing representative"""
        response = Response()
        item = representative.dict()
        
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=Attr("id").eq(representative.id)
            )
            response.body.data = [representative.dict()]
        except ClientError as e:
            self.logger.error(f"Error updating representative: {e}")
            response.add_boto_error(e)
        
        return response

    def delete(self, rep_id: str) -> Response:
        """Delete a representative"""
        response = Response()
        
        try:
            result = self.table.delete_item(
                Key={'id': rep_id},
                ConditionExpression=Attr("id").eq(rep_id),
                ReturnValues="ALL_OLD"
            )
            
            attr = result.get("Attributes")
            if attr:
                response.body.data = [Representative(**attr).dict()]
            
        except ClientError as e:
            self.logger.error(f"Error deleting representative: {e}")
            response.add_boto_error(e)
        
        return response
```

### Step 6: Implement Lambda Handler

Create `backend/src/handlers/api.py`:

```python
"""
Main API Lambda handler with routing
"""
import os
import json
from typing import Dict, Any
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import parse

from models.domain import Representative
from models.store import RepresentativeStore
from models.base import Response, APIError


# Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
TABLE_NAME = os.environ.get("DDB_TABLE_NAME", "representatives")

logger = Logger(service="represent-api", level=LOG_LEVEL)
store = None


@logger.inject_lambda_context(log_event=True)
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Main Lambda handler for API Gateway events
    Routes requests to appropriate CRUD operations
    """
    global store
    
    # Initialize store connection
    if store is None:
        store = RepresentativeStore(TABLE_NAME)
    
    # Parse API Gateway event
    api_event: APIGatewayProxyEventV2 = APIGatewayProxyEventV2(event)
    http_method = api_event.request_context.http.method
    path = api_event.raw_path
    
    response = Response()
    
    try:
        # Route based on path and method
        if '/representatives' in path:
            response = route_representatives(api_event, http_method, store)
        else:
            error = APIError(
                status=404,
                title="Not Found",
                detail=f"Path {path} not found"
            )
            response.add_error(error)
    
    except Exception as e:
        logger.exception("Unhandled error in handler")
        error = APIError(
            status=500,
            title="Internal Server Error",
            detail=str(e)
        )
        response.add_error(error)
    
    return response.dump()


def route_representatives(
    event: APIGatewayProxyEventV2,
    method: str,
    store: RepresentativeStore
) -> Response:
    """Route requests for /representatives endpoint"""
    
    response = Response()
    
    # Extract ID from path if present
    path_parts = event.raw_path.strip('/').split('/')
    rep_id = path_parts[-1] if len(path_parts) > 1 and path_parts[-1] != 'representatives' else None
    
    try:
        if method == 'POST':
            # Create new representative
            body = json.loads(event.body) if event.body else {}
            representative = parse(event=body, model=Representative)
            response = store.create(representative)
            
        elif method == 'GET':
            if rep_id:
                # Get single representative
                response = store.get(rep_id)
            else:
                # List all representatives
                response = store.list_all()
                
        elif method == 'PUT' or method == 'PATCH':
            # Update representative
            body = json.loads(event.body) if event.body else {}
            if rep_id:
                body['id'] = rep_id
            representative = parse(event=body, model=Representative)
            response = store.update(representative)
            
        elif method == 'DELETE':
            if rep_id:
                # Delete representative
                response = store.delete(rep_id)
            else:
                error = APIError(
                    status=400,
                    title="Bad Request",
                    detail="ID required for DELETE operation"
                )
                response.add_error(error)
        else:
            error = APIError(
                status=405,
                title="Method Not Allowed",
                detail=f"Method {method} not supported"
            )
            response.add_error(error)
    
    except Exception as e:
        logger.exception(f"Error in route_representatives: {e}")
        error = APIError(
            status=500,
            title="Internal Server Error",
            detail=str(e)
        )
        response.add_error(error)
    
    return response
```

### Step 7: Create Infrastructure Code

Create `infrastructure/app.py` (CDK entry point):

```python
#!/usr/bin/env python3
"""
CDK App for Represent App Infrastructure
"""
import os
from aws_cdk import core
from stacks.backend_stack import BackendStack

app = core.App()

# Get environment configuration
env_name = os.getenv('ENVIRONMENT', 'dev')
aws_account = os.getenv('CDK_DEFAULT_ACCOUNT')
aws_region = os.getenv('CDK_DEFAULT_REGION', 'us-east-1')

# Create stack
BackendStack(
    app,
    f"RepresentApp-{env_name}",
    env=core.Environment(account=aws_account, region=aws_region),
    env_name=env_name
)

app.synth()
```

Create `infrastructure/stacks/backend_stack.py`:

```python
"""
Backend infrastructure stack
"""
from aws_cdk import (
    core,
    aws_dynamodb as ddb,
    aws_lambda,
    aws_apigatewayv2 as apigw2,
    aws_apigatewayv2_integrations as apigw2_int,
    aws_logs
)
import os


class BackendStack(core.Stack):
    """Infrastructure for Represent App Backend"""
    
    def __init__(self, scope: core.Construct, stack_id: str, env_name: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        
        # DynamoDB Table
        table = ddb.Table(
            self,
            f"{stack_id}-RepresentativesTable",
            partition_key=ddb.Attribute(
                name='id',
                type=ddb.AttributeType.STRING
            ),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY if env_name == 'dev' else core.RemovalPolicy.RETAIN
        )
        
        # Lambda Function
        api_lambda = aws_lambda.Function(
            self,
            f"{stack_id}-ApiHandler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="handlers.api.handler",
            code=aws_lambda.Code.from_asset("backend/src"),
            timeout=core.Duration.seconds(30),
            environment={
                "DDB_TABLE_NAME": table.table_name,
                "LOG_LEVEL": "INFO",
                "POWERTOOLS_SERVICE_NAME": "represent-api"
            }
        )
        
        # Grant Lambda permissions to DynamoDB
        table.grant_read_write_data(api_lambda)
        
        # HTTP API Gateway
        http_api = apigw2.HttpApi(
            self,
            f"{stack_id}-HttpApi",
            create_default_stage=True,
            cors_preflight=apigw2.CorsPreflightOptions(
                allow_methods=[apigw2.CorsHttpMethod.ANY],
                allow_origins=["*"],  # Configure appropriately for production
                allow_headers=["*"]
            )
        )
        
        # Lambda Integration
        integration = apigw2_int.HttpLambdaIntegration(
            f"{stack_id}-Integration",
            api_lambda
        )
        
        # Add routes
        http_api.add_routes(
            path="/api/{proxy+}",
            methods=[
                apigw2.HttpMethod.GET,
                apigw2.HttpMethod.POST,
                apigw2.HttpMethod.PUT,
                apigw2.HttpMethod.PATCH,
                apigw2.HttpMethod.DELETE
            ],
            integration=integration
        )
        
        # Outputs
        core.CfnOutput(
            self,
            "ApiUrl",
            value=http_api.url,
            description="HTTP API Gateway URL"
        )
        
        core.CfnOutput(
            self,
            "TableName",
            value=table.table_name,
            description="DynamoDB Table Name"
        )
```

### Step 8: Create Tests

Create `backend/tests/unit/test_api_handler.py`:

```python
"""
Unit tests for API handler
"""
import json
import pytest
from moto import mock_dynamodb
import boto3
from handlers.api import handler
from models.domain import Representative


@mock_dynamodb
def test_create_representative():
    """Test creating a representative"""
    # Setup mock DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='representatives',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Create test event
    event = {
        'version': '2.0',
        'routeKey': 'POST /api/representatives',
        'rawPath': '/api/representatives',
        'requestContext': {
            'http': {
                'method': 'POST'
            }
        },
        'body': json.dumps({
            'name': 'John Doe',
            'position': 'Senator',
            'state': 'CA',
            'party': 'Independent'
        })
    }
    
    # Call handler
    response = handler(event, None)
    
    # Assertions
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'data' in body
    assert len(body['data']) == 1
    assert body['data'][0]['name'] == 'John Doe'


# Add more tests...
```

### Step 9: Configuration Files

Create `.env.example`:

```bash
# Environment
ENVIRONMENT=dev
AWS_REGION=us-east-1

# DynamoDB
DDB_TABLE_NAME=representatives

# Lambda
LOG_LEVEL=INFO
POWERTOOLS_SERVICE_NAME=represent-api

# CDK
CDK_DEFAULT_ACCOUNT=your-account-id
CDK_DEFAULT_REGION=us-east-1
```

Create `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=html --cov-report=term"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/test_*"]
```

## Phase 3: Deployment Instructions

### Prerequisites
```bash
# Install AWS CDK
npm install -g aws-cdk

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Configure AWS credentials
aws configure
```

### Deploy
```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy stack
cd infrastructure
cdk deploy
```

### Local Testing
```bash
# Run tests
cd backend
pytest

# Test with SAM CLI
sam local start-api
```

## Next Steps

1. Customize domain models for your specific use case
2. Add authentication/authorization
3. Implement additional API endpoints
4. Add CI/CD pipeline
5. Configure monitoring and alarms
6. Add API documentation (OpenAPI/Swagger)
7. Implement rate limiting
8. Add caching layer if needed

## Resources

- [AWS Lambda Powertools Documentation](https://awslabs.github.io/aws-lambda-powertools-python/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [API Gateway V2 Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/)
