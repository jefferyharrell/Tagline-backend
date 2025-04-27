# ADR 0006: Adopt Refresh Token Flow for User Authentication

**Status:** Accepted
**Date:** 2025-04-26

## Context

Modern web applications must balance security, user experience, and flexibility in authentication. Tagline supports both browser-based and API/mobile clients. We need an auth mechanism that enables:
- Short-lived access tokens (for security)
- Long-lived sessions (for UX)
- Secure logout and token revocation
- Compatibility with browser and non-browser clients

## Decision

**Tagline will use a refresh token flow for user authentication.**

- Users receive a short-lived access token (JWT) and a long-lived refresh token (opaque or JWT) at login.
- Access tokens are used for most API calls; refresh tokens are used to obtain new access tokens when expired.
- Both tokens are stored as HttpOnly, Secure cookies in the browser (never localStorage).
- Refresh tokens are stored server-side in Redis for revocation and session management.
- The backend exposes a `/refresh` endpoint to rotate access tokens using the refresh token.
- Logout and token revocation are handled by deleting the refresh token from Redis and expiring the cookie.

## Rationale

- **Security:** Short-lived access tokens minimize risk if stolen. HttpOnly cookies prevent XSS token theft.
- **User Experience:** Long-lived refresh tokens allow seamless session renewal without frequent logins.
- **Logout/Revocation:** Refresh tokens can be revoked server-side (in Redis), instantly ending a session.
- **Flexibility:** This flow supports web, mobile, and API clients with minimal changes.
- **Industry Standard:** Mirrors best practices used by Google, Microsoft, and others for modern auth.

## Alternatives Considered

- **Session Cookie Only:** Simpler, but harder to support mobile/API clients, and less flexible for token rotation/revocation.
- **Access Token Only:** Forces frequent re-login or long expiry (less secure).
- **LocalStorage:** Vulnerable to XSS; rejected for security.

## Consequences

- Slightly more complexity in backend and frontend auth logic.
- Requires Redis or similar for refresh token storage and revocation.
- Enables secure, flexible, and scalable auth for all client types.

---

*This ADR formalizes the use of a refresh token flow for Tagline user authentication. If future requirements change, we will revisit this decision.*
