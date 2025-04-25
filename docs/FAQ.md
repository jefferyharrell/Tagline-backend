# Tagline Backend FAQ

Welcome to the place where we answer the questions we ask ourselves (so we don’t have to ask them again).

---

## Why doesn’t `/refresh` require an access token?

Because the whole point of `/refresh` is to get a new access token when the old one is expired or missing! `/refresh` authenticates using the refresh token in the request body. If we required an access token, you’d be locked out when it expires—which is exactly when you need to refresh. This is standard practice for token-based auth APIs.

## Where do I find the canonical API spec?

See [`Tagline-infra/SPEC_LLM.md`](../../Tagline-infra/SPEC_LLM.md). This is the single source of truth for all API endpoints, objects, and expected behaviors. If the backend or frontend ever disagrees with this file, the spec wins (unless we update it).

## What’s the difference between a unit, integration, and E2E test in this project?

- **Unit tests:** Mock all external dependencies, test code in isolation, fast. Located in `tests/unit/`.
- **Integration tests:** Use real implementations for most dependencies (e.g., real DB, real storage), minimal mocking. Located in `tests/integration/`.
- **E2E tests:** Require a real backend server (usually via Docker Compose), no mocking, interact over HTTP, simulate real-world usage. Located in `tests/e2e/`.

For more, see [`tests/README.md`](../tests/README.md).

## Why is all photo metadata inside a `metadata` dictionary instead of top-level fields?

Because the canonical spec ([SPEC_LLM.md](../../Tagline-infra/SPEC_LLM.md)) says so! This makes the API easier to evolve (we can add new metadata fields without breaking clients) and keeps the contract clean.

## What’s the deal with logout/invalidate refresh tokens?

As of MVP, logout isn’t implemented. Refresh tokens naturally expire, and you can’t use an expired one. If/when we add logout, it’ll work by blacklisting the refresh token. (See open roadmap item in `STATUS.md`.)

---

*Add more questions as you go! If you find yourself asking “why did we do it this way?”—this is the place to answer it.*
