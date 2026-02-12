# Deployment Guide

**Last Updated**: February 11, 2026  
**Feature**: 007-frontend-deployment

## Overview

This guide describes the complete deployment process for the Represent App, including both backend API and frontend SPA components.

## Architecture

### Production Environment

- **Frontend**: React SPA hosted on S3 + CloudFront CDN
- **Backend**: Python Lambda functions behind API Gateway
- **Database**: DynamoDB for representative data caching
- **Infrastructure**: AWS CDK for Infrastructure as Code

### URLs

- **Frontend (Production)**: https://d2x31oul4x7uo0.cloudfront.net
- **Backend API**: https://pktpja4zxd.execute-api.us-west-1.amazonaws.com
- **Region**: us-west-1 (N. California)

## Prerequisites

1. **AWS CLI** configured with credentials
2. **AWS CDK** bootstrapped in target account/region:
   ```bash
   cdk bootstrap aws://ACCOUNT-NUMBER/us-west-1
   ```
3. **Node.js 18+** and npm
4. **Python 3.9+** and pip
5. **API Keys** stored in AWS Parameter Store:
   - `/represent-app/google-maps-api-key`
   - `/represent-app/openstates-api-key`

## Initial Setup

### 1. Install Dependencies

```bash
# Backend Python dependencies
cd backend
pip install -r requirements.txt

# Frontend Node dependencies
cd ../frontend
npm install

# Infrastructure CDK dependencies
cd ../infrastructure
pip install -r requirements.txt
```

### 2. Store API Keys

```bash
# Google Maps API Key
aws ssm put-parameter \
  --name "/represent-app/google-maps-api-key" \
  --value "YOUR_GOOGLE_MAPS_KEY" \
  --type "SecureString" \
  --overwrite

# OpenStates API Key
aws ssm put-parameter \
  --name "/represent-app/openstates-api-key" \
  --value "YOUR_OPENSTATES_KEY" \
  --type "SecureString" \
  --overwrite
```

## Backend Deployment

### Deploy Backend Stack

```bash
cd infrastructure

# Deploy backend resources (DynamoDB, Lambda, API Gateway)
cdk deploy RepresentApp-dev --require-approval never --outputs-file backend-outputs.json

# Extract API Gateway URL
cat backend-outputs.json
```

**Expected Output**:
```json
{
  "RepresentApp-dev": {
    "ApiUrl": "https://pktpja4zxd.execute-api.us-west-1.amazonaws.com/",
    "LambdaArn": "arn:aws:lambda:...",
    "TableName": "RepresentApp-dev-..."
  }
}
```

### Test Backend API

```bash
# Test with curl
curl "https://pktpja4zxd.execute-api.us-west-1.amazonaws.com/api/lookup/address?address=Seattle,WA"
```

**Expected**: JSON response with representatives data

## Frontend Deployment

### 1. Configure Environment

```bash
cd frontend

# Create production environment file with API URL
cat > .env.production << EOF
VITE_API_BASE_URL=https://pktpja4zxd.execute-api.us-west-1.amazonaws.com
EOF
```

### 2. Build Frontend

```bash
# Run pre-deployment validation
npm test
npm run lint
npm run build

# Verify dist/ directory created
ls -la dist/
```

### 3. Deploy Frontend Stack

```bash
cd ../infrastructure

# Deploy frontend resources (S3, CloudFront)
cdk deploy RepresentAppFrontend-dev --require-approval never --outputs-file frontend-outputs.json

# Get CloudFront URL
cat frontend-outputs.json
```

**Expected Output**:
```json
{
  "RepresentAppFrontend-dev": {
    "CloudFrontUrl": "https://d2x31oul4x7uo0.cloudfront.net",
    "S3BucketName": "representappfrontend-dev-..."
  }
}
```

### 4. Wait for CloudFront Propagation

CloudFront distributions take 15-20 minutes to fully propagate to all edge locations. The URL will be accessible sooner, but full global availability requires patience.

## CORS Configuration

CORS is configured in `infrastructure/stacks/backend_stack.py`:

```python
cors_preflight=apigw2.CorsPreflightOptions(
    allow_methods=[apigw2.CorsHttpMethod.ANY],
    allow_origins=[
        "http://localhost:5173",  # Local development
        "http://localhost:4173",  # Vite preview
        "https://d2x31oul4x7uo0.cloudfront.net"  # Production CloudFront
    ],
    allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"],
    allow_credentials=False,
    max_age=cdk.Duration.hours(1)
)
```

**To update CORS**:
1. Edit `backend_stack.py` allowed origins
2. Redeploy: `cdk deploy RepresentApp-dev`

## Verification

### Automated Tests

```bash
# Test CloudFront serves HTML
curl -I https://d2x31oul4x7uo0.cloudfront.net/

# Test API from CloudFront origin
curl -X GET "https://pktpja4zxd.execute-api.us-west-1.amazonaws.com/api/lookup/address?address=Seattle,WA" \
  -H "Origin: https://d2x31oul4x7uo0.cloudfront.net"

# Verify CORS headers
curl -I -X OPTIONS https://pktpja4zxd.execute-api.us-west-1.amazonaws.com/api/lookup/address \
  -H "Origin: https://d2x31oul4x7uo0.cloudfront.net" \
  -H "Access-Control-Request-Method: POST"
```

