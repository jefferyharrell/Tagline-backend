# ADR 0003: Store SQLite Database on a Docker Volume

## Status
Accepted

## Context

The Tagline backend is deployed as a Docker container using SQLite for persistent storage during the MVP phase. By default, data written to a container's filesystem is ephemeral and will be lost when the container is rebuilt, updated, or removed. To ensure data durability across deployments and upgrades, we need a strategy for persisting the SQLite database file.

## Decision

- The SQLite database file (`tagline.db`) will be stored in the `/data` directory inside the container.
- The `/data` directory will be mapped to a named Docker volume (`tagline-db-data`) via `docker-compose.yml`.
- The `DATABASE_URL` environment variable is set to `sqlite:////data/tagline.db` to ensure the app writes to the correct location.
- This configuration is documented in `docker-compose.yml` and the backend README.

## Consequences

- Data in the SQLite database will persist across container rebuilds, restarts, and upgrades.
- Developers and operators do not need to worry about accidental data loss due to ephemeral container filesystems.
- The volume can be backed up, inspected, or migrated as needed using standard Docker tooling.
- If/when the project migrates to a different database (e.g., Postgres), the same principle applies: persistent data must live outside the container's ephemeral filesystem.

## References
- [docker-compose.yml](../../docker-compose.yml)
- [README.md](../../README.md)

---

*This decision was made in April 2025. Revisit if the deployment architecture or database technology changes.*
