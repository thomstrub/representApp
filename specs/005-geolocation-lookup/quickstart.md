# Quickstart Guide: Geolocation-Based Representative Lookup

**Feature**: 005-geolocation-lookup  
**Date**: 2026-02-10  
**Status**: Ready for Implementation

## Overview

This guide helps developers quickly test and validate the geolocation-based representative lookup feature. The feature replaces Google Civic Information API with Google Maps Geocoding + OpenStates geo endpoint.

---

## Prerequisites

### 1. API Keys Required

You'll need two API keys stored in AWS Systems Manager Parameter Store:

- **Google Maps API Key**: `/represent-app/google-maps-api-key`
  - Get key from: https://console.cloud.google.com/apis/credentials
  - Enable: "Geocoding API"
  - Add to Parameter Store (SecureString type)

- **OpenStates API Key**: `/represent-app/openstates-api-key` (already exists)
  - If missing, get key from: https://openstates.org/api/register/

### 2. Python Environment

```bash
cd backend

# Install dependencies (including new googlemaps library)
pip install -r requirements.txt

# Verify googlemaps installed
python -c "import googlemaps; print(googlemaps.__version__)"
```

### 3. AWS Credentials

Ensure AWS CLI is configured with credentials that have:
- `ssm:GetParameter` permission for Parameter Store
- Lambda invoke permissions (for local testing)

```bash
# Verify AWS credentials
aws sts get-caller-identity
```

---

## Quick Test: Python Shell

### Test 1: Google Maps Geocoding

```python
import googlemaps

# Get API key from Parameter Store
import boto3
ssm = boto3.client('ssm')
response = ssm.get_parameter(Name='/represent-app/google-maps-api-key', WithDecryption=True)
api_key = response['Parameter']['Value']

# Initialize client
gmaps = googlemaps.Client(key=api_key)

# Test geocoding
result = gmaps.geocode('1600 Pennsylvania Avenue NW, Washington, DC')
print(f"Formatted Address: {result[0]['formatted_address']}")
print(f"Latitude: {result[0]['geometry']['location']['lat']}")
print(f"Longitude: {result[0]['geometry']['location']['lng']}")

# Expected output:
# Formatted Address: 1600 Pennsylvania Avenue NW, Washington, DC 20500, USA
# Latitude: 38.8976763
# Longitude: -77.0365298
```

### Test 2: OpenStates Geo Endpoint

```python
import requests
import boto3

# Get API key
ssm = boto3.client('ssm')
response = ssm.get_parameter(Name='/represent-app/openstates-api-key', WithDecryption=True)
api_key = response['Parameter']['Value']

# Test geo endpoint (Seattle coordinates)
url = "https://v3.openstates.org/people.geo"
params = {
    'lat': 47.6105,
    'lng': -122.3115,
    'apikey': api_key
}

response = requests.get(url, params=params)
data = response.json()

print(f"Found {len(data['results'])} representatives")
for person in data['results']:
    print(f"- {person['name']} ({person['current_role']['title']}) - {person['jurisdiction']['name']}")

# Expected output:
# Found 6 representatives
# - Adam Smith (Representative) - United States
# - Patty Murray (Senator) - United States
# - Maria Cantwell (Senator) - United States
# - Rebecca Saldaña (Senator) - Washington
# - Chipalo Street (Representative) - Washington
# - Sharon Tomiko Santos (Representative) - Washington
```

### Test 3: End-to-End Flow

