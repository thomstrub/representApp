# Quickstart: Frontend Deployment

**Feature**: 007-frontend-deployment  
**Last Updated**: 2026-02-11

## Prerequisites

- AWS CLI configured with credentials
- AWS CDK bootstrapped in target account/region
- Backend API deployed (feature 003-address-lookup)
- Frontend application built and tested (feature 004-address-ui)
- Node.js 18+ and npm installed
- Python 3.9+ installed

## Quick Start (30 minutes)

### Step 1: Pre-Deployment Validation (5 min)

```bash
# Navigate to frontend directory
cd frontend/

# Run tests
npm test

# Run linter
npm run lint

# Generate coverage report
npm run test:coverage

# Verify >80% coverage in output

# Test production build
npm run build

# Verify dist/ directory created
ls -la dist/
```

**Expected Output**:
- All tests passing
- No lint errors
- Coverage >80%
- dist/ directory with index.html, assets/

### Step 2: Get Backend API URL (2 min)

```bash
# Navigate to infrastructure directory
cd ../infrastructure/

# Get API Gateway URL from backend stack
cdk deploy BackendStack --outputs-file outputs.json

# Extract API URL
cat outputs.json | grep -i "apigateway"
```

**Expected Output**:
```json
{
  "BackendStack": {
    "ApiGatewayUrl": "https://abc123.execute-api.us-west-2.amazonaws.com"
  }
}
```

### Step 3: Configure Frontend Environment (2 min)

```bash
# Navigate back to frontend
cd ../frontend/

# Create production environment file
cat > .env.production << EOF
VITE_API_BASE_URL=https://abc123.execute-api.us-west-2.amazonaws.com
EOF

# Verify environment file
cat .env.production

# Rebuild with production env
npm run build
```

**Expected Output**:
- .env.production created
- Build completes without errors

### Step 4: Create Frontend CDK Stack (10 min)

```bash
# Navigate to infrastructure
cd ../infrastructure/stacks/

# Create frontend_stack.py (see implementation below)

# Update app.py to include FrontendStack
cd ..
# Edit app.py (add import and instantiation)
```

