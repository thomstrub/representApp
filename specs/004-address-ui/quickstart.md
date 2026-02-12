# Quickstart Guide: Address Lookup Frontend

**Date**: 2026-02-09  
**Purpose**: Setup instructions and quick reference for frontend development  
**Audience**: Frontend developers implementing React + TypeScript + Material UI application

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Development Workflow](#development-workflow)
4. [Component Quick Reference](#component-quick-reference)
5. [Testing Guide](#testing-guide)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

**Required Software**:
- Node.js 18+ and npm 9+
- Git
- Code editor (VS Code recommended)

**Required Knowledge**:
- React 18 (hooks: useState, useEffect)
- TypeScript basics
- Material UI components
- Jest + React Testing Library

**Backend Dependency**:
- Backend API from feature 003-address-lookup must be running
- API Gateway endpoint URL required

---

## Project Setup

### Step 1: Create Vite Project

```bash
# From repository root
npm create vite@latest frontend -- --template react-ts
cd frontend
```

**Verify Vite version**: Vite 5+ recommended

---

### Step 2: Install Dependencies

```bash
# UI Library (Material UI)
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material

# Form Handling & Validation
npm install react-hook-form @hookform/resolvers zod

# Testing (Dev Dependencies)
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom @vitest/ui

# Optional: ESLint + Prettier (Code Quality)
npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-react
```

**Total Install Time**: ~2-3 minutes on modern connection

---

### Step 3: Configure Environment Variables

Create `.env` file in `frontend/` directory:

```bash
# .env (Development)
VITE_API_BASE_URL=http://localhost:3000

# .env.production (Production)
# VITE_API_BASE_URL=https://api.representapp.example.com
```

**Important**: 
- Add `.env` to `.gitignore`
- Use `VITE_` prefix for all environment variables

---

### Step 4: Configure Vitest

Update `vite.config.ts`:

```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
  },
});
```

Create `src/setupTests.ts`:

```typescript
import '@testing-library/jest-dom';
```

---

### Step 5: Update package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint . --ext ts,tsx"
  }
}
```

---

### Step 6: Project Structure Setup

Create directory structure:

```bash
mkdir -p src/components src/pages src/hooks src/types src/utils src/tests/components src/tests/integration src/tests/utils
```

**Final Structure**:
```
frontend/
├── src/
│   ├── components/        # React components
│   ├── pages/            # Page components
│   ├── hooks/            # Custom hooks
│   ├── types/            # TypeScript types
│   ├── utils/            # Utility functions
│   ├── tests/            # Test files
│   ├── App.tsx           # Root component
│   ├── main.tsx          # Entry point
│   └── setupTests.ts     # Test setup
├── public/               # Static assets
├── .env                  # Environment variables (gitignored)
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

---

## Development Workflow

### TDD Cycle (Red-Green-Refactor)

**1. Write Test First** (Red):
```bash
# Create test file
touch src/tests/components/AddressForm.test.tsx

# Write failing test
npm test
```

**2. Implement Component** (Green):
```bash
# Create component file
touch src/components/AddressForm.tsx

# Write minimal code to pass test
npm test  # Should pass now
```

**3. Refactor** (Refactor):
```bash
# Improve code while keeping tests green
npm test  # Ensure still passing
```

---

### Running Development Server

```bash
npm run dev
```

**Access**: http://localhost:5173 (default Vite port)

**Hot Module Replacement**: Automatically refreshes on file changes

---

### Running Tests

```bash
# Watch mode (TDD)
npm test

# Run once with coverage
npm run test:coverage

# UI mode (visual test runner)
npm run test:ui
```

**Coverage Target**: >80% (per constitution)

---

### Building for Production

```bash
# Type check + build
npm run build

# Preview production build
npm run preview
```

**Output**: `dist/` directory (ready for S3 deployment)

---

## Component Quick Reference

### 1. AddressForm Component

**File**: `src/components/AddressForm.tsx`

**Implementation Pattern** (React Hook Form + Zod):

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { TextField, Button, Box } from '@mui/material';

const addressSchema = z.object({
  address: z.string()
    .min(1, "Address is required")
    .max(200, "Address must be under 200 characters"),
});

type AddressFormData = z.infer<typeof addressSchema>;

interface AddressFormProps {
  onSubmit: (data: AddressFormData) => void;
  disabled?: boolean;
}

export const AddressForm = ({ onSubmit, disabled }: AddressFormProps) => {
  const { register, handleSubmit, formState: { errors } } = useForm<AddressFormData>({
    resolver: zodResolver(addressSchema),
    mode: 'onBlur',  // Validate on blur (per spec)
  });

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <TextField
        {...register('address')}
        label="Enter your address"
        placeholder="123 Main St, City, State ZIP"
        error={!!errors.address}
        helperText={errors.address?.message}
        disabled={disabled}
        fullWidth
        autoFocus
      />
      <Button
        type="submit"
        variant="contained"
        disabled={disabled}
        sx={{ mt: 2 }}
      >
        Find My Representatives
      </Button>
    </Box>
  );
};
```

**Test Example**:
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AddressForm } from './AddressForm';

test('displays validation error for empty address', async () => {
  const onSubmit = vi.fn();
  render(<AddressForm onSubmit={onSubmit} />);
  
  const input = screen.getByLabelText(/enter your address/i);
  const button = screen.getByRole('button', { name: /find/i });
  
  await userEvent.click(button);
  
  expect(await screen.findByText(/address is required/i)).toBeInTheDocument();
  expect(onSubmit).not.toHaveBeenCalled();
});
```

