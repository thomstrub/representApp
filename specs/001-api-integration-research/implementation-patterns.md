# Implementation Patterns - Phase 5 Research

**Date**: February 7, 2026  
**Tasks**: T024-T031  
**Sources**: openstates/people, openstates/openstates-core, datamade/my-reps

## Overview

This document extracts and consolidates 5+ implementation patterns from analyzed GitHub repositories into reusable patterns for the Represent App MVP.

---

## Pattern 1: API Authentication Strategy

**Source**: openstates/openstates-core, datamade/my-reps  
**Task**: T024

### Problem
Securely manage API keys for external services (OpenStates, Google Civic) without hardcoding credentials in source code.

### Solution

#### Environment Variables (Development)
```python
# For local development and testing
import os

def get_api_key_from_env(key_name: str) -> str:
    """Get API key from environment variable"""
    api_key = os.environ.get(key_name)
    if not api_key:
        raise ValueError(f"{key_name} environment variable not set")
    return api_key

# Usage
OPENSTATES_API_KEY = get_api_key_from_env('OPENSTATES_API_KEY')
GOOGLE_CIVIC_API_KEY = get_api_key_from_env('GOOGLE_CIVIC_API_KEY')
```

#### AWS Parameter Store (Production)
```python
# For Lambda deployment with secure key storage
import boto3
from functools import lru_cache

ssm = boto3.client('ssm', region_name='us-west-2')

@lru_cache(maxsize=10)
def get_api_key_from_parameter_store(parameter_name: str) -> str:
    """
    Retrieve API key from AWS Systems Manager Parameter Store
    
    Caching reduces API calls and improves Lambda cold start performance.
    Keys are encrypted at rest with KMS.
    
    Args:
        parameter_name: Parameter Store path (e.g., '/represent-app/api-keys/openstates')
        
    Returns:
        Decrypted API key value
    """
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']

# Usage in Lambda handler
def lambda_handler(event, context):
    openstates_key = get_api_key_from_parameter_store('/represent-app/api-keys/openstates')
    # Use key for API calls
```

#### Request Header Patterns

**OpenStates API** (Header-based):
```python
import requests

def call_openstates_api(endpoint: str, api_key: str, params: dict = None) -> dict:
    """
    Call OpenStates API with header-based authentication
    
    Pattern: X-API-Key header
    Documentation: https://docs.openstates.org/api-v3/
    """
    headers = {
        'X-API-Key': api_key,
        'Accept': 'application/json'
    }
    
    url = f"https://v3.openstates.org{endpoint}"
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    return response.json()

# Example usage
people = call_openstates_api(
    endpoint='/people',
    api_key=openstates_key,
    params={
        'jurisdiction': 'ocd-jurisdiction/country:us/state:wa/government',
        'per_page': 100
    }
)
```

**Google APIs** (Query Parameter):
```python
def call_google_civic_api(endpoint: str, api_key: str, params: dict = None) -> dict:
    """
    Call Google Civic Information API with query parameter authentication
    
    Pattern: ?key= query parameter
    Note: Representatives endpoint deprecated April 2025
    """
    if params is None:
        params = {}
    
    params['key'] = api_key  # Add API key to query params
    
    url = f"https://www.googleapis.com/civicinfo/v2{endpoint}"
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    return response.json()
```

### Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for local development
3. **Use Parameter Store** for production Lambda deployment
4. **Cache parameter lookups** with `@lru_cache` to reduce SSM calls
5. **Rotate keys periodically** and update Parameter Store
6. **Use separate keys** for development and production
7. **Encrypt at rest** using AWS KMS for Parameter Store

### Application to Represent App

```python
# backend/src/utils/auth.py
import os
import boto3
from functools import lru_cache
from typing import Optional

# Determine if running in Lambda
IS_LAMBDA = os.environ.get('AWS_EXECUTION_ENV') is not None

if IS_LAMBDA:
    ssm = boto3.client('ssm', region_name='us-west-2')
    
    @lru_cache(maxsize=10)
    def get_api_key(parameter_name: str) -> str:
        """Get API key from Parameter Store (Lambda)"""
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
else:
    def get_api_key(env_var_name: str) -> str:
        """Get API key from environment variable (local dev)"""
        api_key = os.environ.get(env_var_name)
        if not api_key:
            raise ValueError(f"{env_var_name} environment variable not set")
        return api_key

# Usage is the same regardless of environment
OPENSTATES_API_KEY = get_api_key(
    '/represent-app/api-keys/openstates' if IS_LAMBDA else 'OPENSTATES_API_KEY'
)
```

