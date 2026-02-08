# GraphQL Implementation Plan (Post-MVP)

## Overview

This document outlines an implementation plan for adopting GraphQL patterns from the elect.io repository analysis. This is a **post-MVP enhancement** that will modernize the API architecture and improve frontend flexibility.

## Context from Research

From analysis of **nrenner0211/elect.io**, the following GraphQL patterns were identified:
- React + Apollo Client for frontend queries and mutations
- Apollo Server for GraphQL backend
- JWT authentication integrated with GraphQL context
- Flexible queries reducing over-fetching
- Type-safe schema with GraphQL SDL
- Mutations for address storage and user profile management

## Current Architecture (MVP)

```
React Frontend → API Gateway (REST) → Lambda (Python) → DynamoDB
```

## Target Architecture (Post-MVP with GraphQL)

```
React Frontend → API Gateway (HTTP/WebSocket) → Lambda (GraphQL Server) → DynamoDB
                     ↓
               Apollo Client                                     
```

---

## Implementation Plan

### Phase 1: Research and Design

#### 1.1 Evaluate GraphQL for Serverless
- **Objective**: Determine best approach for GraphQL in AWS Lambda
- **Tasks**:
  - Research AWS AppSync vs. self-hosted GraphQL server
  - Compare Apollo Server vs. GraphQL-Python (Graphene, Strawberry)
  - Evaluate cold start implications for GraphQL Lambda
  - Design schema to support representative queries and mutations
  
- **Decision Factors**:
  - **AWS AppSync Pros**: Managed service, built-in subscriptions, DynamoDB resolvers, automatic caching
  - **AppSync Cons**: Less flexibility, vendor lock-in, learning curve
  - **Self-hosted (Apollo) Pros**: Full control, existing ecosystem, Python integration
  - **Self-hosted Cons**: More maintenance, need to handle WebSocket for subscriptions

- **Recommendation**: Start with AWS AppSync for MVP features, migrate to self-hosted if custom requirements emerge

#### 1.2 Design GraphQL Schema
```graphql
# Representative queries
type Representative {
  id: ID!
  name: String!
  office: String!
  party: String
  divisionId: String!
  governmentLevel: GovernmentLevel!
  phones: [String!]
  emails: [String!]
  urls: [String!]
  address: Address
  channels: [SocialMediaChannel!]
  photoUrl: String
  lastUpdated: DateTime!
}

enum GovernmentLevel {
  FEDERAL
  STATE
  COUNTY
  LOCAL
}

type Address {
  line1: String
  line2: String
  city: String
  state: String
  zip: String
}

type SocialMediaChannel {
  type: String!
  id: String!
  url: String!
}

# Queries
type Query {
  # Get representatives by zip code
  representativesByZip(zipCode: String!, level: GovernmentLevel): [Representative!]!
  
  # Get specific representative by ID
  representative(id: ID!): Representative
  
  # Search representatives
  searchRepresentatives(query: String!, filters: RepresentativeFilters): [Representative!]!
  
  # User's saved addresses (requires authentication)
  myAddresses: [SavedAddress!]!
}

input RepresentativeFilters {
  governmentLevel: GovernmentLevel
  party: String
  state: String
}

# Mutations (post-MVP with user features)
type Mutation {
  # Save address to user profile
  addAddress(address: String!): SavedAddress!
  
  # Remove saved address
  removeAddress(addressId: ID!): Boolean!
  
  # Track an issue (future feature)
  trackIssue(issueId: ID!): Issue!
}

type SavedAddress {
  id: ID!
  address: String!
  zipCode: String!
  addedAt: DateTime!
  representatives: [Representative!]!
}
```

### Phase 2: Backend Implementation

#### 2.1 AWS AppSync Setup (Option A - Recommended)

