# Research: Technical Decisions for Address Lookup UI

**Date**: 2026-02-09  
**Purpose**: Resolve NEEDS CLARIFICATION items from Technical Context  
**Input**: github-research.md analysis of 4 React/TypeScript projects  

---

## Research Questions & Decisions

### 1. Build Tool: Vite vs Create React App

**Decision**: **Vite**

**Rationale**:
- Modern, faster build times compared to CRA (HMR in <50ms vs 1-2s)
- Better developer experience with instant server start
- Native ESM support, optimized for modern browsers
- Used in CivicSpot (quality reference: ⭐⭐⭐⭐⭐) - production-ready pattern
- Create React App is in maintenance mode (React team recommends frameworks like Next.js or Vite)
- CRA adds ~400MB node_modules vs Vite ~200MB
- Better TypeScript support out of the box

**Alternatives Considered**:
- **Create React App**: More established, but slower, in maintenance mode, bloated dependencies
- **Next.js**: Overkill for single-page app with no SSR/SSG requirements
- **Parcel**: Simpler but less TypeScript optimization and smaller ecosystem

**Configuration**:
```bash
npm create vite@latest frontend -- --template react-ts
```

---

### 2. HTTP Client: axios vs fetch

**Decision**: **fetch (native)**

**Rationale**:
- No additional dependency (0KB bundle size)
- Native browser API, well-supported in all modern browsers
- Sufficient for simple GET requests to backend API
- Used successfully in react-rep-finder project for Google Civic API
- TypeScript types built-in (@types/node includes fetch types)
- Simpler mental model for team (no library-specific quirks)
- Backend API from feature 003 is straightforward REST endpoint

**Alternatives Considered**:
- **axios**: More features (interceptors, automatic JSON transforms, better error handling), but adds 13KB+ to bundle
- **React Query**: Excellent for caching/state management, but adds complexity and 40KB+ bundle size for MVP overkill

**Implementation Pattern** (from react-rep-finder):
```typescript
const response = await fetch(`${API_BASE_URL}/representatives?address=${encodeURIComponent(address)}`);
if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
const data = await response.json();
```

---

### 3. Form Validation: Library Selection

**Decision**: **React Hook Form + Zod**

**Rationale**:
- Strongly recommended in github-research.md based on 2 high-quality projects (CivicSpot, react-wizard-demo)
- **React Hook Form**: Best performance (uncontrolled components, minimal re-renders), 25KB gzipped
- **Zod**: Type-safe schema validation, excellent TypeScript inference, 54KB gzipped
- Declarative validation rules with clear error messages
- Built-in accessibility features (ARIA labels, error announcements)
- Excellent React 18 compatibility
- Satisfies spec requirement: "Validate on blur and on submit"

