# GitHub Research: React/TypeScript Address Lookup Projects

**Date**: February 9, 2026  
**Purpose**: Identify reusable patterns and components from similar projects for feature 004-address-ui  
**Research Scope**: React + TypeScript projects with address lookup, form validation, API integration, and card-based displays

---

## Executive Summary

Analyzed 4 React projects implementing address lookup interfaces with varying approaches to validation, API integration, and UI patterns. Key finding: Modern projects heavily favor **React Hook Form + Zod validation** for form handling, and there's an existing project using the **Google Civic Information API** that closely matches our requirements.

### Top Recommendations:
1. **Validation**: React Hook Form + Zod (from CivicSpot & react-wizard-demo)
2. **Address Input**: Google Places Autocomplete (from MyTrip)
3. **API Pattern**: fetch with proper error handling (from react-rep-finder)
4. **Card Layout**: shadcn/ui or MUI Card components with responsive grid

---

## Project 1: CivicSpot (Civic Engagement Platform)

**Repository**: [Shreesh8/CivicSpot](https://github.com/Shreesh8/CivicSpot)  
**Stars**: 2 | **Last Updated**: December 2025 (Active)  
**Quality**: ⭐⭐⭐⭐⭐ Excellent - Production-ready patterns

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite
- **UI Library**: shadcn/ui (similar philosophy to Material UI)
- **Form Handling**: React Hook Form + Zod validation
- **Styling**: Tailwind CSS
- **APIs**: Google Maps API, Google Places, Google Vision API
- **Backend**: Supabase
- **Routing**: React Router v6

### Key Components

#### 1. Address/Location Form ([IssueForm.tsx](https://github.com/Shreesh8/CivicSpot/blob/main/src/components/issues/IssueForm.tsx))
```typescript
// Lines 695-728: Location input with Google Places
<FormField
  control={form.control}
  name="location"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Location</FormLabel>
      <FormControl>
        <Input
          placeholder="Enter address or use map"
          {...field}
        />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>
```

**Pattern Highlights**:
- Zod schema validation integrated with React Hook Form
- Real-time validation (`mode: "onChange"`)
- Interactive map-based location selection fallback
- "Use My Location" geolocation feature

#### 2. Validation Schema Pattern ([IssueForm.tsx#L58-97](https://github.com/Shreesh8/CivicSpot/blob/main/src/components/issues/IssueForm.tsx#L58-97))
```typescript
const formSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  description: z.string().min(20, "Description must be at least 20 characters"),
  location: z.string().min(1, "Location is required"),
  category: z.string().min(1, "Category is required"),
  photos: z.array(z.instanceof(File)).max(5, "Maximum 5 photos allowed"),
});
```

**Reusable Pattern**:
- Declarative validation rules
- Custom error messages
- TypeScript type inference from schema
- Composable validation logic

#### 3. Card Display ([IssueCard.tsx](https://github.com/Shreesh8/CivicSpot/blob/main/src/components/issues/IssueCard.tsx))
```typescript
<Card className="hover:shadow-lg transition-shadow">
  <CardHeader>
    <div className="flex justify-between items-start">
      <CardTitle>{issue.title}</CardTitle>
      <Badge>{issue.category}</Badge>
    </div>
  </CardHeader>
  <CardContent>
    <p className="text-sm text-muted-foreground">{issue.description}</p>
    <div className="flex items-center gap-2 mt-2">
      <MapPin className="h-4 w-4" />
      <span className="text-xs">{issue.location}</span>
    </div>
  </CardContent>
  <CardFooter>
    {/* Actions */}
  </CardFooter>
</Card>
```

**Pattern Highlights**:
- Composable card structure (Header, Content, Footer)
- Hover states and transitions
- Icon integration
- Badge components for status/category
- Responsive grid layout

#### 4. API Integration - Google Maps Loader
```typescript
// Lazy-load Google Maps API
const loadGoogleMapsScript = () => {
  return new Promise((resolve, reject) => {
    if (window.google?.maps) {
      resolve(window.google.maps);
      return;
    }
    // Load script dynamically
  });
};
```

**Reusable Pattern**:
- Lazy loading external scripts
- Promise-based API initialization
- Singleton pattern for script loading

### Pros for Our Project
✅ Modern TypeScript patterns  
✅ Excellent form validation approach  
✅ Responsive card layouts  
✅ Clean component composition  
✅ Active development (December 2025)

### Cons
⚠️ Uses Tailwind instead of Material UI (patterns still transferable)  
⚠️ shadcn/ui instead of MUI (but similar component philosophy)

### Recommended Patterns to Adopt
1. **React Hook Form + Zod validation** - Industry standard, excellent TypeScript support
2. **Card component structure** - Composable Header/Content/Footer pattern works with MUI
3. **Real-time validation** with `mode: "onChange"`
4. **FormField render prop pattern** for consistent field styling

---

## Project 2: react-rep-finder (Representative Finder)

**Repository**: [dboudet/react-rep-finder](https://github.com/dboudet/react-rep-finder)  
**Stars**: 1 | **Last Updated**: July 2021  
**Quality**: ⭐⭐⭐ Good - Functional but older patterns

### Technology Stack
- **Frontend**: React 17 (JavaScript - no TypeScript)
- **UI Library**: Bootstrap 5
- **API**: **Google Civic Information API** ⭐ (Exactly what we need!)
- **Auth**: Firebase Authentication
- **Routing**: React Router v5

### Key Components

#### 1. Google Civic API Integration ([RepresentativeSearch.js#L6-37](https://github.com/dboudet/react-rep-finder/blob/main/src/components/RepresentativeSearch.js#L6-37))
```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);
  
  try {
    const response = await fetch(
      `https://civicinfo.googleapis.com/civicinfo/v2/representatives?address=${address}&key=${API_KEY}`
    );
    const data = await response.json();
    
    if (data.error) {
      setError(data.error.message);
    } else {
      setResults(data);
    }
  } catch (err) {
    setError("Failed to fetch representatives");
  } finally {
    setLoading(false);
  }
};
```

**Pattern Highlights**:
- Direct fetch implementation (no axios dependency)
- Loading state management
- Error handling with user feedback
- Address query parameter encoding

#### 2. Representative Display ([RepresentativeSearchResults.js](https://github.com/dboudet/react-rep-finder/blob/main/src/components/RepresentativeSearchResults.js))
```javascript
{officials.map((official, index) => (
  <div key={index} className="card mb-3">
    <div className="card-body">
      {official.photoUrl && <img src={official.photoUrl} alt={official.name} />}
      <h5>{official.name}</h5>
      <p><strong>Office:</strong> {offices[index]?.name}</p>
      <p><strong>Party:</strong> {official.party}</p>
      <p><strong>Phone:</strong> {official.phones?.[0]}</p>
      <p><strong>Email:</strong> {official.emails?.[0]}</p>
      {official.urls && (
        <a href={official.urls[0]} target="_blank" rel="noopener noreferrer">
          Official Website
        </a>
      )}
    </div>
  </div>
))}
```

**Pattern Highlights**:
- Maps Google Civic API response to cards
- Handles optional fields (phones, emails, photoUrl)
- External link handling with security attributes
- Groups offices with officials

#### 3. Form Pattern
```javascript
<form onSubmit={handleSubmit}>
  <input
    type="text"
    value={address}
    onChange={(e) => setAddress(e.target.value)}
    placeholder="Enter your address"
    required
  />
  <button type="submit" disabled={loading}>
    {loading ? "Searching..." : "Find My Representatives"}
  </button>