**Implementation**: See [Frontend Stack Code](#frontend-stack-code) below

### Step 5: Deploy Frontend Infrastructure (10 min)

```bash
# From infrastructure/ directory

# Synthesize CDK stack (verify template)
cdk synth FrontendStack

# Deploy frontend stack
cdk deploy FrontendStack

# Answer 'y' to deployment confirmation
```

**Expected Output**:
```
FrontendStack: deploying...
FrontendStack: creating CloudFormation changeset...
...
✅ FrontendStack

Outputs:
FrontendStack.CloudFrontUrl = https://d1234567890.cloudfront.net
FrontendStack.S3BucketName = frontendstack-frontendbucket12345-abc123

Stack ARN:
arn:aws:cloudformation:us-west-2:123456789012:stack/FrontendStack/...
```

### Step 6: Configure CORS (5 min)

```bash
# Update backend stack to include CloudFront origin in CORS

# Edit infrastructure/stacks/backend_stack.py
# Add CloudFront URL to CORS allow_origins

# Redeploy backend
cdk deploy BackendStack
```

**CORS Configuration**:
```python
cors=apigatewayv2.CorsPreflightOptions(
    allow_origins=[
        "http://localhost:5173",  # Development
        "https://d1234567890.cloudfront.net"  # Production
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)
```

### Step 7: Validate Deployment (5 min)

```bash
# Wait for CloudFront propagation (15-20 minutes)
# Check CloudFront distribution status in AWS Console

# Once deployed, test the frontend
open https://d1234567890.cloudfront.net

# Test address lookup:
# 1. Enter: "1600 Pennsylvania Avenue NW, Washington, DC 20500"
# 2. Click "Find My Representatives"
# 3. Verify results display

# Check browser console (F12) - should be no errors
```

**Expected Behavior**:
- Frontend loads without errors
- Address form accepts input
- API request returns representatives
- Results display in cards

## Frontend Stack Code

Create `infrastructure/stacks/frontend_stack.py`:

```python
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,
    CfnOutput,
    Duration
)
from constructs import Construct
import os

class FrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for frontend hosting
        frontend_bucket = s3.Bucket(
            self, "FrontendBucket",
            website_index_document="index.html",
            website_error_document="index.html",  # SPA routing
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_policy=False,
                block_public_acls=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # CloudFront distribution
        distribution = cloudfront.Distribution(
            self, "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(frontend_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0)
                )
            ]
        )

        # Deploy frontend build to S3
        frontend_build_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "..", 
            "frontend", 
            "dist"
        )

        s3deploy.BucketDeployment(
            self, "DeployFrontend",
            sources=[s3deploy.Source.asset(frontend_build_path)],
            destination_bucket=frontend_bucket,
            distribution=distribution,
            distribution_paths=["/*"]
        )

        # Outputs
        CfnOutput(
            self, "CloudFrontUrl",
            value=f"https://{distribution.distribution_domain_name}",
            description="Frontend CloudFront URL"
        )

        CfnOutput(
            self, "S3BucketName",
            value=frontend_bucket.bucket_name,
            description="Frontend S3 bucket name"
        )
```

Update `infrastructure/app.py`:

```python
#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.backend_stack import BackendStack
from stacks.frontend_stack import FrontendStack  # ADD THIS

app = cdk.App()

# Backend stack (existing)
backend_stack = BackendStack(
    app, "BackendStack",
    env=cdk.Environment(
        account="123456789012",
        region="us-west-2"
    )
)

# Frontend stack (NEW)
frontend_stack = FrontendStack(
    app, "FrontendStack",
    env=cdk.Environment(
        account="123456789012",
        region="us-west-2"
    )
)

app.synth()
```

## Troubleshooting

### Issue: CloudFront returns 403 Forbidden

**Cause**: S3 bucket not publicly accessible

**Solution**:
```bash
# Verify bucket policy allows public read
aws s3api get-bucket-policy --bucket <bucket-name>

# If missing, update frontend_stack.py to set public_read_access=True
# Redeploy: cdk deploy FrontendStack
```

### Issue: API requests fail with CORS errors

**Cause**: Backend CORS not configured for CloudFront origin

**Solution**:
```bash
# Update backend_stack.py with CloudFront URL in allow_origins
# Redeploy backend: cdk deploy BackendStack

# Verify CORS headers in browser network tab:
# Response should include: Access-Control-Allow-Origin: https://d123.cloudfront.net
```

### Issue: Direct URLs (e.g., /address) return 404

**Cause**: CloudFront not configured for SPA routing

**Solution**:
```python
# Add error response to CloudFront distribution in frontend_stack.py
error_responses=[
    cloudfront.ErrorResponse(
        http_status=404,
        response_http_status=200,
        response_page_path="/index.html"
    )
]
```

### Issue: Environment variables not working

**Cause**: Build doesn't include .env.production

**Solution**:
```bash
# Verify .env.production exists in frontend/
cat frontend/.env.production

# Rebuild frontend
cd frontend && npm run build

# Redeploy: cd ../infrastructure && cdk deploy FrontendStack
```

### Issue: Changes not reflected after deployment

**Cause**: CloudFront cache

**Solution**:
```bash
# Invalidate CloudFront distribution
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"

# Wait 2-5 minutes for invalidation to complete
```

## Deployment Checklist

- [ ] All frontend tests passing
- [ ] Lint errors resolved
- [ ] Test coverage >80%
- [ ] Production build tested locally
- [ ] Backend API URL obtained
- [ ] .env.production created with correct API URL
- [ ] FrontendStack CDK code created
- [ ] CDK synth successful
- [ ] FrontendStack deployed
- [ ] CloudFront URL recorded
- [ ] CORS configured on backend
- [ ] Backend stack redeployed
- [ ] Frontend accessible at CloudFront URL
- [ ] Address lookup flow tested
- [ ] No browser console errors
- [ ] Tested on mobile device
- [ ] Documentation updated

## Next Steps

After successful deployment:

1. **Custom Domain** (optional): Add Route53 + ACM certificate
2. **CI/CD Pipeline**: Automate deployment on git push
3. **Monitoring**: Set up CloudWatch alarms for errors
4. **Performance**: Add CloudFront logging and Web Vitals tracking
5. **Staging Environment**: Create separate staging stack

## References

- [AWS CDK CloudFront Patterns](https://docs.aws.amazon.com/cdk/v2/guide/cloudfront.html)
- [Vite Build Documentation](https://vitejs.dev/guide/build.html)
- Feature 003: Backend API implementation
- Feature 004: Frontend UI implementation