**Infrastructure Changes** (`infrastructure/stacks/graphql_stack.py`):
```python
from aws_cdk import (
    Stack,
    aws_appsync as appsync,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
)

class GraphQLStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        
        # Create AppSync API
        api = appsync.GraphqlApi(
            self, "RepresentativeAPI",
            name="represent-app-api",
            schema=appsync.SchemaFile.from_asset("graphql/schema.graphql"),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.API_KEY
                ),
                additional_authorization_modes=[
                    appsync.AuthorizationMode(
                        authorization_type=appsync.AuthorizationType.USER_POOL,
                        user_pool_config=appsync.UserPoolConfig(
                            user_pool=self.user_pool
                        )
                    )
                ]
            ),
            log_config=appsync.LogConfig(
                field_log_level=appsync.FieldLogLevel.ALL
            ),
            xray_enabled=True
        )
        
        # Connect DynamoDB as data source
        representatives_ds = api.add_dynamo_db_data_source(
            "RepresentativesDataSource",
            table=self.representatives_table
        )
        
        # Create resolvers
        representatives_ds.create_resolver(
            "QueryRepresentativesByZipResolver",
            type_name="Query",
            field_name="representativesByZip",
            request_mapping_template=appsync.MappingTemplate.from_file(
                "graphql/resolvers/representativesByZip.req.vtl"
            ),
            response_mapping_template=appsync.MappingTemplate.from_file(
                "graphql/resolvers/representativesByZip.res.vtl"
            )
        )
```

**VTL Resolver Template** (`graphql/resolvers/representativesByZip.req.vtl`):
```vtl
{
  "version": "2018-05-29",
  "operation": "Query",
  "index": "ZipCodeIndex",
  "query": {
    "expression": "PK = :zipKey",
    "expressionValues": {
      ":zipKey": $util.dynamodb.toDynamoDBJson("ZIP#$ctx.args.zipCode")
    }
  }
  #if($ctx.args.level)
  ,
  "filter": {
    "expression": "governmentLevel = :level",
    "expressionValues": {
      ":level": $util.dynamodb.toDynamoDBJson($ctx.args.level)
    }
  }
  #end
}
```

#### 2.2 Python GraphQL Server with Lambda (Option B - Custom Implementation)

**Dependencies** (`backend/requirements.txt`):
```
strawberry-graphql[fastapi]==0.215.0
mangum==0.17.0  # ASGI adapter for Lambda
```

**GraphQL Server** (`backend/src/handlers/graphql_handler.py`):
```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from mangum import Mangum
from typing import List, Optional
from .resolvers import Query, Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

# Lambda handler
handler = Mangum(graphql_app, lifespan="off")
```

**Resolvers** (`backend/src/handlers/resolvers.py`):
```python
import strawberry
from typing import List, Optional
from ..models.domain import Representative
from ..models.store import RepresentativeStore

@strawberry.type
class Query:
    @strawberry.field
    def representatives_by_zip(
        self,
        zip_code: str,
        level: Optional[str] = None
    ) -> List[Representative]:
        """Get representatives by zip code"""
        store = RepresentativeStore()
        return store.get_by_zip_code(zip_code, level)
    
    @strawberry.field
    def representative(self, id: str) -> Optional[Representative]:
        """Get specific representative"""
        store = RepresentativeStore()
        return store.get(id)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_address(self, address: str, info: strawberry.Info) -> SavedAddress:
        """Save address to user profile"""
        # Validate user authentication from info.context
        user_id = info.context["user_id"]
        # Implementation here
        pass
```

### Phase 3: Frontend Integration

#### 3.1 Install Apollo Client

**Dependencies** (`frontend/package.json`):
```json
{
  "dependencies": {
    "@apollo/client": "^3.8.0",
    "graphql": "^16.8.0"
  }
}
```

#### 3.2 Configure Apollo Client

**Setup** (`frontend/src/apollo/client.js`):
```javascript
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: process.env.REACT_APP_GRAPHQL_ENDPOINT, // AppSync or Lambda URL
});

// Authentication link (for JWT or Cognito)
const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('authToken');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  };
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});

export default client;
```

**Provider Setup** (`frontend/src/index.js`):
```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloProvider } from '@apollo/client';
import client from './apollo/client';
import App from './App';

ReactDOM.render(
  <ApolloProvider client={client}>
    <App />
  </ApolloProvider>,
  document.getElementById('root')
);
```

#### 3.3 Create GraphQL Queries and Mutations

**Queries** (`frontend/src/graphql/queries.js`):
```javascript
import { gql } from '@apollo/client';

export const GET_REPRESENTATIVES_BY_ZIP = gql`
  query GetRepresentativesByZip($zipCode: String!, $level: GovernmentLevel) {
    representativesByZip(zipCode: $zipCode, level: $level) {
      id
      name
      office
      party
      governmentLevel
      phones
      emails
      urls
      photoUrl
      channels {
        type
        id
        url
      }
    }
  }
`;

export const GET_MY_ADDRESSES = gql`
  query GetMyAddresses {
    myAddresses {
      id
      address
      zipCode
      representatives {
        id
        name
        office
      }
    }
  }
