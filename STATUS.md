# Backend Development Status

This document tracks the progress of the Tagline backend (FastAPI) implementation. Each milestone below represents a major step toward a robust, production-ready API.

## Current Status

- [x] Set up CI for automated testing
- [x] Scaffold minimal FastAPI application
- [ ] Implement core API endpoints
    - [ ] POST /login — Authenticate, get tokens
        - [ ] Define `LoginRequest` and `LoginResponse` models
        - [ ] Add validation for login payload (password required, type)
        - [ ] Unit test: valid/invalid login payloads
        - [ ] E2E test: endpoint behavior
    - [ ] POST /refresh — Get new access token
        - [ ] Define `RefreshRequest` and `RefreshResponse` models
        - [ ] Add validation for refresh payload (refresh_token required, type)
        - [ ] Unit test: valid/invalid refresh payloads
        - [ ] E2E test: endpoint behavior
    - [ ] GET /photos — List photo IDs (paginated)
        - [ ] Define `PhotoListResponse` model
        - [ ] Add validation for query params (limit, offset)
        - [ ] Unit test: valid/invalid pagination params
        - [ ] E2E test: endpoint behavior
    - [ ] GET /photos/{id} — Get photo + metadata
        - [ ] Define `Photo` model
        - [ ] Add validation for path param (UUID format)
        - [ ] Unit test: valid/invalid photo ID
        - [ ] E2E test: endpoint behavior
    - [ ] PATCH /photos/{id}/metadata — Update metadata (description)
        - [ ] Define `UpdateMetadataRequest` model
        - [ ] Add validation for description and last_modified
        - [ ] Unit test: valid/invalid metadata payloads
        - [ ] E2E test: endpoint behavior
    - [ ] GET /photos/{id}/image — Get image file
        - [ ] Define response model or headers (content-type, etc.)
        - [ ] Add validation for path param (UUID format)
        - [ ] Unit test: valid/invalid photo ID
        - [ ] E2E test: endpoint behavior
    - [ ] POST /rescan — Scan storage, import new photos
        - [ ] Define response model if needed
        - [ ] Validate triggering conditions
        - [ ] Unit test: endpoint behavior
        - [ ] E2E test: endpoint behavior
- [ ] Add authentication and authorization
    - [ ] Design and implement refresh token store for revocation
        - [ ] Choose storage backend (in-memory, file, or database)
        - [ ] Store issued refresh tokens with status/expiration
        - [ ] Check token validity on each refresh
        - [ ] Implement revocation (blacklist/delete)
        - [ ] Unit test: token issuance, validation, revocation
        - [ ] E2E test: revoked token cannot be used
    - [ ] Implement password-based authentication
        - [ ] Add `BACKEND_PASSWORD` to environment/config
        - [ ] Create Pydantic model for login request/response
        - [ ] Implement `/login` endpoint to verify password and issue tokens
        - [ ] Unit test: correct and incorrect password
        - [ ] E2E test: login flow
    - [ ] Implement JWT access and refresh tokens
        - [ ] Generate short-lived access tokens (JWT)
        - [ ] Generate long-lived refresh tokens (JWT)
        - [ ] Store JWT secret in env/config
        - [ ] Add token expiration and refresh logic
        - [ ] Unit test: token creation/validation/expiration
        - [ ] E2E test: token usage and refresh
    - [ ] Protect endpoints with authentication
        - [ ] Require access token for all protected endpoints
        - [ ] Implement token validation in FastAPI dependencies
        - [ ] Return 401/403 for missing/invalid tokens
        - [ ] Unit test: unauthorized access
        - [ ] E2E test: endpoint protection
- [ ] Implement logout/invalidate refresh tokens (optional for MVP)
    - [ ] Add refresh token blacklist or revocation mechanism (if needed)
    - [ ] Unit/E2E test: revoked token cannot be used
- [ ] Document authentication flow and error responses
- [ ] Add file storage for photos
- [ ] Integrate persistent storage (database)
- [ ] Add API documentation and OpenAPI schema customizations
- [ ] Improve error handling and logging
- [ ] Performance and security review
- [ ] Production readiness checklist

## Last Updated
2025-04-22

---

Want to help? See the project spec in `infra/SPEC.md` for details and priorities.