```python
import googlemaps
import requests
import boto3
from uuid import uuid4
from datetime import datetime

# Get both API keys
ssm = boto3.client('ssm')
google_key = ssm.get_parameter(Name='/represent-app/google-maps-api-key', WithDecryption=True)['Parameter']['Value']
openstates_key = ssm.get_parameter(Name='/represent-app/openstates-api-key', WithDecryption=True)['Parameter']['Value']

# Step 1: Geocode address
gmaps = googlemaps.Client(key=google_key)
address = "Pike Place Market, Seattle, WA"
geocode_result = gmaps.geocode(address)

if not geocode_result:
    print("Address not found!")
else:
    location = geocode_result[0]['geometry']['location']
    formatted_address = geocode_result[0]['formatted_address']
    print(f"Geocoded: {formatted_address}")
    print(f"Coordinates: {location['lat']}, {location['lng']}")
    
    # Step 2: Query OpenStates
    url = "https://v3.openstates.org/people.geo"
    params = {
        'lat': location['lat'],
        'lng': location['lng'],
        'apikey': openstates_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Step 3: Transform to Representative model
    representatives = []
    for person in data['results']:
        rep = {
            'id': str(uuid4()),
            'name': person['name'],
            'position': person['current_role']['title'],
            'district': person['current_role'].get('district'),
            'state': person['jurisdiction']['name'],
            'party': person.get('party'),
            'contact_info': {
                'email': person.get('email'),
                'phone': None,
                'image': person.get('image')
            },
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        }
        representatives.append(rep)
    
    # Step 4: Group by government level
    grouped = {'federal': [], 'state': [], 'local': []}
    for rep, person in zip(representatives, data['results']):
        classification = person['jurisdiction']['classification']
        if classification == 'country':
            grouped['federal'].append(rep)
        elif classification == 'state':
            grouped['state'].append(rep)
        else:
            grouped['local'].append(rep)
    
    # Step 5: Build final response
    result = {
        'representatives': grouped,
        'metadata': {
            'address': formatted_address,
            'coordinates': {
                'latitude': location['lat'],
                'longitude': location['lng']
            },
            'total_count': len(representatives),
            'government_levels': [k for k, v in grouped.items() if v]
        },
        'warnings': []
    }
    
    print(f"\nFederal: {len(result['representatives']['federal'])}")
    print(f"State: {len(result['representatives']['state'])}")
    print(f"Local: {len(result['representatives']['local'])}")
    print(f"Total: {result['metadata']['total_count']}")
```

---

## Quick Test: Unit Tests

### Run Specific Test Files (TDD Workflow)

```bash
cd backend

# Test geocoding functionality (User Story 1)
pytest tests/unit/services/test_google_maps.py -v

# Test OpenStates geo endpoint (User Story 2)
pytest tests/unit/services/test_openstates_geo.py -v

# Test handler integration (User Story 3)
pytest tests/integration/test_address_to_reps.py -v

# Run all feature tests
pytest tests/ -v -k "geolocation or google_maps or openstates_geo"
```

### Expected Test Structure

```
tests/
├── unit/
│   ├── services/
│   │   ├── test_google_maps.py           # NEW
│   │   └── test_openstates_geo.py        # NEW
│   └── handlers/
│       └── test_address_lookup.py        # MODIFIED
└── integration/
    └── test_address_to_reps.py           # NEW
```

---

## Quick Test: Local Lambda Invocation

### Simulate API Gateway Event

```bash
cd backend

# Create test event JSON
cat > test_event.json << 'EOF'
{
  "queryStringParameters": {
    "address": "Pike Place Market, Seattle, WA"
  },
  "requestContext": {
    "requestId": "test-request-id"
  }
}
EOF

# Invoke handler locally (assuming handler at src/handlers/address_lookup.py)
python -c "
import json
import sys
from src.handlers.address_lookup import lambda_handler

class MockContext:
    aws_request_id = 'test-request-id'

with open('test_event.json') as f:
    event = json.load(f)

result = lambda_handler(event, MockContext())
print(json.dumps(json.loads(result['body']), indent=2))
"
```

---

## Quick Test: API Endpoint (Deployed)

### Using curl

```bash
# Replace with your actual API Gateway endpoint
API_URL="https://your-api-id.execute-api.us-west-2.amazonaws.com"

# Test 1: Valid address (Seattle)
curl -X GET "${API_URL}/representatives?address=Pike%20Place%20Market,%20Seattle,%20WA" \
  -H "Content-Type: application/json" \
  | jq '.'

# Test 2: Valid address (Washington DC)
curl -X GET "${API_URL}/representatives?address=1600%20Pennsylvania%20Avenue%20NW,%20Washington,%20DC" \
  -H "Content-Type: application/json" \
  | jq '.metadata.total_count'

# Test 3: Invalid address (should return 400)
curl -X GET "${API_URL}/representatives?address=invalid" \
  -H "Content-Type: application/json" \
  | jq '.error'

# Test 4: Missing address (should return 400)
curl -X GET "${API_URL}/representatives" \
  -H "Content-Type: application/json" \
  | jq '.error'
```

### Using Python requests

```python
import requests

API_URL = "https://your-api-id.execute-api.us-west-2.amazonaws.com"

# Test valid address
response = requests.get(
    f"{API_URL}/representatives",
    params={'address': 'Pike Place Market, Seattle, WA'}
)

print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Total Representatives: {data['metadata']['total_count']}")
print(f"Federal: {len(data['representatives']['federal'])}")
print(f"State: {len(data['representatives']['state'])}")
print(f"Local: {len(data['representatives']['local'])}")
```