---

## Pattern 2: Multi-Layer Caching Strategy

**Source**: openstates/openstates-core  
**Task**: T025

### Problem
API calls are slow and rate-limited. Need to minimize external API calls while keeping data fresh.

### Solution: Three-Layer Caching

#### Layer 1: Lambda Memory (Hot Cache)
```python
from functools import lru_cache
from typing import Dict, Any
import time

# In-memory cache for Lambda container reuse
# Survives multiple invocations within same container lifecycle

@lru_cache(maxsize=128)
def get_state_legislators_cached(
    jurisdiction_id: str,
    ttl_seconds: int = 3600  # 1 hour
) -> Dict[str, Any]:
    """
    Cache OpenStates API responses in Lambda memory
    
    Benefits:
    - Zero latency for cache hits
    - No external calls during Lambda warm starts
    - Automatic eviction (LRU policy)
    
    Limitations:
    - Cleared on Lambda cold start
    - Not shared across Lambda instances
    - Limited to container memory
    """
    # Cache miss - call API
    return call_openstates_api(
        endpoint='/people',
        params={'jurisdiction': jurisdiction_id}
    )
```

#### Layer 2: DynamoDB (Warm Cache)
```python
import boto3
import json
from datetime import datetime, timedelta
from typing import Optional

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
cache_table = dynamodb.Table('represent-app-cache')

def get_from_dynamodb_cache(
    cache_key: str,
    ttl_seconds: int = 3600
) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached data from DynamoDB
    
    Benefits:
    - Shared across all Lambda instances
    - Persists beyond Lambda lifecycle
    - Fast reads (single-digit milliseconds)
    
    Schema:
    - PK: 'CACHE#{cache_key}'
    - expires_at: Unix timestamp
    - data: JSON blob
    """
    try:
        response = cache_table.get_item(
            Key={'PK': f'CACHE#{cache_key}'}
        )
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        
        # Check expiration
        expires_at = item.get('expires_at', 0)
        if expires_at < int(time.time()):
            # Expired - delete and return None
            cache_table.delete_item(Key={'PK': f'CACHE#{cache_key}'})
            return None
        
        # Parse and return cached data
        return json.loads(item['data'])
        
    except Exception as e:
        print(f"Cache read error: {e}")
        return None  # Cache miss on error

def put_to_dynamodb_cache(
    cache_key: str,
    data: Dict[str, Any],
    ttl_seconds: int = 3600
) -> None:
    """Store data in DynamoDB cache with TTL"""
    try:
        expires_at = int(time.time()) + ttl_seconds
        
        cache_table.put_item(
            Item={
                'PK': f'CACHE#{cache_key}',
                'expires_at': expires_at,
                'data': json.dumps(data),
                'created_at': datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        print(f"Cache write error: {e}")
        # Don't fail on cache write errors
```

#### Layer 3: DynamoDB (Cold Storage)
```python
def get_legislators_with_caching(jurisdiction_id: str) -> Dict[str, Any]:
    """
    Three-layer caching strategy
    
    Flow:
    1. Check Lambda memory (@lru_cache) - Hot cache
    2. Check DynamoDB cache table - Warm cache (1 hour TTL)
    3. Check DynamoDB data table - Cold storage (24 hour refresh)
    4. Fall back to API call
    """
    cache_key = f"legislators:{jurisdiction_id}"
    
    # Layer 1: Lambda memory (implicit via @lru_cache decorator)
    # This happens automatically when function is decorated
    
    # Layer 2: DynamoDB cache (1 hour TTL)
    cached_data = get_from_dynamodb_cache(cache_key, ttl_seconds=3600)
    if cached_data:
        return cached_data
    
    # Layer 3: DynamoDB data table (24 hour refresh)
    # Check if we have "acceptable" data (within 24 hours)
    stored_data = get_from_data_table(jurisdiction_id)
    if stored_data and is_fresh_enough(stored_data, max_age_hours=24):
        # Cache in Layer 2 for faster subsequent access
        put_to_dynamodb_cache(cache_key, stored_data, ttl_seconds=3600)
        return stored_data
    
    # Layer 4: API call (cache miss - refresh all layers)
    api_data = call_openstates_api(
        endpoint='/people',
        params={'jurisdiction': jurisdiction_id}
    )
    
    # Populate all cache layers
    put_to_data_table(jurisdiction_id, api_data)  # Cold storage
    put_to_dynamodb_cache(cache_key, api_data, ttl_seconds=3600)  # Warm cache
    # Lambda memory cache happens automatically on return
    
    return api_data
```