</form>

{error && <div className="alert alert-danger">{error}</div>}
```

**Pattern Highlights**:
- Controlled input component
- Disabled submit during loading
- Clear error display
- HTML5 `required` attribute

### Pros for Our Project
✅ **Directly uses Google Civic Information API** - Proven integration pattern  
✅ Shows how to map API response to UI  
✅ Simple, understandable code  
✅ Handles optional data fields gracefully

### Cons
⚠️ No TypeScript (we'll need to add types)  
⚠️ Older React patterns (function components but older hooks usage)  
⚠️ No advanced validation library  
⚠️ Bootstrap instead of Material UI

### Recommended Patterns to Adopt
1. **Google Civic API integration pattern** - Direct fetch, query params, error handling
2. **Optional field handling** - `official.phones?.[0]` pattern
3. **Loading state management** - Simple boolean flag
4. **Response mapping** - offices array + officials array correlation

---

## Project 3: MyTrip (Travel Planning with Address Autocomplete)

**Repository**: [PolThm/MyTrip](https://github.com/PolThm/MyTrip)  
**Stars**: 3 | **Last Updated**: July 2025  
**Quality**: ⭐⭐⭐⭐ Very Good - Modern patterns with Redux

### Technology Stack
- **Frontend**: React 18 + TypeScript + Redux Toolkit
- **UI Library**: Tailwind CSS (custom components)
- **APIs**: Google Places API (Autocomplete), Google Distance Matrix API
- **Payment**: Stripe API integration
- **Auth**: Firebase Authentication

### Key Components

#### 1. Address Autocomplete Component ([InputAutocomplete.tsx](https://github.com/PolThm/MyTrip/blob/main/src/components/InputAutocomplete.tsx))
```typescript
import PlacesAutocomplete, {
  geocodeByAddress,
  getLatLng,
} from 'react-places-autocomplete';