---

### 2. RepresentativeCard Component

**File**: `src/components/RepresentativeCard.tsx`

**Implementation Pattern** (Material UI Card):

```typescript
import { Card, CardHeader, CardContent, CardActions, Avatar, Typography, Link, Box } from '@mui/material';
import { Email, Phone, LocationOn, Language } from '@mui/icons-material';
import type { Representative } from '../types/representative';

interface RepresentativeCardProps {
  representative: Representative;
}

export const RepresentativeCard = ({ representative }: RepresentativeCardProps) => {
  const { name, office, party, email, phone, address, website, photo_url } = representative;
  
  // Generate initials for placeholder
  const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2);
  
  return (
    <Card elevation={2}>
      <CardHeader
        avatar={
          photo_url ? (
            <Avatar src={photo_url} alt={`${name} - ${office}`} />
          ) : (
            <Avatar>{initials}</Avatar>
          )
        }
        title={name}
        subheader={`${office}${party ? ` (${party})` : ''}`}
      />
      <CardContent>
        {email && (
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <Email fontSize="small" />
            <Typography variant="body2">{email}</Typography>
          </Box>
        )}
        {phone && (
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <Phone fontSize="small" />
            <Typography variant="body2">{phone}</Typography>
          </Box>
        )}
        {address && (
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <LocationOn fontSize="small" />
            <Typography variant="body2">{address}</Typography>
          </Box>
        )}
      </CardContent>
      {website && (
        <CardActions>
          <Link href={website} target="_blank" rel="noopener noreferrer">
            <Language fontSize="small" /> Official Website
          </Link>
        </CardActions>
      )}
    </Card>
  );
};
```

---

### 3. useRepresentatives Hook

**File**: `src/hooks/useRepresentatives.ts`

**Implementation Pattern** (Custom Hook):

```typescript
import { useState } from 'react';
import type { Representative } from '../types/representative';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type AppState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: Representative[] }
  | { status: 'error'; message: string };

export const useRepresentatives = () => {
  const [appState, setAppState] = useState<AppState>({ status: 'idle' });

  const fetchByAddress = async (address: string) => {
    setAppState({ status: 'loading' });

    try {
      const url = `${API_BASE_URL}/representatives?address=${encodeURIComponent(address)}`;
      const response = await fetch(url);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(getErrorMessage(response.status, errorData));
      }

      const data = await response.json();
      setAppState({ status: 'success', data: data.representatives });
    } catch (error) {
      const message = error instanceof Error
        ? error.message
        : 'An unexpected error occurred. Please try again.';
      setAppState({ status: 'error', message });
    }
  };

  const clearResults = () => {
    setAppState({ status: 'idle' });
  };

  return { appState, fetchByAddress, clearResults };
};

// Helper function (see contracts/backend-api.md)
const getErrorMessage = (status: number, errorData: any): string => {
  // Implementation in contracts doc
};
```

---

## Testing Guide

### Test File Naming Convention

```
src/components/AddressForm.tsx       → src/tests/components/AddressForm.test.tsx
src/hooks/useRepresentatives.ts      → src/tests/hooks/useRepresentatives.test.ts
src/utils/grouping.ts                → src/tests/utils/grouping.test.ts
```

---

### Unit Test Example (Component)

