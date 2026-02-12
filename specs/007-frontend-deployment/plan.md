# Implementation Plan: Frontend Deployment

**Branch**: `007-frontend-deployment` | **Date**: 2026-02-11 | **Spec**: [spec.md](spec.md)

## Summary

Deploy the Represent App React frontend to AWS using S3 for static hosting and CloudFront for CDN distribution. Create CDK infrastructure stack, configure production build, establish CORS policies, and validate end-to-end functionality in production environment.

## Technical Context

**Language/Version**: Python 3.9 (CDK), TypeScript (frontend build)  
**Primary Dependencies**: AWS CDK, Vite (build tool), AWS S3, CloudFront  
**Storage**: S3 bucket for static assets  
**Testing**: Manual production validation, integration testing  
**Target Platform**: AWS Cloud (us-west-2 region)  
**Project Type**: Infrastructure + deployment  
**Performance Goals**: CloudFront <100ms TTFB, S3 static hosting, global CDN distribution  
**Constraints**: Use existing AWS account, leverage CDK patterns from backend stack, minimal cost  
**Scale/Scope**: Single S3 bucket, single CloudFront distribution, single environment (production)

## Constitution Check

| Principle | Compliance | Notes |
|-----------|------------|-------|
| **I. Test-Driven Development** | ✅ N/A | Deployment infrastructure - validated via deployment testing, not unit tests |
| **II. Testing Scope** | ✅ PASS | Manual validation testing of deployed frontend. No e2e frameworks. |
| **III. Code Quality Gates** | ✅ PASS | CDK stack follows project patterns. Deployment checklist ensures quality. |
| **IV. Incremental Development** | ✅ PASS | Phased: infrastructure → build → deploy → configure → validate |
| **V. Serverless Architecture** | ✅ PASS | S3 + CloudFront is serverless - no servers to manage, pay-per-use, auto-scaling |
| **VI. Accessible Information Design** | ✅ PASS | Deployment documentation in README, clear deployment steps |

## Architecture Decisions

### AD-001: S3 + CloudFront for Frontend Hosting

**Decision**: Use S3 for static file storage with CloudFront CDN distribution

**Rationale**:
- Serverless (no EC2 instances to manage)
- Cost-effective ($0.01-0.05/month for low traffic)
- Global CDN distribution via CloudFront
- Integrates with existing AWS CDK infrastructure
- Industry standard for React/SPA hosting

**Alternatives Considered**:
- Vercel/Netlify: Requires external service, less control
- EC2 + Nginx: Over-engineered, higher cost, maintenance burden

### AD-002: CDK for Infrastructure Management

**Decision**: Extend existing CDK project with FrontendStack

**Rationale**:
- Consistent with backend infrastructure (feature 003)
- Version controlled infrastructure
- Replicable across environments
- Python CDK already configured in project

### AD-003: Single Production Environment

**Decision**: Deploy single production environment initially

**Rationale**:
- Simplest deployment path
- Staging environment deferred to future iteration
- Manual validation sufficient for MVP

## File Structure

```
infrastructure/
  stacks/
    frontend_stack.py          # NEW: S3 + CloudFront CDK stack
    
frontend/
  .env.production              # NEW: Production API URL
  dist/                        # Build output (gitignored)
  
README.md                      # UPDATED: Deployment documentation
frontend/README.md             # UPDATED: Build and deploy commands
```

## Implementation Phases

### Phase 1: Infrastructure Setup
- Create FrontendStack with S3 bucket
- Configure CloudFront distribution
- Set up bucket policies and CORS

### Phase 2: Build Configuration
- Create .env.production with API URL
- Test production build locally
- Verify dist/ output

### Phase 3: Deployment
- Deploy CDK stack
- Upload frontend assets to S3
- Configure CORS on backend API Gateway

### Phase 4: Validation
- Test from multiple devices
- Validate quickstart guide
- Document deployment process

## Key Components

### FrontendStack (infrastructure/stacks/frontend_stack.py)

```python
- S3 Bucket (website hosting enabled)
- CloudFront Distribution
  - Origin: S3 bucket
  - Default root object: index.html
  - Error pages: SPA routing support
  - Caching behavior
- Bucket Deployment (CDK construct)
```

### Environment Configuration

```bash
# .env (development)
VITE_API_BASE_URL=http://localhost:3000

# .env.production (production) 
VITE_API_BASE_URL=https://<api-gateway-id>.execute-api.us-west-2.amazonaws.com
```

## Dependencies

- AWS CDK bootstrapped in target account/region
- Backend API deployed (feature 003)
- Frontend build tested (feature 004)
- API Gateway URL available from backend stack outputs

## Risk Mitigation

- **Risk**: CloudFront propagation delay (15-20 minutes)
  - **Mitigation**: Document expected delay, use invalidation for updates
  
- **Risk**: CORS misconfiguration blocking API calls
  - **Mitigation**: Test CORS locally first, systematic troubleshooting

- **Risk**: Environment variable mismatch
  - **Mitigation**: Explicit validation step, checklist verification

## Success Metrics

- Frontend accessible at CloudFront URL
- Address lookup completes successfully
- API requests return 200 OK
- No browser console errors
- All quickstart steps validated