interface InputAutocompleteProps {
  updateInputAddress: (address: string, lat: number, lng: number) => void;
  label: string;
  placeholder: string;
}

const InputAutocomplete = ({ updateInputAddress, label, placeholder }: InputAutocompleteProps) => {
  const [address, setAddress] = useState("");

  const handleSelect = async (value: string) => {
    const results = await geocodeByAddress(value);
    const latLng = await getLatLng(results[0]);
    
    setAddress(value);
    updateInputAddress(value, latLng.lat, latLng.lng);
  };

  return (
    <PlacesAutocomplete
      value={address}
      onChange={setAddress}
      onSelect={handleSelect}
      searchOptions={{ types: ['address'] }}
    >
      {({ getInputProps, suggestions, getSuggestionItemProps }) => (
        <div>
          <input
            {...getInputProps({ placeholder })}
            className="input-field"
          />
          <div className="autocomplete-dropdown">
            {suggestions.map((suggestion) => (
              <div
                {...getSuggestionItemProps(suggestion)}
                className="suggestion-item"
              >
                {suggestion.description}
              </div>
            ))}
          </div>
        </div>
      )}
    </PlacesAutocomplete>
  );
};
```

**Pattern Highlights**:
- Reusable autocomplete component
- Google Places API integration
- Geocoding for lat/lng coordinates
- TypeScript interfaces for props
- Callback pattern for parent communication
- Dropdown suggestions with keyboard navigation

#### 2. Redux State Management Pattern
```typescript
// tripSlice.ts
interface TripState {
  departure: { address: string; lat: number; lng: number } | null;
  arrival: { address: string; lat: number; lng: number } | null;
  distance: number | null;
  price: number | null;
}

const tripSlice = createSlice({
  name: 'trip',
  initialState,
  reducers: {
    setDeparture: (state, action: PayloadAction<Address>) => {
      state.departure = action.payload;
    },
    setArrival: (state, action: PayloadAction<Address>) => {
      state.arrival = action.payload;
    },
  },
});
```

**Pattern Highlights**:
- Typed Redux with RTK
- Separate state slices
- localStorage persistence middleware
- Async thunks for API calls

#### 3. Form Validation Pattern
```typescript
const [formErrorDisplayed, setFormErrorDisplayed] = useState(false);

const handleValidation = () => {
  if (!departure || !arrival) {
    setFormErrorDisplayed(true);
    toast.error("Please enter both departure and arrival addresses");
    return false;
  }
  return true;
};

const handleSubmit = (e: FormEvent) => {
  e.preventDefault();
  
  if (!handleValidation()) {
    return;
  }
  
  // Calculate distance via Google Distance Matrix API
  dispatch(calculateDistance({ departure, arrival }));
};
```

**Pattern Highlights**:
- Manual validation before submit
- Toast notifications for errors
- State-based error display control
- Conditional form enabling

### Pros for Our Project
✅ **Excellent address autocomplete pattern** - Polished UX  
✅ Google Places API integration  
✅ TypeScript throughout  
✅ Reusable input component  
✅ Modern React patterns

### Cons
⚠️ Redux overkill for simple address form (Context or local state better)  
⚠️ Tailwind instead of Material UI  
⚠️ Manual validation (Zod would be cleaner)

### Recommended Patterns to Adopt
1. **Google Places Autocomplete component** - Best-in-class address input UX
2. **Geocoding pattern** - Convert address to lat/lng for API calls
3. **Reusable input component** - Encapsulated autocomplete logic
4. **Toast notifications** - User feedback for errors/success

---

## Project 4: react-wizard-demo (Multi-Step Form Wizard)

**Repository**: [Ajaykumarchawla/react-wizard-demo](https://github.com/Ajaykumarchawla/react-wizard-demo)  
**Stars**: 0 | **Last Updated**: September 2025 (Active)  
**Quality**: ⭐⭐⭐⭐⭐ Excellent - Best validation patterns

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite
- **Form Handling**: React Hook Form + Zod validation
- **Routing**: React Router v6
- **State Management**: Context API + Reducer + localStorage
- **Styling**: CSS Modules

### Key Components

#### 1. Address Form with Validation ([UserAddress.tsx](https://github.com/Ajaykumarchawla/react-wizard-demo/blob/main/src/pages/UserAddress.tsx))
```typescript
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  city: z.string()
    .min(1, "City is required")
    .max(60, "City must be less than 60 characters"),
  zip: z.string()
    .min(3, "ZIP/Postal code is required")
    .max(12, "ZIP/Postal code must be less than 12 characters")
    .regex(/^[0-9-]+$/, "Only numbers and hyphens allowed"),
  country: z.string()
    .min(1, "Country is required")
    .max(56, "Country must be less than 56 characters"),
});