---

## Validation Checklist

Use this checklist to verify the feature is working correctly:

### User Story 1: Google Geolocation API
- [ ] Valid addresses geocode successfully to lat/lng coordinates
- [ ] Invalid addresses return appropriate error message (400)
- [ ] Geocoding timeout is respected (5 seconds)
- [ ] Geocoding errors are logged with X-Ray tracing

### User Story 2: OpenStates Geo Endpoint
- [ ] Valid coordinates return representatives from OpenStates
- [ ] Coordinates outside US or with no data return empty results (not error)
- [ ] OpenStates timeout is respected (10 seconds)
- [ ] Representatives include federal, state, and local levels

### User Story 3: End-to-End Flow
- [ ] Address → Representatives flow completes in <3 seconds
- [ ] Results are grouped by government level (federal/state/local)
- [ ] Response structure matches existing frontend contract
- [ ] Metadata includes geocoded address and coordinates
- [ ] Total count matches number of representatives returned

### User Story 4: Cleanup (Post-Migration)
- [ ] GoogleCivicClient code removed from codebase
- [ ] Google Civic API tests removed or updated
- [ ] Parameter Store Google Civic key deprecated
- [ ] Documentation updated to reference geolocation approach
- [ ] All existing tests still pass after cleanup

---

## Troubleshooting

### Issue: "Google Maps API key not found"

**Solution**:
```bash
# Add key to Parameter Store
aws ssm put-parameter \
  --name "/represent-app/google-maps-api-key" \
  --value "YOUR_GOOGLE_MAPS_API_KEY" \
  --type "SecureString" \
  --description "Google Maps Geocoding API key"

# Verify
aws ssm get-parameter --name "/represent-app/google-maps-api-key" --with-decryption
```

### Issue: "ImportError: No module named googlemaps"

**Solution**:
```bash
cd backend
pip install googlemaps>=4.10.0

# Or reinstall all dependencies
pip install -r requirements.txt
```

### Issue: "Geocoding returns no results"

**Possible Causes**:
- Address is not in the US (OpenStates only covers US)
- Address is too vague (e.g., just "Main St")
- Address has typos or is malformed

**Solution**: Try with a more complete address including city and state.

### Issue: "OpenStates returns empty results"

**Possible Causes**:
- Coordinates are valid but outside US territories
- Coordinates are in a location where OpenStates has no data

**Expected Behavior**: This is not an error - return empty results with appropriate metadata.

### Issue: "Timeout errors"

**Solution**:
- Check network connectivity
- Verify API keys are valid
- Check CloudWatch logs for detailed error messages
- Ensure Lambda timeout is set to 15+ seconds

### Issue: "Lambda execution role permissions"

**Solution**:
```bash
# Add SSM GetParameter permission to Lambda role
aws iam put-role-policy \
  --role-name your-lambda-role-name \
  --policy-name ParameterStoreAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": ["ssm:GetParameter"],
      "Resource": "arn:aws:ssm:*:*:parameter/represent-app/*"
    }]
  }'
```

---

## Performance Benchmarks

Expected performance metrics for validation:

| Metric | Target | Notes |
|--------|--------|-------|
| Geocoding latency | <1s typical | Google Maps usually sub-second |
| OpenStates latency | <2s typical | OpenStates usually 1-2s |
| End-to-end latency | <3s | Total address → representatives |
| Success rate | >95% | For valid US addresses |
| Geocoding accuracy | >95% | For complete addresses |

---

## Next Steps

After validating this feature:

1. **User Story 1 (P1)**: Implement and test Google Maps geocoding
2. **User Story 2 (P2)**: Implement and test OpenStates geo endpoint
3. **User Story 3 (P3)**: Integrate end-to-end flow
4. **User Story 4 (P4)**: Clean up legacy Google Civic code

**Follow TDD workflow**: Write tests FIRST, then implement code.

---

## References

- [Feature Spec](spec.md) - Full feature specification
- [Research Document](research.md) - Technology decisions and patterns
- [Data Model](data-model.md) - Entity definitions and transformations
- [API Contract](contracts/address-lookup-api.yaml) - OpenAPI specification
- [Implementation Plan](plan.md) - Detailed implementation plan

---

**Last Updated**: 2026-02-10  
**Status**: Ready for implementation