```typescript
import { render, screen } from '@testing-library/react';
import { RepresentativeCard } from './RepresentativeCard';

const mockRepresentative = {
  id: 'test-id',
  name: 'Jane Doe',
  office: 'US Senator',
  party: 'Democratic',
  government_level: 'federal' as const,
  jurisdiction: 'United States',
  email: 'jane@senate.gov',
  phone: '202-555-0100',
  address: null,
  website: 'https://jane.senate.gov',
  photo_url: null,
};

test('displays representative information', () => {
  render(<RepresentativeCard representative={mockRepresentative} />);
  
  expect(screen.getByText('Jane Doe')).toBeInTheDocument();
  expect(screen.getByText(/US Senator/)).toBeInTheDocument();
  expect(screen.getByText('jane@senate.gov')).toBeInTheDocument();
});

test('displays initials when photo_url is null', () => {
  render(<RepresentativeCard representative={mockRepresentative} />);
  
  const avatar = screen.getByText('JD'); // Jane Doe → JD
  expect(avatar).toBeInTheDocument();
});
```

---

### Integration Test Example (Complete Flow)

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HomePage } from './HomePage';
import { server } from '../tests/mocks/server';
import { rest } from 'msw';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

test('complete lookup flow: form submit → loading → results', async () => {
  // Mock API success
  server.use(
    rest.get(`${API_BASE_URL}/representatives`, (req, res, ctx) => {
      return res(ctx.json({
        representatives: [{ id: '1', name: 'Test Rep', /* ... */ }],
        metadata: { address: req.url.searchParams.get('address') },
      }));
    })
  );

  render(<HomePage />);
  
  const input = screen.getByLabelText(/enter your address/i);
  const button = screen.getByRole('button', { name: /find/i });
  
  await userEvent.type(input, '123 Main St, Seattle, WA 98101');
  await userEvent.click(button);
  
  // Loading indicator appears
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  
  // Results appear
  await waitFor(() => {
    expect(screen.getByText('Test Rep')).toBeInTheDocument();
  });
});
```

---

## Deployment

### Build for Production

```bash
npm run build
```

**Output**: `dist/` directory containing:
- Optimized JavaScript bundles
- Minified CSS
- Static assets
- index.html entry point

---

### Deploy to AWS S3 + CloudFront

**Prerequisites**:
- S3 bucket created via CDK (infrastructure/stacks/frontend_stack.py)
- CloudFront distribution configured
- AWS CLI configured locally

**Deployment Commands**:
```bash
# Build application
npm run build

# Sync to S3
aws s3 sync dist/ s3://represent-app-frontend-bucket --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id E123456 --paths "/*"
```

**CDK Deployment** (Automated):
```bash
# From infrastructure/
cdk deploy FrontendStack
```

---

## Troubleshooting

### Issue: "Cannot read properties of undefined (vite)"

**Solution**: Ensure environment variable uses `VITE_` prefix
```typescript
// ✅ Correct
const API_URL = import.meta.env.VITE_API_BASE_URL;

// ❌ Wrong
const API_URL = process.env.REACT_APP_API_BASE_URL;
```

---

### Issue: CORS errors when calling backend API

**Solution**: Backend API Gateway must include CORS headers
- Check backend CDK stack configuration
- Verify `Access-Control-Allow-Origin` header present
- Use browser DevTools Network tab to inspect response headers

---

### Issue: Tests failing with "Cannot find module '@testing-library/jest-dom'"

**Solution**: Ensure setupTests.ts is configured in vite.config.ts
```typescript
test: {
  setupFiles: './src/setupTests.ts',  // ← Must be present
}
```

---

### Issue: Material UI styles not applying

**Solution**: Ensure Emotion dependencies installed
```bash
npm install @emotion/react @emotion/styled
```

---

### Issue: TypeScript errors in test files

**Solution**: Add vitest types to tsconfig.json
```json
{
  "compilerOptions": {
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  }
}
```

---

## Performance Tips

1. **Lazy Load Components**: Use React.lazy() for code splitting (post-MVP)
2. **Optimize Images**: Compress representative photos (CloudFront handles this)
3. **Bundle Analysis**: Run `npm run build -- --analyze` to inspect bundle size
4. **Lighthouse Audit**: Run in Chrome DevTools to identify performance issues

---

## Next Steps

1. ✅ Setup complete
2. → Implement AddressForm component (TDD)
3. → Implement useRepresentatives hook (TDD)
4. → Implement RepresentativeCard component (TDD)
5. → Implement ResultsDisplay component (TDD)
6. → Implement HomePage component (Integration testing)
7. → Add responsive design (Test at 320px, 768px, 1024px)
8. → Accessibility audit (WCAG AA compliance)
9. → Deploy to S3 + CloudFront

---

## Related Documentation

- [Feature Spec](spec.md) - Full feature specification
- [Data Model](data-model.md) - TypeScript types and interfaces
- [Backend API Contract](contracts/backend-api.md) - API integration guide
- [GitHub Research](github-research.md) - Pattern examples from real projects
- [Research Decisions](research.md) - Technology choices and rationale