type FormData = z.infer<typeof schema>;

const UserAddress = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    mode: "onChange", // Real-time validation
  });

  const onSubmit = (data: FormData) => {
    // Save to context and proceed to next step
    dispatch({ type: 'SET_ADDRESS', payload: data });
    navigate('/step3');
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="city">City</label>
        <input
          id="city"
          {...register("city")}
          className={errors.city ? 'error' : ''}
        />
        {errors.city && <span className="error-message">{errors.city.message}</span>}
      </div>

      <div>
        <label htmlFor="zip">ZIP/Postal Code</label>
        <input
          id="zip"
          {...register("zip")}
          className={errors.zip ? 'error' : ''}
        />
        {errors.zip && <span className="error-message">{errors.zip.message}</span>}
      </div>

      <div>
        <label htmlFor="country">Country</label>
        <input
          id="country"
          {...register("country")}
          className={errors.country ? 'error' : ''}
        />
        {errors.country && <span className="error-message">{errors.country.message}</span>}
      </div>

      <button type="submit" disabled={!isValid}>
        Next Step
      </button>
    </form>
  );
};
```

**Pattern Highlights**:
- Zod schema with custom error messages
- TypeScript type inference from schema (`z.infer`)
- React Hook Form registration
- Real-time validation (`mode: "onChange"`)
- Inline error display
- Submit button disabled when invalid
- Conditional CSS classes for error state

#### 2. Wizard Context Pattern ([WizardContext.tsx](https://github.com/Ajaykumarchawla/react-wizard-demo/blob/main/src/context/WizardContext.tsx))
```typescript
interface WizardState {
  personalInfo: PersonalInfo | null;
  address: Address | null;
  preferences: Preferences | null;
  currentStep: number;
}

type WizardAction =
  | { type: 'SET_PERSONAL_INFO'; payload: PersonalInfo }
  | { type: 'SET_ADDRESS'; payload: Address }
  | { type: 'SET_PREFERENCES'; payload: Preferences }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'RESET' };

const wizardReducer = (state: WizardState, action: WizardAction): WizardState => {
  switch (action.type) {
    case 'SET_ADDRESS':
      return { ...state, address: action.payload };
    case 'NEXT_STEP':
      return { ...state, currentStep: state.currentStep + 1 };
    // ... other cases
    default:
      return state;
  }
};

// LocalStorage persistence
useEffect(() => {
  localStorage.setItem('wizardState', JSON.stringify(state));
}, [state]);
```

**Pattern Highlights**:
- Typed reducer with discriminated union actions
- Context API for global state
- localStorage persistence
- Step-based navigation
- Form data aggregation

#### 3. Navigation Control Pattern
```typescript
const { wizard, dispatch } = useWizard();
const [nextEnabled, setNextEnabled] = useState(false);

useEffect(() => {
  // Enable "Next" button only when form is valid
  setNextEnabled(isValid);
}, [isValid]);