`;
```

**Mutations** (`frontend/src/graphql/mutations.js`):
```javascript
import { gql } from '@apollo/client';

export const ADD_ADDRESS = gql`
  mutation AddAddress($address: String!) {
    addAddress(address: $address) {
      id
      address
      zipCode
      addedAt
    }
  }
`;
```

#### 3.4 Update React Components

**Representative Lookup Component** (`frontend/src/components/RepLookup.jsx`):
```javascript
import React, { useState } from 'react';
import { useQuery } from '@apollo/client';
import { GET_REPRESENTATIVES_BY_ZIP } from '../graphql/queries';
import { TextField, Button, CircularProgress, Alert } from '@mui/material';
import RepCard from './RepCard';

export default function RepLookup() {
  const [zipCode, setZipCode] = useState('');
  const [level, setLevel] = useState(null);
  
  const { loading, error, data, refetch } = useQuery(
    GET_REPRESENTATIVES_BY_ZIP,
    {
      variables: { zipCode, level },
      skip: !zipCode, // Don't query until zip code entered
    }
  );
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (zipCode) {
      refetch({ zipCode, level });
    }
  };
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Enter Zip Code"
          value={zipCode}
          onChange={(e) => setZipCode(e.target.value)}
          variant="outlined"
        />
        <Button type="submit" variant="contained">
          Find Representatives
        </Button>
      </form>
      
      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error.message}</Alert>}
      
      {data?.representativesByZip && (
        <div>
          {data.representativesByZip.map(rep => (
            <RepCard key={rep.id} representative={rep} />
          ))}
        </div>
      )}
    </div>
  );
}
```

**Save Address Component** (`frontend/src/components/SaveAddress.jsx`):
```javascript
import React from 'react';
import { useMutation } from '@apollo/client';
import { ADD_ADDRESS } from '../graphql/mutations';
import { GET_MY_ADDRESSES } from '../graphql/queries';
import { Button } from '@mui/material';

export default function SaveAddress({ address }) {
  const [addAddress, { loading, error }] = useMutation(ADD_ADDRESS, {
    refetchQueries: [{ query: GET_MY_ADDRESSES }],
  });
  
  const handleSave = async () => {
    try {
      await addAddress({ variables: { address } });
      alert('Address saved successfully!');
    } catch (err) {
      console.error('Error saving address:', err);
    }
  };
  
  return (
    <Button
      onClick={handleSave}
      disabled={loading}
      variant="outlined"
    >
      {loading ? 'Saving...' : 'Save Address'}
    </Button>
  );
}
```

### Phase 4: Authentication Integration

#### 4.1 AWS Cognito Setup (if using AppSync)
```python
# In infrastructure stack
user_pool = cognito.UserPool(
    self, "UserPool",
    user_pool_name="represent-app-users",
    self_sign_up_enabled=True,
    sign_in_aliases=cognito.SignInAliases(email=True),
    auto_verify=cognito.AutoVerifiedAttrs(email=True),
)

user_pool_client = user_pool.add_client(
    "AppClient",
    auth_flows=cognito.AuthFlow(user_password=True, user_srp=True),
)
```

#### 4.2 JWT Integration (if self-hosted)
- Implement JWT verification in GraphQL context
- Use patterns from elect.io's `utils/auth.js`
- Store tokens in localStorage or httpOnly cookies

### Phase 5: Testing

#### 5.1 Backend Tests
```python
# tests/unit/test_graphql_resolvers.py
import pytest
from strawberry.test import BaseGraphQLTestClient

def test_representatives_by_zip():
    query = """
        query {
            representativesByZip(zipCode: "94102") {
                id
                name
                office
            }
        }
    """
    result = client.query(query)
    assert not result.errors
    assert len(result.data["representativesByZip"]) > 0
```

#### 5.2 Frontend Tests
```javascript
// tests/RepLookup.test.js
import { MockedProvider } from '@apollo/client/testing';
import { render, screen } from '@testing-library/react';
import RepLookup from '../components/RepLookup';
import { GET_REPRESENTATIVES_BY_ZIP } from '../graphql/queries';

const mocks = [
  {
    request: {
      query: GET_REPRESENTATIVES_BY_ZIP,
      variables: { zipCode: '94102' },
    },
    result: {
      data: {
        representativesByZip: [
          { id: '1', name: 'John Doe', office: 'Senator' },
        ],
      },
    },
  },
];

test('renders representatives', async () => {
  render(
    <MockedProvider mocks={mocks}>
      <RepLookup />
    </MockedProvider>
  );
  // Test implementation
});
```

