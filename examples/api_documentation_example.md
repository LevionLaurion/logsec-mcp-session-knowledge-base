# API Documentation Example

This example shows how to organize and track API documentation using LogSec.

## Documenting a REST API

### Initial API Overview
```python
lo_save("""
# User Management API Documentation

## Base URL
`https://api.example.com/v1`

## Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer <token>
```

## Error Responses
Standard error format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

Status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
""", "userapi_docs")
```

### Endpoint Documentation
```python
lo_save("""
# User Endpoints

## GET /users
List all users with pagination

### Request
```
GET /users?page=1&limit=20&sort=created_at&order=desc
```

### Query Parameters
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 20, max: 100): Items per page
- `sort` (string, default: 'id'): Sort field
- `order` (string, default: 'asc'): Sort order (asc|desc)

### Response 200 OK
```json
{
  "data": [
    {
      "id": "123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

## POST /users
Create a new user

### Request
```json
{
  "email": "newuser@example.com",
  "password": "securePassword123!",
  "name": "Jane Smith",
  "role": "user"
}
```

### Validation Rules
- `email`: Required, valid email, unique
- `password`: Required, min 8 chars, must contain uppercase, lowercase, number
- `name`: Required, 2-100 characters
- `role`: Optional, enum ['user', 'admin'], default 'user'

### Response 201 Created
```json
{
  "id": "124",
  "email": "newuser@example.com",
  "name": "Jane Smith",
  "role": "user",
  "created_at": "2024-01-15T11:00:00Z"
}
```
""", "userapi_docs")
```

### Searching API Documentation

```python
# Find specific endpoint documentation
lo_load("userapi_docs", "POST /users validation")

# Find all error handling info
lo_load("userapi_docs", "error response status codes")

# Find authentication details
lo_load("userapi_docs", "bearer token authentication")
```

## Benefits for API Documentation

1. **Version Tracking**: Each update creates a new session
2. **Searchable**: Find endpoints by method, path, or functionality
3. **Change History**: See how API evolved over time
4. **Context Preservation**: Related endpoints stay connected
5. **Auto-Classification**: Tagged as `api_doc` type automatically
