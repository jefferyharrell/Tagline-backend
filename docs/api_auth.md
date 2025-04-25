# Tagline API Authentication & Error Handling Guide

Welcome, future Tagline devs (and our own forgetful selves)! This doc explains how authentication works in the Tagline backend, how to interact with protected endpoints, and what error responses you can expect. Everything here is up-to-date as of 2025-04-25.

---

## Authentication Flow

### 1. Login: Obtain Access & Refresh Tokens
- **Endpoint:** `POST /login`
- **Request Body:**
  ```json
  {
    "password": "<your-backend-password>"
  }
  ```
- **Success Response:**
  ```json
  {
    "access_token": "<JWT>",
    "refresh_token": "<JWT>"
  }
  ```
- **Error Responses:**
  - `401 Unauthorized` for wrong password
  - `422 Unprocessable Entity` for missing/invalid payload

### 2. Use the Access Token
- For all protected endpoints, include this header:
  ```
  Authorization: Bearer <access_token>
  ```
- Access tokens are short-lived (see backend config for expiry time).

### 3. Refresh Tokens
- **Endpoint:** `POST /refresh`
- **Request Body:**
  ```json
  {
    "refresh_token": "<your-refresh-token>"
  }
  ```
- **Success Response:**
  ```json
  {
    "access_token": "<new-access-token>",
    "refresh_token": "<new-refresh-token>"
  }
  ```
- **Error Responses:**
  - `401 Unauthorized` for invalid/expired refresh token
  - `422 Unprocessable Entity` for missing/invalid payload

### 4. Logout (Token Invalidation)
- **NOT YET IMPLEMENTED** for MVP. Tokens naturally expire. If/when implemented, logout will blacklist the refresh token.

---

## Protected Endpoints
All core photo API endpoints require a valid access token:
- `GET /photos`
- `GET /photos/{id}`
- `GET /photos/{id}/image`
- `PATCH /photos/{id}/metadata`

You must include the `Authorization: Bearer <access_token>` header.

---

## Error Responses: What to Expect

### Auth & Token Issues
- **401 Unauthorized**: Missing or invalid access/refresh token, or wrong password.
  ```json
  { "detail": "Not authenticated" }
  ```
- **403 Forbidden**: Token present but user not authorized (should not happen in MVP, but may occur in future multi-user version).
- **422 Unprocessable Entity**: Malformed request body or missing required fields.
  ```json
  { "detail": "...' } // message depends on the error
  ```

### Example: Expired/Invalid Token
- Response:
  ```json
  { "detail": "Could not validate credentials" }
  ```

### Example: Failed Login
- Response:
  ```json
  { "detail": "Incorrect password" }
  ```

---

## Example cURL Requests

### Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"password": "hunter2"}'
```

### Get Photos (with Access Token)
```bash
curl http://localhost:8000/photos \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

---

## Gotchas & Notes
- The backend expects all tokens in the `Authorization: Bearer ...` header (not as cookies).
- Access tokens expire quickly; use the refresh token to get a new one.
- Refresh tokens also expire and can be revoked (in future versions).
- Error messages are consistent and JSON-formatted.
- See [SPEC_LLM.md](../../Tagline-infra/SPEC_LLM.md) for the canonical API spec and object definitions.

---

**If you’re working on the frontend and something here doesn’t match reality, please update this doc!**
