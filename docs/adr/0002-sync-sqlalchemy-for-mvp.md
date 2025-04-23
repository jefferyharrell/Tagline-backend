# ADR 0002: Use Synchronous SQLAlchemy for MVP Database Access

## Status
Accepted

## Context
The Tagline backend requires a robust, maintainable way to interact with a relational database. SQLAlchemy is the chosen ORM. FastAPI supports both synchronous and asynchronous database access patterns. Asynchronous (async) SQLAlchemy is increasingly popular for high-concurrency applications, but comes with additional complexity and setup requirements. Synchronous (sync) SQLAlchemy is simpler to implement and is well-supported, especially for SQLite (our MVP default).

## Decision
For the MVP, we will use synchronous SQLAlchemy for all database access. This decision is based on:
- Simplicity: Sync SQLAlchemy is easier to set up and reason about, especially for contributors new to async Python.
- SQLite support: Sync access is mature and reliable with SQLite, which is our default for local development and early deployment.
- MVP needs: Expected load and concurrency are low, so sync performance is acceptable.
- Future flexibility: By confining DB logic to a data access layer, we can refactor to async in the future with moderate effort if scaling or DB backend changes require it.

## Consequences
- All database access code will use synchronous SQLAlchemy (`Session`, not `AsyncSession`).
- Route handlers and dependencies will be synchronous (`def`, not `async def`).
- If we migrate to async in the future, we will update the data access layer, session/engine setup, and dependency injection, but not the entire codebase.
- Contributors should avoid direct DB access in route handlers—always use the DAL to ease future refactoring.

---

*This decision was made in April 2025. Revisit if project requirements, expected load, or database backend change.*
