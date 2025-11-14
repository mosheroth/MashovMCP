# Mashov API Authentication Flow

Based on reverse engineering of https://web.mashov.info/students/login

## API Base URL
- **Base URL**: `https://web.mashov.info/api/`
- **Login Endpoint**: `/api/login`

## Authentication Flow

### Single-Step Authentication
- **Method**: POST
- **Endpoint**: `/api/login`
- **Payload**:
  ```json
  {
    "username": "your_username",
    "password": "your_password",
    "semel": "school_id",
    "year": "2025"
  }
  ```
- **Headers**: 
  - `Content-Type: application/json`
  
- **Response**: 
  - **Status**: 200 on success
  - **CSRF Token**: Returned in response headers as `x-csrf-token` or `X-CSRF-Token`
  - **Session Cookies**: Automatically set by the server for subsequent requests
  
- **Success Indicators** (any of these in response body):
  - `success: true`
  - `authenticated: true`
  - `token` field present
  - `accessToken` field present
  - `userSettings` object present
  - `schoolSettings` object present

### Response Structure

#### Parent Account Response
For parent accounts, the response includes an `accessToken` object with a `children` array:
```json
{
  "accessToken": {
    "children": [
      {
        "childGuid": "student-guid-here",
        "privateName": "ישראל",
        "familyName": "ישראלי",
        "classCode": "ו",
        "classNum": 1,
        "gender": "ז",
        "groups": [135, 136, ...]
      },
      ...
    ]
  }
}
```

#### Student Account Response
For student accounts, the GUID is typically at the top level:
```json
{
  "guid": "student-guid-here",
  "userSettings": { ... },
  "schoolSettings": { ... }
}
```

## Required Credentials

1. **School ID (semel)**: Unique identifier for the school
   - Can be retrieved from `GET /api/schools` endpoint
   - Required before authentication

2. **Year**: Academic year (e.g., "2025")
   - Available after school is selected

3. **Username**: Student ID or username

4. **Password**: User password

## Session Management

### HTTP Session
- Use a persistent HTTP session (e.g., `aiohttp.ClientSession`) to maintain:
  - Session cookies (automatically managed)
  - Connection pooling

### CSRF Token
- **Location**: Response header `x-csrf-token` from login response
- **Usage**: Include in all subsequent API requests as `x-csrf-token` header
- **Format**: Long string token
- **Lifetime**: Valid for the session duration

### Student GUID
- **Parent Accounts**: Extract from `accessToken.children[0].childGuid`
  - Multiple children supported
  - First child used by default
- **Student Accounts**: Extract from top-level `guid`, `studentGuid`, or `userGuid` field
- **Usage**: Required for student-specific endpoints like `/api/students/{guid}/homework`

## API Endpoints

### Authentication & User Info
- `POST /api/login` - Authenticate user
- `GET /api/schools` - List all available schools

### Student Data Endpoints
All student endpoints follow the pattern: `/api/students/{studentGuid}/{resource}`

- `GET /api/students/{guid}/homework` - Get homework assignments
- `GET /api/students/{guid}/behave` - Get behavior events (attendance, good words, etc.)
- `GET /api/students/{guid}/grades` - Get grades
- `GET /api/students/{guid}/lessons` - Get lesson history
- `GET /api/students/{guid}/groups` - Get student's groups/classes
- `GET /api/students/{guid}/timetable` - Get class schedule
- `GET /api/students/{guid}/files` - Get files
- `GET /api/students/{guid}/alfon` - Get class directory
- `GET /api/students/{guid}/maakav` - Get progress tracking info

## Error Handling

### Common Error Scenarios

1. **401 Unauthorized**
   - Session expired or invalid credentials
   - Solution: Re-authenticate with `login()`

2. **404 Not Found**
   - Invalid endpoint or student GUID
   - Note: Empty POST to `/api/login` returns 404 (not used)

3. **Invalid Credentials**
   - Response status: Usually 200 with error message in body
   - Check response body for `message` or `error` fields

### Error Response Format
```json
{
  "success": false,
  "message": "Invalid credentials",
  "error": "Authentication failed"
}
```

## Implementation Notes

### Current Python Implementation (`mashov_client.py`)

The implementation includes:

1. **Single-step authentication**:
   - Direct POST to `/api/login` with credentials
   - No initialization step needed (empty POST returns 404)

2. **Automatic CSRF token extraction**:
   - Extracted from login response headers
   - Automatically included in all subsequent requests

3. **Parent account support**:
   - Detects and stores list of children
   - Uses first child's GUID by default
   - Supports accessing data for specific children

4. **Student GUID extraction**:
   - Automatic extraction from login response
   - Searches multiple possible field names
   - Validates GUID format (UUID with dashes)

5. **Session persistence**:
   - Uses `aiohttp.ClientSession` singleton
   - Maintains cookies across requests
   - Automatic re-authentication on 401

6. **Comprehensive error handling**:
   - Multiple success indicators checked
   - Detailed debug logging
   - Informative error messages

### Usage Example

```python
from mashov_client import MashovClient

# Get singleton instance
client = MashovClient.get_instance()

# Configure credentials
client.configure(
    username="your_username",
    password="your_password",
    semel="school_id",
    year="2025"
)

# Login (happens automatically on first request)
await client.login()

# Make API requests
homework = await client.get_homework()
grades = await client.get_grades()
```

