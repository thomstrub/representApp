# API Key Registration Instructions

**Feature**: API Integration Research  
**Phase**: 1 - Setup  
**Date**: 2026-02-07

## Required Actions for T001-T003

To complete Phase 1 and unblock Phase 2 research, you need to register for API keys and store them securely.

### T001: Register for Google Civic Information API Key

**Steps**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing project
3. Navigate to "APIs & Services" → "Library"
4. Search for "Google Civic Information API"
5. Click "Enable"
6. Navigate to "APIs & Services" → "Credentials"
7. Click "Create Credentials" → "API Key"
8. (Recommended) Restrict the API key:
   - Click on the API key to edit
   - Under "API restrictions", select "Restrict key"
   - Select "Google Civic Information API"
   - Under "Application restrictions", select "IP addresses" (if testing from fixed location) or leave unrestricted for development
9. Copy the API key

**Verification**:
Test the divisions endpoint with:
```bash
curl "https://www.googleapis.com/civicinfo/v2/divisions?query=1600+Pennsylvania+Ave+NW,+Washington,+DC+20500&key=YOUR_API_KEY"
```

Expected: JSON response with OCD-IDs for federal, state, and local divisions

### T002: Register for OpenStates.org API Key

**Steps**:
1. Go to [OpenStates Signup](https://openstates.org/accounts/signup/)
2. Create a free account
3. Verify your email address
4. Log in to your account
5. Navigate to your profile or API settings
6. Generate an API key
7. Note the free tier limits: 5,000 requests/day, 10 requests/second
8. Copy the API key

**Verification**:
Test the people endpoint with:
```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://v3.openstates.org/people?jurisdiction=wa&per_page=10"
```

Expected: JSON response with Washington state legislators

### T003: Store API Keys in AWS Systems Manager Parameter Store

**Prerequisites**:
- AWS CLI configured: `aws configure`
- Appropriate IAM permissions to create SSM parameters

**Steps**:

1. Store Google Civic API key:
```bash
aws ssm put-parameter \
  --name "/represent-app/api-keys/google-civic" \
  --value "YOUR_GOOGLE_API_KEY" \
  --type "SecureString" \
  --description "Google Civic Information API key for divisions endpoint" \
  --tags Key=Project,Value=RepresentApp Key=Environment,Value=Development
```

2. Store OpenStates API key:
```bash
aws ssm put-parameter \
  --name "/represent-app/api-keys/openstates" \
  --value "YOUR_OPENSTATES_API_KEY" \
  --type "SecureString" \
  --description "OpenStates.org API key for state representative data" \
  --tags Key=Project,Value=RepresentApp Key=Environment,Value=Development
```

**Verification**:
Retrieve and verify the stored keys (values will be encrypted):
```bash
# List parameters
aws ssm describe-parameters --filters "Key=Name,Values=/represent-app/api-keys/"

# Get decrypted value (for verification only)
aws ssm get-parameter --name "/represent-app/api-keys/google-civic" --with-decryption
aws ssm get-parameter --name "/represent-app/api-keys/openstates" --with-decryption
```

### Security Notes

- **Never commit API keys to git**: API keys are stored in Parameter Store, not in code
- **Use SecureString type**: Ensures keys are encrypted at rest
- **Restrict key permissions**: Limit which IAM roles can access these parameters
- **Rotate keys regularly**: Consider implementing key rotation (post-MVP)
- **Monitor usage**: Set up CloudWatch alarms for unusual API usage patterns

### Cost Considerations

- **Google Civic API**: Free tier includes 25,000 requests/day - sufficient for MVP
- **OpenStates API**: Free tier includes 5,000 requests/day - sufficient with caching
- **AWS Parameter Store**: Standard parameters are free (up to 10,000 parameters)

### Next Steps After Completion

Once you've completed T001-T003:
1. Mark tasks as complete in `tasks.md`: `- [X] T001`, `- [X] T002`, `- [X] T003`
2. Verify API access with the curl commands above
3. Proceed to Phase 2: Foundational (T005-T007) - testing the APIs programmatically

### Troubleshooting

**Google Civic API Issues**:
- Error 403: API key may be restricted incorrectly or API not enabled
- Error 400: Query parameter format issue, ensure address is URL-encoded

**OpenStates API Issues**:
- Error 401: API key invalid or not included in X-API-Key header
- Error 429: Rate limit exceeded, wait before retrying

**AWS Parameter Store Issues**:
- Access denied: Check IAM permissions for ssm:PutParameter action
- Parameter already exists: Use --overwrite flag to update existing parameter

---

**Status**: Waiting on user to complete T001-T003 before Phase 2 can begin.
