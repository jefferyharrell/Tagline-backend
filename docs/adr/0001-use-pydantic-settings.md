# ADR 0001: Use Pydantic BaseSettings for Configuration

## Status
Accepted

## Context
We need a robust, maintainable way to manage environment-based configuration (e.g., database connection strings, secrets, feature flags) in the Tagline backend. Historically, Python projects have used `python-dotenv` or direct `os.environ` calls, but these approaches have limitations in type safety, structure, and testability.

## Decision
We will use [Pydantic](https://docs.pydantic.dev/latest/usage/settings/) `BaseSettings` for all backend configuration. This approach allows us to:
- Define all config variables in one place with types and defaults.
- Load values from environment variables and `.env` files automatically.
- Document config options and defaults in code.
- Easily extend and test configuration.

## Consequences
- All config is centralized, type-checked, and self-documenting.
- `.env` files are supported for local development, but not required in production.
- Future config changes (adding/removing variables) are explicit and easy to review.
- Contributors should use `from app.config import settings` instead of `os.environ` or `python-dotenv` directly.

---

*This decision was made in April 2025. Revisit if project requirements or Python ecosystem best practices change.*