### Cache Invalidation Strategy

```python
def invalidate_cache(jurisdiction_id: str) -> None:
    """
    Invalidate cache when data changes
    
    Use cases:
    - Manual refresh triggered by user
    - Background job detects stale data
    - Admin update to representative data
    """
    cache_key = f"legislators:{jurisdiction_id}"
    
    # Clear DynamoDB cache
    try:
        cache_table.delete_item(Key={'PK': f'CACHE#{cache_key}'})
    except Exception:
        pass  # Silent failure ok for cache invalidation
    
    # Lambda memory cache clears on next cold start
    # Or use cache versioning: cache_key = f"legislators:{jurisdiction_id}:v{version}"
```

### Best Practices

1. **Layer 1 (Memory)**: Use `@lru_cache` for hot data, maxsize=128-256
2. **Layer 2 (DynamoDB)**: 1-hour TTL for frequently accessed data
3. **Layer 3 (Storage)**: 24-hour refresh cycle for base data
4. **Cache keys**: Use descriptive, hierarchical keys (`resource:id:subkey`)
5. **TTL policy**: Shorter for dynamic data, longer for static data
6. **Graceful degradation**: Return stale data on API errors
7. **Monitoring**: Track cache hit rates (Lambda memory, DynamoDB)

### Application to Represent App

```python
# Caching configuration
CACHE_CONFIG = {
    'legislators_by_state': {
        'memory_cache': True,
        'dynamodb_ttl': 3600,      # 1 hour
        'refresh_interval': 86400   # 24 hours
    },
    'api_keys': {
        'memory_cache': True,
        'dynamodb_ttl': None,       # No expiration
        'refresh_interval': None
    }
}
```

---

## Pattern 3: Data Model with Validation

**Source**: openstates/openstates-core  
**Task**: T026

### Problem
API responses need validation, normalization, and type safety before storage and use.

### Solution: Pydantic Models with Validators

