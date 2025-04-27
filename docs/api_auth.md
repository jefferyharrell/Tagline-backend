# Tagline API Authentication & Error Handling Guide

Welcome, future Tagline devs (and our own forgetful selves)! This doc explains how authentication works in the Tagline backend, how to interact with protected endpoints, and what error responses you can expect. Everything here is up-to-date as of 2025-04-25.

---

## Authentication Flow

### 1. Login: Obtain Auth Cookies
- **Endpoint:** `POST /login`
- **Request Body:**
  ```json
  {
    "password": "<your-backend-password>"
  }
  ```
- **Success Response:**
  - Sets `tagline_access_token` and `tagline_refresh_token` cookies (HTTP-only, path=/).
  - Returns:
    ```json
    { "detail": "Login successful" }
    ```
- **Error Responses:**
  - `401 Unauthorized` for wrong password
  - `422 Unprocessable Entity` for missing/invalid payload

### 2. Use the Access Token Cookie
- For all protected endpoints, the backend will read your `tagline_access_token` cookie automatically (no need to set Authorization headers).
- Access tokens are short-lived (see backend config for expiry time).
- If your cookie is missing or expired, you’ll get a 401 error.

### 3. Refresh Tokens
- **Endpoint:** `POST /refresh`
- **How it works:**
  - If you have a `tagline_refresh_token` cookie, it will be used automatically (no need to send in the body).
  - You may also send `{ "refresh_token": "..." }` in the request body if not using cookies (e.g., API clients, tests).
- **Success Response:**
  - Sets new `tagline_access_token` and `tagline_refresh_token` cookies.
  - Returns:
    ```json
    { "detail": "Token refreshed successfully" }
    ```
- **Error Responses:**
  - `401 Unauthorized` for invalid/expired refresh token
  - `422 Unprocessable Entity` for missing/invalid payload

### 4. Logout (Token Invalidation)
- **Endpoint:** `POST /logout`
- **How it works:**
  - Clears both `tagline_access_token` and `tagline_refresh_token` cookies.
  - Returns:
    ```json
    { "detail": "Successfully logged out" }
    ```
- **Note:** Blacklisting/revocation is not implemented for MVP. Tokens naturally expire.

---

## Protected Endpoints
All core photo API endpoints require a valid access token:
- `GET /photos`
- `GET /photos/{id}`
- `GET /photos/{id}/image`
- `PATCH /photos/{id}/metadata`

You do NOT need to include Authorization headers. The backend reads your cookies automatically.

---

## Error Responses: What to Expect

### Auth & Token Issues
- **401 Unauthorized**: Missing or invalid access/refresh token, or wrong password.
  ```json
  { "detail": "Missing authentication token" }
  ```
- **403 Forbidden**: Token present but user not authorized (should not happen in MVP, but may occur in future multi-user version).
- **422 Unprocessable Entity**: Malformed request body or missing required fields.
  ```json
  { "detail": "...' } // message depends on the error
  ```

### Example: Expired/Invalid Token
- Response:
  ```json
  { "detail": "Invalid or expired token" }
  ```

### Example: Failed Login
- Response:
  ```json
  { "detail": "Invalid password" }
  ```

---

## Example cURL Requests

### Login
```bash
curl -i -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"password": "hunter2"}'
# Cookies will be set in the response (see Set-Cookie headers)
```

### Get Photos (with Access Token Cookie)
```bash
curl -i http://localhost:8000/photos \
  --cookie "tagline_access_token=<your-access-token>"
# Or, if you have cookies saved from login, curl will send them automatically
```

### Refresh Token (with Cookie)
```bash
curl -i -X POST http://localhost:8000/refresh \
  --cookie "tagline_refresh_token=<your-refresh-token>"
# If you have the cookie set, you can omit the body entirely
```

---

## Gotchas & Notes
- The backend expects all tokens as HTTP-only cookies (`tagline_access_token`, `tagline_refresh_token`).
- Access tokens expire quickly; use the refresh token (cookie) to get a new one.
- Refresh tokens also expire and can be revoked (in future versions).
- Error messages are consistent and JSON-formatted.
- Cookies are set with `httponly` and `samesite=lax` for security and UX (see backend source for details).
- See [SPEC_LLM.md](../../Tagline-infra/SPEC_LLM.md) for the canonical API spec and object definitions.

---

**If you’re working on the frontend and something here doesn’t match reality, please update this doc!**
