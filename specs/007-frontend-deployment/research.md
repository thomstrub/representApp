# Research: Frontend Deployment

**Feature**: 007-frontend-deployment  
**Date**: 2026-02-11  
**Researcher**: AI Assistant

## Research Questions

### Q1: What's the best practice for deploying React SPAs to AWS?

**Answer**: S3 + CloudFront is the industry standard for React SPA deployment on AWS.

**Key Findings**:
- S3 provides static file hosting with high availability
- CloudFront CDN reduces latency with global edge locations
- Serverless architecture (no servers to manage)
- Cost-effective: ~$0.01-0.05/month for low-medium traffic
- Supports SPA routing via CloudFront error page configuration

**Sources**:
- AWS Documentation: Static Website Hosting
- React deployment guides
- Existing project infrastructure (backend uses CDK)

### Q2: How to handle SPA routing with CloudFront?

**Answer**: Configure CloudFront to route 404 errors to index.html

**Implementation**:
```python
# CloudFront distribution error response configuration
error_responses=[
    cloudfront.CfnDistribution.CustomErrorResponseProperty(
        error_code=404,
        response_code=200,
        response_page_path="/index.html"
    )
]
```

**Rationale**:
- React Router uses client-side routing
- Direct URLs (e.g., /address) don't exist as files in S3
- CloudFront returns index.html for all routes
- React Router handles routing on client-side

### Q3: How to manage environment variables in Vite builds?

**Answer**: Use .env files with VITE_ prefix

**Implementation**:
```bash
# .env.production
VITE_API_BASE_URL=https://api.example.com
```

**Access in code**:
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

**Build-time substitution**: Vite replaces import.meta.env.* at build time

### Q4: What CORS configuration is needed?

**Answer**: API Gateway must allow CloudFront origin

**Required Headers**:
- `Access-Control-Allow-Origin`: CloudFront URL
- `Access-Control-Allow-Methods`: GET, POST, OPTIONS
- `Access-Control-Allow-Headers`: Content-Type

**CDK Implementation**:
```python
# In backend API Gateway configuration
cors=apigatewayv2.CorsPreflightOptions(
    allow_origins=["https://d123456.cloudfront.net"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)
```

## Architecture Decisions

### AWS CDK for Infrastructure

**Decision**: Use AWS CDK Python to define frontend infrastructure

**Pros**:
- Consistent with backend stack (feature 003)
- Version controlled infrastructure
- Type-safe infrastructure definitions
- Easy integration with existing CDK app

**Cons**:
- Learning curve for team unfamiliar with CDK
- Requires CDK bootstrap

**Alternatives Considered**:
- Terraform: Different tooling from backend
- Manual AWS Console: Not repeatable, no version control
- AWS Amplify: Additional abstraction layer, less control

### S3 Bucket Policies

**Public Read Access Required**:
```python
s3.Bucket(
    self, "FrontendBucket",
    website_index_document="index.html",
    public_read_access=True,  # Required for CloudFront
    block_public_access=s3.BlockPublicAccess(
        block_public_policy=False
    )
)
```

**Security Note**: Only static assets exposed, no sensitive data

## Performance Considerations

### CloudFront Caching Strategy

**Static Assets** (JS, CSS, images):
- Cache for 1 year
- Use content-based hashing (Vite default)
- Invalidate on deployment

**Index.html**:
- No cache or short TTL
- Ensures users get latest app version

**Implementation**:
```python
# Cache behavior for static assets
cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED

# Cache behavior for index.html
cache_policy=cloudfront.CachePolicy(
    self, "IndexCachePolicy",
    max_ttl=Duration.seconds(0),
    min_ttl=Duration.seconds(0)
)
```

### Build Optimization

**Vite Production Build**:
- Code splitting (automatic)
- Minification
- Tree shaking
- Asset optimization

**Bundle Size Monitoring**:
- Use `npm run build -- --analyze` to inspect bundle
- Material UI should be tree-shaken

## Deployment Workflow

### Initial Deployment

1. Build frontend: `npm run build`
2. Deploy CDK stack: `cdk deploy FrontendStack`
3. CDK handles S3 upload automatically
4. Wait for CloudFront propagation (15-20 min)

### Subsequent Deployments

1. Update code
2. Build: `npm run build`
3. Deploy: `cdk deploy FrontendStack`
4. Invalidate CloudFront cache: `aws cloudfront create-invalidation`

## Cost Estimation

### Expected Monthly Costs (Low Traffic)

- S3 Storage: 100MB @ $0.023/GB = $0.002
- S3 Requests: 10,000 GET @ $0.0004/1000 = $0.004
- CloudFront Data Transfer: 10GB @ $0.085/GB = $0.85
- CloudFront Requests: 10,000 @ $0.0075/10,000 = $0.0075

**Total**: ~$0.86/month (low traffic estimation)

**Scaling**: Costs increase linearly with traffic, but remain low for typical use

## Security Considerations

### S3 Bucket Security

- Block direct S3 access (force CloudFront)
- Use Origin Access Identity (OAI)
- No sensitive data in frontend bundle

### API Security

- CORS restricts API access to known origins
- Backend API handles authentication/authorization
- Frontend only handles presentation logic

### Environment Variables

- Never commit .env.production with real URLs
- Use .env.production.template for reference
- Document environment variable setup

## Monitoring & Debugging

### CloudFront Logs

Enable CloudFront access logs to S3 bucket:
- Track request patterns
- Debug routing issues
- Monitor error rates

### CloudWatch Metrics

- CloudFront requests, errors, data transfer
- S3 bucket metrics
- Set up alarms for error rates

## References

- [AWS CDK CloudFront Documentation](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront.html)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [React SPA Deployment Patterns](https://create-react-app.dev/docs/deployment/)
- Project: features/003-address-lookup (backend infrastructure patterns)
