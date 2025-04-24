# ADR 0005: Dropbox Storage Provider — SDK vs HTTP API

**Status:** Accepted
**Date:** 2025-04-24

## Context

Tagline's backend must support Dropbox as a first-class, production-ready storage provider for photo blobs. Dropbox offers both an official Python SDK (`dropbox` package) and a RESTful HTTP API. We need to choose the right integration path for maintainability, reliability, and developer experience.

## Decision

**We will use the official Dropbox Python SDK (`dropbox` package) for all Dropbox integration in the backend, unless a critical feature is unavailable in the SDK and only accessible via the HTTP API.**

- The SDK is mature, well-documented, and covers all core file operations, authentication, and error handling.
- It supports service-account flows: a single admin can authorize Tagline with a long-lived refresh token (no end-user Dropbox login required).
- The SDK handles token refresh, chunked uploads/downloads, pagination, and common edge cases automatically.
- Pythonic API: returns objects, raises exceptions, and integrates cleanly with modern Python code.
- Using the SDK minimizes boilerplate and risk of subtle HTTP bugs.
- If a future requirement is not supported by the SDK, we may implement that specific call using the HTTP API as a fallback, but this is not expected for MVP.

## Consequences

- Tagline's Dropbox storage provider will depend on the `dropbox` PyPI package.
- The backend will require Dropbox app credentials and a refresh token (see README and .env.example for setup).
- All Dropbox API interactions will use the SDK unless a strong technical reason forces direct HTTP use.
- This ADR will be referenced in code, documentation, and onboarding materials.

## Alternatives Considered

- **Raw HTTP API:** More control, but more boilerplate, error-prone, and unnecessary for our use case.
- **Hybrid:** Only use HTTP for features missing in the SDK (if ever needed).

## References
- [Dropbox Python SDK Docs](https://dropbox-sdk-python.readthedocs.io/en/latest/)
- [Dropbox HTTP API Docs](https://www.dropbox.com/developers/documentation/http/documentation)
- [Dropbox OAuth Guide](https://developers.dropbox.com/oauth-guide)

---

*This ADR formalizes our commitment to the official Dropbox Python SDK for Tagline's Dropbox storage provider. If the SDK ever becomes a blocker, we will revisit this decision.*
