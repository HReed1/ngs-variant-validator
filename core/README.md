# Core Application Library

This directory houses the foundational components required to manage database connections and map object-relational schemas consistently across the application. It acts as the shared single source of truth for both the `api` and `etl` services.

## The Zero-Trust Connection Manager
The `core/database.py` script manages SQLAlchemy sessions explicitly **without** role fallbacks. This is a critical security countermeasure. 

By demanding the executing process dynamically inject the `DB_USER` and `DB_PASSWORD` variables, it structurally prevents privilege escalation. The `api` microservice operates securely under the highly-restricted `frontend_api` Postgres role, while the `etl` processes retain their necessary read/write authority, completely isolated from one another.

## Structural Data Models
The `core/models.py` file exposes precise SQLAlchemy ORM mixins (`FileLocationMixin`, `PipelineResultMixin`, `ApiEndpointMixin`). These mixins guarantee consistency between data ingress (ETL script) and data egress (the API), definitively mitigating schema drift.