---

## Decision Points

### When to Implement GraphQL?

**Implement GraphQL when:**
- ✅ MVP is complete and stable
- ✅ REST API patterns are well-established
- ✅ Frontend requires more flexible queries
- ✅ Over-fetching/under-fetching becomes a problem
- ✅ Team has GraphQL expertise or capacity to learn
- ✅ User features (saved addresses, tracked issues) are planned

**Delay GraphQL if:**
- ❌ MVP is not yet complete
- ❌ Team lacks GraphQL experience and has tight deadlines
- ❌ REST API adequately serves current needs
- ❌ Simple CRUD operations are the only requirement

### AppSync vs. Self-Hosted?

**Choose AppSync if:**
- Want managed service with less operational overhead
- Need real-time subscriptions (WebSocket) easily
- DynamoDB is primary data source
- Willing to learn VTL for resolvers
- Cost is acceptable (pay per query)

**Choose Self-Hosted if:**
- Need maximum flexibility and control
- Want to avoid vendor lock-in
- Complex business logic in resolvers
- Existing Python expertise (use Strawberry/Graphene)
- Prefer code-based resolvers over VTL

---

## Migration Strategy

### Incremental Migration (Recommended)

1. **Phase 1**: Keep REST API operational
2. **Phase 2**: Deploy GraphQL alongside REST (dual endpoints)
3. **Phase 3**: Migrate frontend components one-by-one to GraphQL
4. **Phase 4**: Deprecate REST endpoints once all clients migrated
5. **Phase 5**: Remove REST code

### Benefits:
- No disruption to existing users
- Test GraphQL in production gradually
- Rollback capability if issues arise
- Team can learn GraphQL without pressure

---

## Performance Considerations

### GraphQL-Specific Optimizations

1. **Query Complexity Limits**: Prevent expensive nested queries
2. **DataLoader Pattern**: Batch and cache database queries
3. **Persisted Queries**: Reduce payload size for repeated queries
4. **Field-Level Caching**: Cache individual fields with different TTLs
5. **Lambda Cold Starts**: Optimize GraphQL server size, use provisioned concurrency

### Monitoring
- Track query execution time per field
- Monitor resolver performance
- Set alerts for slow queries (>3s)
- Use X-Ray for distributed tracing

---

## Cost Analysis

### AWS AppSync Pricing (Estimated)
- $4.00 per million queries/mutations
- $0.08 per million real-time updates
- Free tier: 250,000 queries per month

### Comparison with REST + Lambda
- REST: Pay per Lambda invocation + API Gateway requests
- GraphQL: Pay per GraphQL operation + Lambda execution
- **Verdict**: Similar costs, GraphQL potentially more efficient with batched queries

---

## Success Criteria

GraphQL implementation is successful when:
- ✅ All REST features available via GraphQL
- ✅ Frontend can query representatives flexibly (by zip, level, party, etc.)
- ✅ Mutations work for user features (save address, track issues)
- ✅ Authentication integrated (Cognito or JWT)
- ✅ Query performance meets SLA (<3s)
- ✅ Test coverage >80% for resolvers
- ✅ Documentation complete (schema, queries, mutations)
- ✅ Zero downtime during migration from REST

---

## Resources

- **elect.io Repository**: https://github.com/nrenner0211/elect.io (React + GraphQL reference)
- **AWS AppSync Docs**: https://docs.aws.amazon.com/appsync/
- **Apollo Client**: https://www.apollographql.com/docs/react/
- **Strawberry GraphQL**: https://strawberry.rocks/ (Python GraphQL library)
- **GraphQL Best Practices**: https://graphql.org/learn/best-practices/

---

## Timeline Estimate

- **Phase 1 (Research)**: 1 week
- **Phase 2 (Backend)**: 2-3 weeks
- **Phase 3 (Frontend)**: 2 weeks
- **Phase 4 (Auth)**: 1 week
- **Phase 5 (Testing)**: 1 week

**Total**: 7-8 weeks for full GraphQL implementation

---

## Conclusion

GraphQL adoption should be considered **post-MVP** once the core REST API is stable and user features (saved addresses, tracked issues) are planned. The recommended approach is **AWS AppSync** for managed simplicity, with migration planned incrementally to avoid disruption. The patterns from elect.io provide a solid reference for React + Apollo integration.