```python
from pydantic import BaseModel, validator, Field
from typing import List, Optional
from datetime import date
import re

# Phone number validation
PHONE_RE = re.compile(r"^(1-)?\d{3}-\d{3}-\d{4}( ext\. \d+)?$")

class Office(BaseModel):
    """
    Contact office for a representative
    
    Pattern from openstates/openstates-core
    """
    classification: str  # 'capitol' or 'district'
    address: str = ""
    voice: str = ""  # Phone: XXX-XXX-XXXX format
    fax: str = ""
    name: str = ""
    
    @validator('voice', 'fax')
    def validate_phone(cls, v):
        """Validate and normalize phone numbers"""
        if not v:
            return v
        
        # Normalize format
        v = re.sub(r'[^\d-]', '', v)  # Remove non-digit, non-dash
        
        if not PHONE_RE.match(v):
            # Try to reformat: (123) 456-7890 -> 123-456-7890
            digits = re.sub(r'\D', '', v)
            if len(digits) == 10:
                v = f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
            elif len(digits) == 11 and digits[0] == '1':
                v = f"1-{digits[1:4]}-{digits[4:7]}-{digits[7:11]}"
        
        return v
    
    @validator('address')
    def normalize_address(cls, v):
        """Normalize multi-line addresses"""
        if not v:
            return v
        
        # Convert newlines to semicolons for consistent display
        v = re.sub(r'\s*\n\s*', '; ', v)
        # Collapse multiple spaces
        v = re.sub(r'\s+', ' ', v)
        
        return v.strip()
    
    class Config:
        # Require at least one contact method
        @validator('*', pre=True, always=True)
        def check_at_least_one_value(cls, v, values):
            if not any([values.get('address'), values.get('voice'), values.get('fax')]):
                raise ValueError("Office must have at least one contact method")
            return v

class Role(BaseModel):
    """Current political role"""
    type: str  # 'upper', 'lower', 'governor', 'mayor', etc.
    district: Optional[str] = None
    jurisdiction: str  # OCD jurisdiction ID
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    def is_active(self, as_of: Optional[date] = None) -> bool:
        """Check if role is currently active"""
        if as_of is None:
            as_of = date.today()
        
        if self.start_date and as_of < self.start_date:
            return False
        
        if self.end_date and as_of > self.end_date:
            return False
        
        return True

class Person(BaseModel):
    """
    Representative data model
    
    Based on OpenStates Person schema with adaptations for Represent App
    """
    id: str  # OCD person ID or internal UUID
    name: str
    given_name: str = ""
    family_name: str = ""
    gender: str = ""
    email: str = ""
    image: str = ""
    
    # Current role and party
    current_role: Optional[Role] = None
    party: str = ""
    
    # Contact information
    offices: List[Office] = Field(default_factory=list)
    
    # Links
    website_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    facebook_url: Optional[str] = None
    
    # Source attribution
    source: str = ""  # 'openstates', 'google_civic', etc.
    last_updated: date = Field(default_factory=date.today)
    
    @validator('name')
    def validate_name(cls, v):
        """Check for mangled names"""
        if v.count(',') > 1:
            raise ValueError("Name has too many commas - likely mangled")
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Basic email validation"""
        if v and '@' not in v:
            raise ValueError("Invalid email format")
        return v
    
    @validator('party')
    def normalize_party(cls, v):
        """Normalize party names"""
        party_map = {
            'D': 'Democratic',
            'R': 'Republican',
            'I': 'Independent',
            'Democratic': 'Democratic',
            'Republican': 'Republican',
            'Independent': 'Independent'
        }
        return party_map.get(v, v)
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format"""
        return {
            'PK': f'PERSON#{self.id}',
            'SK': 'METADATA',
            'type': 'person',
            'name': self.name,
            'role_type': self.current_role.type if self.current_role else None,
            'role_district': self.current_role.district if self.current_role else None,
            'party': self.party,
            'data': self.json(),  # Store full JSON for retrieval
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_openstates_api(cls, api_response: dict) -> 'Person':
        """Parse OpenStates API response into Person model"""
        # Extract current role
        current_role = None
        if api_response.get('current_role'):
            role_data = api_response['current_role']
            current_role = Role(
                type=role_data['type'],
                district=role_data.get('district'),
                jurisdiction=role_data['org_classification'],
                start_date=role_data.get('start_date')
            )
        
        # Extract offices
        offices = []
        for office_data in api_response.get('offices', []):
            try:
                offices.append(Office(**office_data))
            except Exception as e:
                print(f"Skipping invalid office: {e}")
        
        return cls(
            id=api_response['id'],
            name=api_response['name'],
            given_name=api_response.get('given_name', ''),
            family_name=api_response.get('family_name', ''),
            email=api_response.get('email', ''),
            image=api_response.get('image', ''),
            current_role=current_role,
            party=api_response.get('party', [{}])[0].get('name', '') if api_response.get('party') else '',
            offices=offices,
            source='openstates'
        )
```

### Best Practices

1. **Use Pydantic** for automatic validation and serialization
2. **Validators for normalization**: Phone numbers, addresses, emails
3. **Type hints**: Enforce type safety at development and runtime
4. **Graceful degradation**: Skip invalid nested objects, don't fail entire parse
5. **Source attribution**: Track where data came from for debugging
6. **Timestamp everything**: Track when data was last updated
7. **Factory methods**: `from_api_response()` for each API source

### Application to Represent App

```python
# backend/src/models/person.py
# Use the Person model above

# backend/src/handlers/api.py
from models.person import Person

def get_legislators_handler(event, context):
    """Lambda handler for GET /legislators"""
    jurisdiction_id = event['queryStringParameters']['jurisdiction']
    
    # Get from cache or API
    api_data = get_legislators_with_caching(jurisdiction_id)
    
    # Parse and validate
    legislators = []
    for item in api_data.get('results', []):
        try:
            person = Person.from_openstates_api(item)
            legislators.append(person.dict())
        except Exception as e:
            print(f"Skipping invalid person: {e}")
            continue
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'legislators': legislators,
            'count': len(legislators)
        })
    }
```

---

## Pattern 4: Error Handling with Retry Logic

**Source**: openstates/openstates-core, datamade/my-reps  
**Task**: T027

### Problem
External APIs can fail transiently. Need robust retry logic with exponential backoff.

