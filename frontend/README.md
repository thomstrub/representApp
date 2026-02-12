# Represent App - Frontend

React + TypeScript frontend for finding and contacting political representatives.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Material UI (MUI)
- **Form Management**: React Hook Form + Zod validation
- **Testing**: Vitest + React Testing Library
- **HTTP Client**: Native Fetch API

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Configuration

The app uses environment variables for API configuration:

- **Development**: `.env` (points to localhost)
- **Production**: `.env.production` (points to AWS backend)

```bash
# Copy example file and customize
cp .env.example .env
```

## Testing Backend Integration

### Automated Tests

```bash
# Run API compatibility tests
npm test -- api-compatibility.test.ts

# Run all tests
npm test
```

### Manual API Connection Test

```bash
# Test connectivity to production backend
node scripts/test-api-connection.js
```

This script validates:
- ✅ API endpoint is reachable
- ✅ Response structure matches TypeScript types
- ✅ All required fields are present
- ✅ Data types are correct

## Project Structure

```
src/
├── components/         # React components
│   ├── AddressForm.tsx
│   ├── RepresentativeCard.tsx
│   ├── ResultsDisplay.tsx
│   └── LoadingIndicator.tsx
├── hooks/             # Custom React hooks
│   └── useRepresentatives.ts
├── types/             # TypeScript type definitions
│   ├── api.ts         # API response types (nested structure)
│   ├── representative.ts
│   ├── form.ts
│   └── state.ts
├── utils/             # Utility functions
│   └── errors.ts      # Error handling utilities
├── pages/             # Page components
│   └── HomePage.tsx
└── main.tsx           # App entry point

tests/
├── unit/              # Component unit tests
└── integration/       # Integration tests
```

## API Response Structure

The backend API returns representatives pre-grouped by government level with enhanced metadata:

```typescript
interface ApiSuccessResponse {
  representatives: {
    federal: Representative[];
    state: Representative[];
    local: Representative[];
  };
  metadata: {
    address: string;              // Resolved address
    coordinates?: {               // Geographic coordinates
      latitude: number;
      longitude: number;
    };
    total_count: number;          // Total representatives found
    government_levels: string[];  // Levels with results
    response_time_ms?: number;    // Backend processing time
  };
  warnings?: string[];            // Data limitation messages
}
```

**Key Features**:
- Representatives arrive pre-grouped (federal/state/local) - no client-side grouping needed
- Metadata provides resolved address and total counts for display
- Optional warnings array when data is incomplete
- Coordinates support future map-based features

## Architecture

### API Integration

The frontend connects to the backend API via the `useRepresentatives` hook:

```typescript
const { appState, fetchByAddress, clearResults } = useRepresentatives();

// Fetch representatives
await fetchByAddress("1301 4th Ave Seattle WA 98101");

// appState contains: { status, data, message }
```

### TypeScript Types

All API responses are strongly typed. See [src/types/api.ts](src/types/api.ts) for the complete API contract.

### State Management

Simple state management using React hooks:
- `useState` for local component state
- Custom `useRepresentatives` hook for API state
- No Redux or complex state libraries needed for MVP

## Development Guidelines

- Follow TDD approach (write tests first)
- All components must have unit tests
- Integration tests for critical user flows
- Maintain 100% test coverage for new features
- Use Material UI components consistently
- Follow TypeScript strict mode

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
## Production Deployment

### Build for Production

```bash
# Create production build
npm run build

# Preview production build locally
npm run preview
```

The build outputs to `dist/` directory with optimized assets:
- Minified JavaScript bundles
- Optimized CSS
- Static assets with content-based hashing

### Environment Configuration

Production builds require the API endpoint configuration:

```bash
# Create production environment file
cat > .env.production << EOF
VITE_API_BASE_URL=https://pktpja4zxd.execute-api.us-west-1.amazonaws.com
EOF

# Rebuild with production config
npm run build
```

### Deployed Environment

**Production URL**: https://d2x31oul4x7uo0.cloudfront.net

The application is deployed on AWS using:
- **S3**: Static file hosting
- **CloudFront**: Global CDN distribution
- **API Gateway**: Backend API integration

CORS is configured to allow the CloudFront origin for API requests.

### Deployment Process

Automated deployment via AWS CDK (see `infrastructure/` directory):

```bash
cd ../infrastructure

# Deploy frontend stack
cdk deploy RepresentAppFrontend-dev

# Get deployment URLs
cat frontend-outputs.json
```

The CDK stack will:
1. Build the frontend application
2. Upload assets to S3 bucket
3. Create CloudFront distribution
4. Configure caching policies
5. Output the CloudFront URL

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