const handleNext = () => {
  if (isValid) {
    dispatch({ type: 'NEXT_STEP' });
  }
};
```

**Pattern Highlights**:
- Conditional navigation based on validation
- Separation of form state and wizard state
- Custom hooks for wizard control

### Pros for Our Project
✅ **Best-in-class validation pattern** (React Hook Form + Zod)  
✅ TypeScript throughout with strong typing  
✅ Real-time validation  
✅ Inline, accessible error messages  
✅ Modern React patterns (hooks, context)  
✅ Active development (September 2025)

### Cons
⚠️ CSS Modules instead of Material UI  
⚠️ Multi-step wizard pattern (we don't need all steps)  
⚠️ LocalStorage persistence (may not be needed)

### Recommended Patterns to Adopt
1. **Zod validation schema** - Declarative, type-safe validation
2. **React Hook Form integration** - `register`, `handleSubmit`, `formState`
3. **Real-time validation** with `mode: "onChange"`
4. **Inline error display** - Show errors immediately next to fields
5. **TypeScript type inference** from Zod schemas

---

## Comparison Matrix

| Feature | CivicSpot | react-rep-finder | MyTrip | react-wizard-demo |
|---------|-----------|------------------|--------|-------------------|
| **TypeScript** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **React Version** | 18 | 17 | 18 | 18 |
| **Validation Library** | Zod | Manual | Manual | Zod |
| **Form Library** | React Hook Form | Manual | Manual | React Hook Form |
| **UI Framework** | shadcn/ui | Bootstrap 5 | Tailwind | CSS Modules |
| **Address Input** | Map + Text | Text only | **Google Autocomplete** | Text only |
| **API Integration** | Google Maps/Places | **Google Civic** ⭐ | Google Places/Distance | None (form only) |
| **State Management** | Local state | Context API | **Redux** | Context + Reducer |
| **Loading States** | ✅ Yes | ✅ Yes | ✅ Yes | N/A |
| **Error Handling** | ✅ Zod + Toast | ✅ State + Alert | ✅ State + Toast | ✅ Zod + Inline |
| **Card Layout** | ✅ shadcn/ui | ✅ Bootstrap | ✅ Custom | N/A |
| **Responsive Design** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Accessibility** | ✅ Good (shadcn) | ⚠️ Basic | ⚠️ Basic | ✅ Good (labels) |
| **Code Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Last Updated** | Dec 2025 | Jul 2021 | Jul 2025 | Sep 2025 |

---

## Pattern Synthesis: Recommended Tech Stack

Based on analysis of all four projects and our requirements (React + TypeScript + Material UI):

### 1. Form Validation: **React Hook Form + Zod**
**Source**: CivicSpot, react-wizard-demo  
**Why**: Industry standard, excellent TypeScript support, declarative validation

```typescript
// Example schema for our address form
const addressSchema = z.object({
  address: z.string()
    .min(1, "Address is required")
    .max(200, "Address too long"),
  zipCode: z.string()
    .regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP code format")
    .optional(),
});

type AddressFormData = z.infer<typeof addressSchema>;
```

### 2. Address Input: **Google Places Autocomplete**
**Source**: MyTrip  
**Why**: Best UX, reduces user typing, provides geocoding

```typescript
// Wrap in MUI TextField for consistency
<Autocomplete
  options={suggestions}
  renderInput={(params) => (
    <TextField {...params} label="Enter your address" />
  )}
  onSelect={handleAddressSelect}
