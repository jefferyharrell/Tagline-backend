# Migration Plan: API Key Authentication for Tagline Backend

This document tracks the migration from cookie/refresh token authentication to API key authentication for the Tagline backend.

---

## Checklist

### 1. API Key Generation
- [x] Add a script to generate secure API keys (`generate_api_key.py`).
- [x] Document key storage best practices (secrets manager, `.env`, **never** in frontend).

### 2. Backend Changes
- [x] Add API key to backend config (env var: `TAGLINE_API_KEY`).
- [x] Implement FastAPI dependency to require/check API key in `x-api-key` header.
- [x] Apply API key dependency to all protected endpoints.
- [ ] Remove all cookie/token auth logic:
    - [x] Delete login, refresh, logout endpoints
    - [x] Remove token store, Redis token logic, and related settings
    - [x] Remove `AuthService` and related code
    - [x] Clean up tests and fixtures
- [x] Update OpenAPI docs to reflect API key scheme. *(Handled by FastAPI based on `verify_api_key` dependency)*
- [x] Update error responses for unauthorized access. *(Handled by `verify_api_key` dependency)*
- [x] Test API key functionality:
    - [x] Unauthorized access (missing key) returns 401.
    - [x] Unauthorized access (invalid key) returns 403.
    - [x] Valid API key allows access to protected endpoints.

### 3. Frontend Changes
- [ ] Update API client to send `x-api-key` header with all requests.
- [ ] Remove any frontend logic related to cookies/tokens.

### 4. Infra & DevOps
- [ ] Add API key to `.env` and Docker Compose configs.
- [ ] Add Justfile shortcut to generate API key (`just generate-api-key`).
- [ ] Document deployment/rotation instructions.

### 5. Docs & Communication
- [ ] Update backend README and relevant docs to explain new auth scheme.
- [ ] Add a warning about never exposing the API key to client-side code.
- [ ] Update ADRs/specs as needed.

### 6. Testing & Validation
- [ ] Add/Update tests for API key auth (unit/integration/e2e).
- [ ] Validate all endpoints are protected as intended.
- [ ] Verify OpenAPI contract matches implementation.

---

## Notes
- This checklist should be updated as the migration progresses.
- If you spot auth code or docs that aren’t covered here, add them!

---

Let’s do this. 🔥