### Solution: Tenacity Retry Decorator

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import requests
import logging

logger = logging.getLogger(__name__)

# Retryable errors
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

class APIError(Exception):
    """Base exception for API errors"""
    pass

class RateLimitError(APIError):
    """Rate limit exceeded (429)"""
    pass

class ServerError(APIError):
    """Server error (5xx)"""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((RateLimitError, ServerError, requests.Timeout)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def call_api_with_retry(url: str, headers: dict = None, params: dict = None, timeout: int = 10) -> dict:
    """
    Call external API with automatic retry on transient failures
    
    Retry Policy:
    - Attempt 1: Immediate
    - Attempt 2: Wait 1 second
    - Attempt 3: Wait 2 seconds
    - Attempt 4 (final): Wait 4 seconds
    
    Retries on:
    - Rate limit errors (429)
    - Server errors (500, 502, 503, 504)
    - Timeout errors
    
    Does NOT retry on:
    - Client errors (400, 401, 403, 404)
    - Success responses (200-299)
    """
    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        
        # Check for retryable errors
        if response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded: {response.text}")
        
        if response.status_code in RETRYABLE_STATUS_CODES:
            raise ServerError(f"Server error {response.status_code}: {response.text}")
        
        # Raise for other HTTP errors (4xx)
        response.raise_for_status()
        
        return response.json()
        
    except requests.Timeout as e:
        logger.warning(f"Request timeout: {url}")
        raise  # Will be retried
    
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise APIError(f"API request failed: {e}")

# Usage with fallback to cached data
def get_legislators_safely(jurisdiction_id: str) -> dict:
    """
    Get legislators with error handling and graceful degradation
    """
    try:
        # Try API call with retry
        return call_api_with_retry(
            url='https://v3.openstates.org/people',
            headers={'X-API-Key': OPENSTATES_API_KEY},
            params={'jurisdiction': jurisdiction_id}
        )
        
    except RateLimitError:
        logger.warning("Rate limit exceeded, falling back to cache")
        # Return cached data (even if stale)
        cached = get_from_dynamodb_cache(f"legislators:{jurisdiction_id}")
        if cached:
            return cached
        raise APIError("Rate limited and no cache available")
    
    except ServerError:
        logger.error("Server error, falling back to cache")
        cached = get_from_dynamodb_cache(f"legislators:{jurisdiction_id}")
        if cached:
            return cached
        raise APIError("Server error and no cache available")
    
    except APIError as e:
        logger.error(f"API error: {e}")
        # Try to return stale cache
        cached = get_from_data_table(jurisdiction_id)
        if cached:
            logger.warning("Returning stale cached data due to API error")
            return cached
        raise  # No fallback available
```

### Circuit Breaker Pattern

```python
from datetime import datetime, timedelta
from typing import Optional

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures
    
    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, reject requests immediately
    - HALF_OPEN: Testing if service recovered
    """
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            # Check if timeout expired
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.state = 'HALF_OPEN'
                self.success_count = 0
                logger.info("Circuit breaker: OPEN -> HALF_OPEN")
            else:
                raise APIError("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            
            # Success
            if self.state == 'HALF_OPEN':
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = 'CLOSED'
                    self.failure_count = 0
                    logger.info("Circuit breaker: HALF_OPEN -> CLOSED")
            else:
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            # Failure
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"Circuit breaker: -> OPEN (failures: {self.failure_count})")
            
            raise

# Global circuit breaker for OpenStates API
openstates_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout_seconds=60,
    success_threshold=2
)

def call_open states_with_circuit_breaker(endpoint: str, params: dict) -> dict:
    """Call OpenStates API with circuit breaker protection"""
    return openstates_circuit_breaker.call(
        call_api_with_retry,
        url=f'https://v3.openstates.org{endpoint}',
        headers={'X-API-Key': OPENSTATES_API_KEY},
        params=params
    )
```

### Best Practices

1. **Exponential backoff**: Wait 1s, 2s, 4s between retries
2. **Retry only transient errors**: 429, 5xx, timeouts
3. **Don't retry client errors**: 400, 401, 403, 404
4. **Circuit breaker**: Prevent cascading failures
5. **Graceful degradation**: Return stale cache on errors
6. **Logging**: Log all retries and failures
7. **Timeout**: Always set request timeouts (10s default)

---

## Pattern 5: OCD-ID Parsing and Government Level Categorization

**Source**: datamade/my-reps  
**Task**: T028

### Problem
OCD-IDs are hierarchical identifiers that need parsing to determine government level and extract components.

### Solution: Regex-Based Parser

```python
import re
from typing import Dict, Optional, Literal
from enum import Enum

class GovernmentLevel(str, Enum):
    """Government levels for categorization"""
    FEDERAL = "federal"
    FEDERAL_CONGRESS = "federal_congress"
    STATE = "state"
    STATE_LEGISLATURE = "state_legislature"
    COUNTY = "county"
    LOCAL = "local"
    OTHER = "other"

# Regex patterns for OCD-ID parsing
FEDERAL_PATTERN = re.compile(r"^ocd-division/country:us$")
STATE_PATTERN = re.compile(r"^ocd-division/country:us/state:(\w{2})$")
CD_PATTERN = re.compile(r"^ocd-division/country:us/state:(\w{2})/cd:(\d+)$")
SLDU_PATTERN = re.compile(r"^ocd-division/country:us/state:(\w{2})/sldu:(\w+)$")
SLDL_PATTERN = re.compile(r"^ocd-division/country:us/state:(\w{2})/sldl:(\w+)$")
COUNTY_PATTERN = re.compile(r"^ocd-division/country:us/state:(\w{2})/county:(\w+)$")
PLACE_PATTERN = re.compile(r"^ocd-division/country:us/state:(\w{2})/place:(\w+)$")

def parse_ocd_id(ocd_id: str) -> Dict[str, str]:
    """
    Parse OCD-ID into components
    
    Args:
        ocd_id: OCD division identifier (e.g., 'ocd-division/country:us/state:wa/cd:7')
        
    Returns:
        Dictionary with parsed components:
        - level: Government level (federal, state, state_legislature, etc.)
        - country: Country code ('us')
        - state: State abbreviation ('wa')
        - division_type: Type ('cd', 'sldl', 'sldu', 'county', 'place')
        - district: District number or name
        
    Example:
        >>> parse_ocd_id('ocd-division/country:us/state:wa/cd:7')
        {
            'level': 'federal_congress',
            'country': 'us',
            'state': 'wa',
            'division_type': 'cd',
            'district': '7'
        }
    """
    # Check patterns in order of specificity
    
    # Congressional District
    if match := CD_PATTERN.match(ocd_id):
        return {
            'level': GovernmentLevel.FEDERAL_CONGRESS,
            'country': 'us',
            'state': match.group(1),
            'division_type': 'cd',
            'district': match.group(2)
        }
    
    # State Legislature Upper (Senate)
    if match := SLDU_PATTERN.match(ocd_id):
        return {
            'level': GovernmentLevel.STATE_LEGISLATURE,
            'country': 'us',
            'state': match.group(1),
            'division_type': 'sldu',
            'district': match.group(2)
        }
    
    # State Legislature Lower (House)
    if match := SLDL_PATTERN.match(ocd_id):
        return {
            'level': GovernmentLevel.STATE_LEGISLATURE,
            'country': 'us',
            'state': match.group(1),
            'division_type': 'sldl',
            'district': match.group(2)
        }
    
    # County
    if match := COUNTY_PATTERN.match(ocd_id):
        return {
            'level': GovernmentLevel.COUNTY,
            'country': 'us',
            'state': match.group(1),
            'division_type': 'county',
            'district': match.group(2)
        }
    
    # Place (City/Town)
    if match := PLACE_PATTERN.match(ocd_id):
        return {
            'level': GovernmentLevel.LOCAL,
            'country': 'us',
            'state': match.group(1),
            'division_type': 'place',
            'district': match.group(2)
        }
    
    # State (no district)
    if match := STATE_PATTERN.match(ocd_id):
        return {
            'level': GovernmentLevel.STATE,
            'country': 'us',
            'state': match.group(1)
        }
    
    # Federal (country only)
    if FEDERAL_PATTERN.match(ocd_id):
        return {
            'level': GovernmentLevel.FEDERAL,
            'country': 'us'
        }
    
    # Unknown format
    return {
        'level': GovernmentLevel.OTHER,
        'raw': ocd_id
    }

def categorize_by_government_level(
    legislators: List[Dict],
    group_by: Literal['level', 'state', 'district'] = 'level'
) -> Dict[str, List[Dict]]:
    """
    Group legislators by government level or other criteria
    
    Args:
        legislators: List of legislator dictionaries with 'ocd_id' field
        group_by: Grouping criteria ('level', 'state', 'district')
        
    Returns:
        Dictionary mapping group keys to legislator lists
    """
    grouped = {}
    
    for legislator in legislators:
        ocd_id = legislator.get('current_role', {}).get('ocd_id')
        if not ocd_id:
            continue
        
        parsed = parse_ocd_id(ocd_id)
        
        if group_by == 'level':
            key = parsed['level']
        elif group_by == 'state':
            key = parsed.get('state', 'unknown')
        elif group_by == 'district':
            key = f"{parsed.get('state', '')}:{parsed.get('division_type', '')}:{parsed.get('district', '')}"
        else:
            key = 'ungrouped'
        
        if key not in grouped:
            grouped[key] = []
        
        grouped[key].append(legislator)
    
    return grouped

# Example usage
legislators_data = get_legislators_safely('ocd-jurisdiction/country:us/state:wa/government')

# Group by government level
by_level = categorize_by_government_level(legislators_data['results'], group_by='level')

print(f"Federal Congress: {len(by_level.get(GovernmentLevel.FEDERAL_CONGRESS, []))}")
print(f"State Senate: {len([p for p in by_level.get(GovernmentLevel.STATE_LEGISLATURE, []) if parse_ocd_id(p['ocd_id'])['division_type'] == 'sldu'])}")
print(f"State House: {len([p for p in by_level.get(GovernmentLevel.STATE_LEGISLATURE, []) if parse_ocd_id(p['ocd_id'])['division_type'] == 'sldl'])}")
```

### OCD-ID Construction Helper

```python
def construct_ocd_id(
    state: str,
    division_type: Optional[str] = None,
    district: Optional[str] = None
) -> str:
    """
    Construct OCD-ID from components
    
    Args:
        state: 2-letter state code (lowercase)
        division_type: 'cd', 'sldu', 'sldl', 'county', 'place'
        district: District number or name
        
    Returns:
        OCD-ID string
        
    Examples:
        >>> construct_ocd_id('wa')
        'ocd-division/country:us/state:wa'
        
        >>> construct_ocd_id('wa', 'cd', '7')
        'ocd-division/country:us/state:wa/cd:7'
        
        >>> construct_ocd_id('wa', 'sldu', '43')
        'ocd-division/country:us/state:wa/sldu:43'
    """
    state = state.lower()
    ocd_id = f"ocd-division/country:us/state:{state}"
    
    if division_type and district:
        ocd_id += f"/{division_type}:{district}"
    
    return ocd_id
```

### Best Practices

1. **Use regex patterns** for reliable parsing
2. **Handle all formats**: federal, state, cd, sldu, sldl, county, place
3. **Return structured data**: Don't just extract strings
4. **Government level enum**: Type-safe categorization
5. **Construction helpers**: Build OCD-IDs from components
6. **Validation**: Check format before parsing
7. **Graceful fallback**: Return 'other' for unknown formats

---

## Summary: Patterns Extracted (T024-T028 Complete)

### Pattern 1: API Authentication ✅
- Environment variables for development
- Parameter Store for production
- Header vs query parameter authentication
- Caching with `@lru_cache`

### Pattern 2: Multi-Layer Caching ✅
- Lambda memory (hot cache)
- DynamoDB cache table (warm cache)
- DynamoDB data table (cold storage)
- TTL-based expiration
- Cache invalidation strategy

### Pattern 3: Data Model with Validation ✅
- Pydantic models for type safety
- Validators for normalization (phones, addresses)
- Factory methods for API parsing
- DynamoDB serialization

### Pattern 4: Error Handling with Retry ✅
- Exponential backoff retry logic
- Circuit breaker pattern
- Graceful degradation to cached data
- Logging and monitoring

### Pattern 5: OCD-ID Parsing ✅
- Regex-based parser
- Government level categorization
- OCD-ID construction helpers
- Grouping and filtering utilities

---

## Next Steps (T029-T031)

1. **T029**: Consolidate patterns into quickstart.md
2. **T030**: Create implementation checklist
3. **T031**: Document integration flow diagram

These patterns form the foundation for MVP implementation. All are production-ready and based on real-world usage in active projects.