/>
```

### 3. API Integration: **fetch with proper error handling**
**Source**: react-rep-finder  
**Why**: No extra dependencies, modern, works with TypeScript

```typescript
const fetchRepresentatives = async (address: string) => {
  try {
    setLoading(true);
    const response = await fetch(
      `${API_BASE_URL}/representatives?address=${encodeURIComponent(address)}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data: RepresentativeResponse = await response.json();
    setRepresentatives(data.representatives);
  } catch (error) {
    console.error('Failed to fetch representatives:', error);
    setError('Unable to find representatives. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

### 4. Card Display: **Material UI Card + Grid**
**Source**: CivicSpot pattern adapted to MUI  
**Why**: Matches project stack, accessible, responsive

```typescript
<Grid container spacing={3}>
  {representatives.map((rep) => (
    <Grid item xs={12} sm={6} md={4} key={rep.id}>
      <Card>
        <CardHeader
          avatar={
            rep.photoUrl ? (
              <Avatar src={rep.photoUrl} alt={rep.name} />
            ) : (
              <Avatar>{getInitials(rep.name)}</Avatar>
            )
          }
          title={rep.name}
          subheader={rep.office}
        />
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            {rep.party}
          </Typography>
          <Typography variant="body2">
            {rep.email}
          </Typography>
          <Typography variant="body2">
            {rep.phone}
          </Typography>
        </CardContent>
        <CardActions>
          {rep.website && (
            <Button size="small" href={rep.website} target="_blank">
              Official Website
            </Button>
          )}
        </CardActions>
      </Card>
    </Grid>
  ))}
</Grid>
```

### 5. State Management: **Local State + Custom Hooks**
**Source**: CivicSpot  
**Why**: Simple, no Redux overkill, clear data flow

```typescript
// Custom hook for API calls
const useRepresentatives = () => {
  const [representatives, setRepresentatives] = useState<Representative[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchByAddress = async (address: string) => {
    // ... fetch logic
  };

  return { representatives, loading, error, fetchByAddress };
};
```

### 6. Loading States: **Material UI Skeleton + CircularProgress**
**Pattern**: Combine best practices from all projects

```typescript
{loading ? (
  <Box display="flex" justifyContent="center" py={4}>
    <CircularProgress />
  </Box>
) : (
  <Grid container spacing={3}>
    {/* Cards */}
  </Grid>
)}
```

### 7. Error Handling: **Snackbar + Inline Errors**
**Source**: CivicSpot toast pattern + react-wizard-demo inline errors  
**Why**: User-friendly, accessible

```typescript
// Global errors
<Snackbar
  open={!!error}
  autoHideDuration={6000}
  onClose={() => setError(null)}
  message={error}
/>

// Form field errors
{errors.address && (
  <FormHelperText error>
    {errors.address.message}
  </FormHelperText>
)}
```

---

## Reusable Code Patterns

### Pattern 1: Address Form Component
**Adapted from**: react-wizard-demo + CivicSpot

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { TextField, Button, Box } from '@mui/material';

const addressSchema = z.object({
  address: z.string().min(1, "Address is required"),
});

type AddressFormData = z.infer<typeof addressSchema>;

interface AddressFormProps {
  onSubmit: (address: string) => void;
  loading: boolean;
}

export const AddressForm = ({ onSubmit, loading }: AddressFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<AddressFormData>({
    resolver: zodResolver(addressSchema),
    mode: "onBlur", // Validate on blur
  });

  const handleFormSubmit = (data: AddressFormData) => {
    onSubmit(data.address);
  };

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <TextField
        fullWidth
        label="Enter your address"
        {...register("address")}
        error={!!errors.address}
        helperText={errors.address?.message}
        disabled={loading}
      />
      <Button
        type="submit"
        variant="contained"
        disabled={!isValid || loading}
        sx={{ mt: 2 }}
      >
        {loading ? 'Searching...' : 'Find My Representatives'}
      </Button>
    </Box>
  );
};
```

### Pattern 2: Representative Card Component
**Adapted from**: CivicSpot + react-rep-finder

```typescript
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Avatar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { Email, Phone, Language } from '@mui/icons-material';

interface Representative {
  id: string;
  name: string;
  office: string;
  party?: string;
  photoUrl?: string;
  email?: string;
  phone?: string;
  website?: string;
}

interface RepCardProps {
  representative: Representative;
}

export const RepresentativeCard = ({ representative }: RepCardProps) => {
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardHeader
        avatar={
          representative.photoUrl ? (
            <Avatar src={representative.photoUrl} alt={representative.name} />
          ) : (
            <Avatar>{getInitials(representative.name)}</Avatar>
          )
        }
        title={representative.name}
        subheader={representative.office}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        {representative.party && (
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Party: {representative.party}
          </Typography>
        )}
        
        {representative.email && (
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <Email fontSize="small" />
            <Typography variant="body2">{representative.email}</Typography>
          </Box>
        )}
        
        {representative.phone && (
          <Box display="flex" alignItems="center" gap={1}>
            <Phone fontSize="small" />
            <Typography variant="body2">{representative.phone}</Typography>
          </Box>
        )}
      </CardContent>
      <CardActions>
        {representative.website && (
          <Button
            size="small"
            startIcon={<Language />}
            href={representative.website}
            target="_blank"
            rel="noopener noreferrer"
          >
            Official Website
          </Button>
        )}
      </CardActions>
    </Card>
  );
};
```

### Pattern 3: Custom Hook for API Calls
**Adapted from**: MyTrip + react-rep-finder

```typescript
import { useState } from 'react';

interface Representative {
  id: string;
  name: string;
  office: string;
  party?: string;
  photoUrl?: string;
  email?: string;
  phone?: string;
  website?: string;
  governmentLevel: 'federal' | 'state' | 'local';
}

interface UseRepresentativesReturn {
  representatives: Representative[];
  loading: boolean;
  error: string | null;
  fetchByAddress: (address: string) => Promise<void>;
  clearResults: () => void;
}

export const useRepresentatives = (): UseRepresentativesReturn => {
  const [representatives, setRepresentatives] = useState<Representative[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchByAddress = async (address: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `/api/representatives?address=${encodeURIComponent(address)}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRepresentatives(data.representatives || []);
      
      if (data.representatives.length === 0) {
        setError('No representatives found for this address.');
      }
    } catch (err) {
      console.error('Failed to fetch representatives:', err);
      setError('Unable to find representatives. Please check the address and try again.');
      setRepresentatives([]);
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setRepresentatives([]);
    setError(null);
  };

  return {
    representatives,
    loading,
    error,
    fetchByAddress,
    clearResults,
  };
};
```

### Pattern 4: Results Display with Grouping
**Adapted from**: CivicSpot + react-rep-finder

```typescript
import { Grid, Typography, Box, Divider } from '@mui/material';
import { RepresentativeCard } from './RepresentativeCard';

interface ResultsDisplayProps {
  representatives: Representative[];
}

export const ResultsDisplay = ({ representatives }: ResultsDisplayProps) => {
  const groupByLevel = (reps: Representative[]) => {
    return {
      federal: reps.filter(r => r.governmentLevel === 'federal'),
      state: reps.filter(r => r.governmentLevel === 'state'),
      local: reps.filter(r => r.governmentLevel === 'local'),
    };
  };

  const grouped = groupByLevel(representatives);

  const renderSection = (title: string, reps: Representative[]) => {
    if (reps.length === 0) return null;

    return (
      <Box mb={4}>
        <Typography variant="h5" component="h2" gutterBottom>
          {title}
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {reps.map((rep) => (
            <Grid item xs={12} sm={6} md={4} key={rep.id}>
              <RepresentativeCard representative={rep} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  };

  return (
    <Box>
      {renderSection('Federal Representatives', grouped.federal)}
      {renderSection('State Representatives', grouped.state)}
      {renderSection('Local Representatives', grouped.local)}
    </Box>
  );
};
```

---

## Action Items & Integration Plan

### Phase 1: Setup & Dependencies
- [ ] Install dependencies:
  ```bash
  npm install react-hook-form @hookform/resolvers zod
  npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
  npm install @react-google-maps/api  # For Places Autocomplete
  ```

### Phase 2: Create Core Components
- [ ] **AddressForm component** - Use Pattern 1 (React Hook Form + Zod)
- [ ] **RepresentativeCard component** - Use Pattern 2 (MUI Card with optional photo)
- [ ] **ResultsDisplay component** - Use Pattern 4 (Grouped by government level)

### Phase 3: API Integration
- [ ] **useRepresentatives hook** - Use Pattern 3 (Custom hook for API calls)
- [ ] Integrate with existing backend API from feature 003-address-lookup
- [ ] Add TypeScript interfaces for API response types

### Phase 4: Enhanced Features
- [ ] Add Google Places Autocomplete for address input (from MyTrip pattern)
- [ ] Implement loading skeletons for better UX
- [ ] Add error handling with Snackbar notifications
- [ ] Implement "Clear" and "Search another address" buttons

### Phase 5: Polish & Accessibility
- [ ] Add keyboard navigation support
- [ ] Ensure WCAG AA compliance
- [ ] Add ARIA labels to all interactive elements
- [ ] Test with screen readers

---

## Conclusion

We have four excellent reference projects with distinct strengths:

1. **CivicSpot**: Best overall patterns, modern validation approach
2. **react-rep-finder**: Direct Google Civic API integration (very relevant!)
3. **MyTrip**: Best address autocomplete UX
4. **react-wizard-demo**: Best form validation implementation

**Recommended Approach**:
- Start with **react-wizard-demo's** validation pattern (React Hook Form + Zod)
- Adapt **CivicSpot's** component structure to Material UI
- Use **react-rep-finder's** API integration approach
- Consider adding **MyTrip's** Google Places Autocomplete for enhanced UX

This combination provides type safety, excellent UX, and proven patterns that align with our Material UI + TypeScript stack.