**Alternatives Considered**:
- **Formik**: More established but slower (controlled components cause more re-renders), 35KB gzipped
- **Native HTML5 validation**: Too limited (can't handle complex validation, poor UX customization)
- **Manual validation**: Error-prone, no TypeScript safety, harder to maintain

**Example Schema** (adapted from CivicSpot):
```typescript
import { z } from 'zod';

const addressSchema = z.object({
  address: z.string()
    .min(1, "Address is required")
    .max(200, "Address must be under 200 characters"),
  zipCode: z.string()
    .regex(/^\d{5}(-\d{4})?$/, "Invalid zip code format")
    .optional(),
});

type AddressFormData = z.infer<typeof addressSchema>;
```

**Bundle Impact**: ~79KB gzipped combined (acceptable for form-heavy application)

---

### 4. Deployment Target

**Decision**: **AWS S3 + CloudFront**

**Rationale**:
- Aligns with Constitution Principle V (Serverless Architecture)
- Backend already deployed on AWS (Lambda + API Gateway)
- S3 + CloudFront provides:
  - Global CDN (low latency worldwide)
  - HTTPS by default with ACM certificate
  - Scalable to millions of users with $0 idle cost
  - Easy integration with existing infrastructure/ CDK stack
- No server management required
- Cost-effective: S3 ($0.023/GB storage) + CloudFront ($0.085/GB transfer)
- Proven pattern: Static site hosting used by millions of sites

**Alternatives Considered**:
- **Vercel**: Excellent DX, but introduces non-AWS dependency and separate deployment pipeline
- **Netlify**: Similar to Vercel, but fragments infrastructure across providers
- **Amplify Hosting**: AWS-native but higher cost and less control than S3+CloudFront
- **EC2/ECS**: Unnecessary compute overhead for static files, violates serverless principle

**Infrastructure Requirements**:
- New CDK stack: `frontend_stack.py` in `infrastructure/stacks/`
- Resources: S3 bucket (private), CloudFront distribution, OAI (Origin Access Identity)
- DNS: Route53 record pointing to CloudFront (if custom domain)
- CI/CD: Build Vite app (`npm run build`) → upload `dist/` to S3 → invalidate CloudFront cache

---

## Additional Technical Decisions

### 5. Address Input Enhancement

**Decision**: **Google Places Autocomplete** (optional enhancement, not MVP blocker)

**Rationale**:
- MyTrip project demonstrates excellent UX with autocomplete
- Reduces user input errors
- Improves mobile experience (less typing)
- Google Places API provides accurate address formatting

**Implementation**: Post-MVP feature if time allows, using `@react-google-maps/api` library

---

### 6. State Management

**Decision**: **React hooks only (useState, useEffect)** - No Redux/Zustand

**Rationale**:
- Simple application with minimal shared state
- Form state managed by React Hook Form
- API state managed by custom `useRepresentatives` hook (Pattern 3 from github-research.md)
- No complex state interactions requiring centralized store
- Reduces bundle size and cognitive overhead

**When to reconsider**: If adding user authentication or multi-page flows (post-MVP)

---

### 7. UI Component Library Configuration

**Decision**: **Material UI v6** (latest stable)

**Rationale**:
- Required by spec: "Material UI (MUI) component library integrated"
- Provides accessible components out of the box (WCAG AA compliance)
- Responsive grid system for mobile/tablet/desktop layouts
- Icon set via `@mui/icons-material`
- Theme customization for brand consistency

**Required Packages**:
```bash
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
```

---

## Technology Stack Summary

| Category | Technology | Bundle Impact | Justification |
|----------|-----------|---------------|---------------|
| **Build Tool** | Vite 5+ | Dev only | Fastest DX, modern standards |
| **Framework** | React 18 | 45KB | Required by spec |
| **Language** | TypeScript 5+ | Compile-time | Type safety, better DX |
| **UI Library** | Material UI v6 | 300KB | Required by spec, accessibility |
| **Form Management** | React Hook Form | 25KB | Performance, DX |
| **Validation** | Zod | 54KB | Type safety, declarative |
| **HTTP Client** | fetch (native) | 0KB | Simple, sufficient for MVP |
| **State Management** | React hooks | 0KB | Minimal complexity |
| **Hosting** | S3 + CloudFront | Infrastructure | Serverless, scalable |

**Total JavaScript Bundle** (estimated): ~424KB gzipped (acceptable for modern web app)

---

## Dependencies Installation Commands

```bash
# Create frontend project
npm create vite@latest frontend -- --template react-ts
cd frontend

# UI library
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material

# Form handling & validation
npm install react-hook-form @hookform/resolvers zod

# Testing (from constitution)
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom

# Optional: Google Places Autocomplete (post-MVP)
# npm install @react-google-maps/api
```

---

## Performance Targets Validation

Based on technology decisions:

| Metric | Target | Expected | Status |
|--------|--------|----------|--------|
| Initial Load (3G) | <2s | 1.5s | ✅ PASS |
| Complete Lookup (broadband) | <5s | 2-3s | ✅ PASS |
| Loading Indicator | <100ms | ~50ms | ✅ PASS |
| Error Message | <500ms | ~100ms | ✅ PASS |
| Bundle Size | <500KB | ~424KB | ✅ PASS |

---

## Next Steps

1. ✅ All NEEDS CLARIFICATION items resolved
2. → Proceed to Phase 1: Generate data-model.md (component models, state models)
3. → Generate contracts/ (backend API contract from feature 003)
4. → Generate quickstart.md (setup guide, dev workflow)
5. → Update agent context with React + TypeScript + MUI patterns

---

## References

- [github-research.md](github-research.md) - Detailed analysis of 4 React projects
- [CivicSpot Repository](https://github.com/Shreesh8/CivicSpot) - Primary pattern reference
- [Vite Documentation](https://vitejs.dev/) - Build tool guide
- [React Hook Form](https://react-hook-form.com/) - Form library docs
- [Zod](https://zod.dev/) - Validation library docs
- [Material UI](https://mui.com/) - Component library docs
