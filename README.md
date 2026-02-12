# Represent App

A full-stack serverless application for finding and contacting political representatives at all levels of government.

## 🚀 Live Application

**Production**: https://d2x31oul4x7uo0.cloudfront.net

Try it now - look up your representatives by entering your address!

## 📋 Overview

Represent App bridges the gap between political infrastructure and constituents' day-to-day lives. The application helps citizens find, contact, and track their local, state, and federal representatives using a modern cloud-native architecture.

### Key Features

- 🔍 **Address-based Lookup**: Find representatives by entering any U.S. address
- 🏛️ **Multi-level Coverage**: Federal, state, and local officials
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- ⚡ **Real-time Data**: Integrated with Google Civic Information and OpenStates APIs
- 🌍 **Geographic Discovery**: Geocoding and coordinate-based representative lookup

## 🏗️ Architecture

### Technology Stack

**Frontend**:
- React 18 + TypeScript
- Material UI for components
- Vite for build tooling
- Vitest + React Testing Library

**Backend**:
- Python 3.9 Lambda functions
- AWS Lambda Powertools (structured logging, tracing)
- API Gateway HTTP API
- DynamoDB for data caching

**Infrastructure**:
- AWS CDK (Python) for IaC
- S3 + CloudFront for frontend hosting
- Parameter Store for API keys
- CloudWatch for monitoring

**External APIs**:
- Google Maps Geocoding API
- OpenStates Geo API
- Google Civic Information API (future)

### Deployment Architecture

```
┌─────────────┐
│   Browser   │
└─────┬───────┘
      │
      ▼
┌──────────────────┐
│   CloudFront     │ ← https://d2x31oul4x7uo0.cloudfront.net
│   (CDN + SSL)    │
└─────┬────────────┘
      │
      ▼
┌──────────────────┐      ┌────────────────┐
│   S3 Bucket      │      │  API Gateway   │ ← https://pktpja4zxd...
│ (Static Assets)  │      │  (HTTP API)    │
└──────────────────┘      └───────┬────────┘
                                  │
                                  ▼
                          ┌───────────────┐
                          │    Lambda     │
                          │   Handler     │
                          └───┬────┬──────┘
                              │    │
                    ┌─────────┘    └──────────┐
                    ▼                         ▼
            ┌──────────────┐         ┌──────────────┐
            │   DynamoDB   │         │    External  │
            │   (Cache)    │         │     APIs     │
            └──────────────┘         └──────────────┘
```

## 🚦 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- AWS CLI configured
- AWS CDK bootstrapped

### Development Setup

```bash
# Clone repository
git clone https://github.com/thomstrub/representApp.git
cd representApp

# Install frontend dependencies
cd frontend
npm install
npm run dev

# Install backend dependencies (separate terminal)
cd backend
pip install -r requirements.txt
pytest

# Deploy infrastructure (optional for local dev)
cd infrastructure
pip install -r requirements.txt
cdk deploy --all
```

### Environment Variables

**Frontend** (`.env`):
```bash
VITE_API_BASE_URL=http://localhost:3000  # Local development
# Or use production API for testing
VITE_API_BASE_URL=https://pktpja4zxd.execute-api.us-west-1.amazonaws.com
```

**Backend** (AWS Parameter Store):
```bash
aws ssm put-parameter --name "/represent-app/google-maps-api-key" \
  --value "YOUR_KEY" --type "SecureString"

aws ssm put-parameter --name "/represent-app/openstates-api-key" \
  --value "YOUR_KEY" --type "SecureString"
```

## 📦 Deployment

Full deployment guide: [docs/deployment-guide.md](docs/deployment-guide.md)

### Quick Deploy

```bash
cd infrastructure

# Deploy backend (API + Database)
cdk deploy RepresentApp-dev

# Deploy frontend (S3 + CloudFront)
cdk deploy RepresentAppFrontend-dev
```

**Result**: Frontend at CloudFront URL, backend at API Gateway endpoint

## 🧪 Testing

### Frontend Tests

```bash
cd frontend
npm test                 # Run all tests
npm run test:coverage    # Generate coverage report
npm run lint             # Check code style
```

### Backend Tests

```bash
cd backend
pytest                          # Run all tests
pytest --cov=src --cov-report=html  # Generate coverage report
pylint src/                     # Check code quality
```

## 📚 Documentation

- [Project Overview](docs/project-overview.md) - Architecture and design principles
- [Functional Requirements](docs/functional-requirements.md) - Feature specifications
- [Deployment Guide](docs/deployment-guide.md) - Production deployment process
- [Testing Guidelines](docs/testing-guidelines.md) - Testing standards
- [Coding Guidelines](docs/coding-guidelines.md) - Code style and conventions
- [UI Guidelines](docs/ui-guidelines.md) - Material UI standards

### Specification Directory

Feature development follows a structured process in `specs/`:

- `001-api-integration-research/` - Google Civic API research
- `003-address-lookup/` - Backend address lookup implementation
- `004-address-ui/` - Frontend UI components
- `005-geolocation-lookup/` - Geocoding integration
- `006-frontend-api-updates/` - Frontend API client
- `007-frontend-deployment/` - Production deployment

Each spec includes: `plan.md`, `tasks.md`, `research.md`, `quickstart.md`

## 🔐 Security

- ✅ API keys stored in Parameter Store (encrypted)
- ✅ CORS configured for specific origins only
- ✅ IAM roles with least-privilege access
- ✅ No sensitive data in version control
- ✅ CloudFront provides DDoS protection
- ✅ X-Ray tracing for security monitoring

## 📊 Monitoring

### CloudWatch Logs

- **Lambda**: `/aws/lambda/RepresentApp-dev-ApiHandler-*`
- **Structured logging** with AWS Lambda Powertools
- **X-Ray tracing** for distributed request tracking

### Metrics

```bash
# View Lambda logs (real-time)
aws logs tail /aws/lambda/RepresentApp-dev-ApiHandler --follow

# API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=RepresentApp-dev
```

## 💰 Cost Estimate

**Development Environment** (~$2-5 /month):
- S3: $0.01/month (static files)
- CloudFront: $0.01-0.05/month (low traffic)
- API Gateway: $1.00 per million requests
- Lambda: $0.20 per million requests
- DynamoDB: On-demand pricing (~$0-1/month)

**Production** scales with usage but remains cost-effective for moderate traffic.

## 🤝 Contributing

This is a learning project following TDD and cloud-native best practices. 

### Development Principles

1. **Test-Driven Development** - Write tests first
2. **Incremental Changes** - Small, testable modifications
3. **Infrastructure as Code** - All resources in CDK
4. **Documentation** - Keep docs up-to-date

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Google Civic Information API** - Representative data
- **OpenStates API** - State legislature data
- **AWS CDK** - Infrastructure as Code
- **Material UI** - React components
- **Vite** - Build tooling

## 📞 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using AWS, React, and Python**