### Manual Browser Testing

1. Open https://d2x31oul4x7uo0.cloudfront.net in Chrome
2. Test address lookup: "1600 Pennsylvania Avenue NW, Washington, DC"
3. Verify representatives display correctly
4. Check browser console for errors
5. Test on mobile/tablet devices
6. Verify responsive design
7. Test error handling with invalid addresses

## Troubleshooting

### Issue: CloudFront returns 403 Forbidden

**Cause**: S3 bucket policy not allowing public read access

**Solution**:
```bash
# Verify bucket policy in CloudFormation
aws cloudformation describe-stack-resources \
  --stack-name RepresentAppFrontend-dev \
  --logical-resource-id FrontendBucket
```

### Issue: API returns CORS errors

**Cause**: CloudFront origin not in allowed origins list

**Solution**:
1. Check `backend_stack.py` CORS configuration
2. Ensure CloudFront URL is in `allow_origins` list
3. Redeploy backend: `cdk deploy RepresentApp-dev`

### Issue: Frontend shows old version

**Cause**: CloudFront cache or browser cache

**Solution**:
```bash
# Create CloudFront invalidation
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"

# Or force refresh in browser with Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows)
```

### Issue: CDK version mismatch error

**Error**: `Cloud assembly schema version mismatch`

**Solution**:
```bash
# Upgrade Python CDK library to match CLI
cd infrastructure
pip install --upgrade aws-cdk-lib

# Or upgrade CLI to match library
npm install -g aws-cdk@latest
```

### Issue: Lambda timeout on address lookup

**Cause**: Cold start or slow API calls to Google Maps/OpenStates

**Solution**:
- Check CloudWatch logs: `/aws/lambda/RepresentApp-dev-ApiHandler`
- Consider increasing Lambda timeout in `backend_stack.py`
- Add API response caching to DynamoDB

## Cost Optimization

### Current Costs (Estimated)

- **S3 Storage**: ~$0.01/month (small static files)
- **CloudFront**: ~$0.01-0.05/month (low traffic)
- **API Gateway**: $1.00 per million requests
- **Lambda**: $0.20 per million requests (400ms avg)
- **DynamoDB**: On-demand pricing (~$0-1/month)

**Total**: $1-5/month for development environment

### Optimization Tips

1. **Enable CloudFront caching** for static assets (already configured)
2. **Use DynamoDB caching** to reduce external API calls
3. **Delete old CloudWatch logs** after debugging
4. **Use Lambda reserved concurrency** to prevent unexpected costs

## Monitoring

### CloudWatch Dashboards

View logs in AWS Console:

- **Lambda Logs**: `/aws/lambda/RepresentApp-dev-ApiHandler-*`
- **API Gateway Logs**: Execution logs in API Gateway console
- **CloudFront Logs**: Access logs in S3 (if enabled)

### Useful CLI Commands

```bash
# View recent Lambda logs
aws logs tail /aws/lambda/RepresentApp-dev-ApiHandler --follow

# Get API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=RepresentApp-dev \
  --start-time 2026-02-11T00:00:00Z \
  --end-time 2026-02-12T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Check S3 bucket size
aws s3 ls s3://representappfrontend-dev-... --recursive --summarize
```

## Rollback Procedures

### Rollback Frontend

```bash
# Redeploy previous version from git
git checkout PREVIOUS_TAG
cd infrastructure
cdk deploy RepresentAppFrontend-dev
```

### Rollback Backend

```bash
# Use CloudFormation rollback
aws cloudformation rollback-stack --stack-name RepresentApp-dev

# Or redeploy specific git version
git checkout PREVIOUS_TAG
cdk deploy RepresentApp-dev
```

## Disaster Recovery

### Backup Strategy

- **DynamoDB**: Point-in-time recovery enabled (if configured)
- **Parameter Store**: API keys stored securely
- **Infrastructure**: All infrastructure defined in CDK code (version controlled)

### Recovery Process

1. Check git history for last working version
2. Redeploy infrastructure: `cdk deploy RepresentApp-dev`
3. Restore Parameter Store values if needed
4. Redeploy frontend: `cdk deploy RepresentAppFrontend-dev`

## CI/CD Integration (Future)

Recommended GitHub Actions workflow:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy Backend
        run: |
          cd infrastructure
          cdk deploy RepresentApp-dev --require-approval never
      - name: Deploy Frontend
        run: |
          cd infrastructure
          cdk deploy RepresentAppFrontend-dev --require-approval never
```

## Security Considerations

### API Keys

- ✅ Stored in Parameter Store (SecureString)
- ✅ Not committed to git
- ✅ IAM permissions restrict access to Lambda only

### CORS

- ✅ Restrictive origins (localhost + CloudFront only)
- ✅ Specific headers allowed
- ✅ No credentials required

### S3 Bucket

- ⚠️ Public read access (required for CloudFront)
- ✅ Only static assets exposed (no sensitive data)
- ✅ CloudFront provides DDoS protection

## Further Reading

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [CloudFront Developer Guide](https://docs.aws.amazon.com/cloudfront/)
- [API Gateway CORS Configuration](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
