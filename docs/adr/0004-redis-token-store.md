# ADR 0004: Use Redis for Token Storage

## Status

Accepted

## Context

The Tagline backend currently uses the same relational database (RDBMS) for both application metadata (photos, users, etc.) and authentication token storage (refresh tokens, revoked tokens, etc.). This approach is simple for early development, but has several drawbacks:

- **Separation of Concerns:** Tokens are ephemeral, high-churn, and security-critical. Metadata is long-lived and business-critical. Mixing them complicates backup, scaling, and operational strategies.
- **Performance:** Token tables experience rapid insert/delete cycles, which can negatively impact RDBMS performance and bloat.
- **Security:** Isolating tokens allows for stricter access controls and easier key rotation.
- **Future Flexibility:** Using a dedicated token store makes it easier to migrate to alternative storage backends if needed.
- **Disaster Recovery:** Accidental loss or corruption of the token store should not risk application metadata.

## Decision

**We will store authentication tokens (refresh tokens, revoked tokens, etc.) in Redis, rather than the primary RDBMS.**

- In development, we will use an in-memory Redis container via Docker Compose, with no persistence.
- In production, we will use a hosted or persistent Redis service (e.g., AWS ElastiCache, Upstash, etc.) with appropriate backup and security settings.
- The backend will connect to Redis using a configurable `REDIS_URL` environment variable.
- All token-related logic (issue, check, revoke) will use Redis as the backend store.

## Consequences

- **Development:** Tokens will not survive Redis restarts in dev, which is acceptable for rapid iteration.
- **Production:** Token persistence, backup, and monitoring will be handled by the chosen Redis provider.
- **Codebase:** Token storage logic will be isolated from metadata storage, simplifying future migrations or refactors.
- **Security:** Redis can be locked down and tuned specifically for token workloads.
- **Testing:** Integration and E2E tests will use the Docker Compose Redis service.

## Alternatives Considered

- **Continue using the RDBMS:** Simple, but suboptimal for performance, security, and future flexibility.
- **Use another key-value store (e.g., Memcached, DynamoDB):** Redis is the industry standard for this use case and offers the best combination of speed, features, and ecosystem support.

## References

- [Redis documentation](https://redis.io/)
- [12 Factor App: Backing Services](https://12factor.net/backing-services)
- [ADR 0001: Use Pydantic Settings for Configuration](./0001-use-pydantic-settings.md)
- [ADR 0002: Use Sync SQLAlchemy for MVP](./0002-sync-sqlalchemy-for-mvp.md)
- [ADR 0003: Store SQLite DB on Docker Volume](./0003-store-sqlite-db-on-docker-volume.md)
