# 📄 Architectural Retrospective: Normalization & Zero-Trust Migration

**Date:** 2026-02-23
**Domain:** System Architecture, Database Engineering, DevSecOps

## 1. Data Modeling: Aligning Schema with Biological Reality

**The Problem:** The initial database relied on a flattened `samples` table where `sample_id` acted as the primary key while holding both the `patient_id` and the `assay_type`. This violated biological reality, as it prevented a single physical biospecimen from undergoing multiple independent sequencing events.
**The Solution:** Decomposed the schema into a strict 1-to-many biological hierarchy: `Patient -> Sample -> Run`.
**The Lesson:** Relational databases must model the real-world lifecycle of the data. By shifting the computational focus from the physical object (`Sample`) to the temporal event (`Run`), the system now natively supports longitudinal tracking and multi-assay workflows without risking primary key collisions.

## 2. DevSecOps: The Principle of Least Privilege in Migrations

**The Problem:** During the introduction of Alembic for programmatic schema migrations, an initial attempt to fix a permissions error inadvertently granted the `etl_worker` role `CREATE` privileges on the `public` schema.
**The Solution:** Revoked DDL (Data Definition Language) access from the runtime application role and configured `alembic.ini` to execute via the `postgres` superuser.
**The Lesson:** Never mix structural authority with data manipulation.

* **Database Owners (`postgres`):** Define the structure (CREATE/DROP tables, manage Alembic).
* **Runtime Workers (`etl_worker`):** Manipulate the data (INSERT/UPDATE/DELETE).
Granting an application role the power to alter schema opens a catastrophic attack vector if an application-layer vulnerability occurs.

## 3. Zero-Trust API Design: Physical Separation from PHI

**The Problem:** The frontend REST API needed to query relational metadata without ever exposing Protected Health Information (PHI) like `patient_id`.
**The Solution:** Implemented SQL `VIEW` structures (`frontend_patients`, `frontend_samples`, `frontend_runs`). The patient view securely projects an MD5 surrogate hash (`patient_hash`) while entirely omitting the underlying ciphertext column. The `frontend_api` PostgreSQL role was explicitly blocked from querying base tables.
**The Lesson:** Application-layer security is fragile; database-layer security is rigid. By physically barring the API's database role from selecting sensitive columns, data leakage becomes architecturally impossible, even if the Python code is compromised.

## 4. CI/CD Parity: The "Works on My Machine" Trap

**The Problem:** The local test suite passed flawlessly after the Alembic migration, but the CI/CD pipeline failed catastrophically with `UndefinedTable` errors.
**The Solution:** Updated the `.github/workflows/ci_pipeline.yaml` to execute `alembic upgrade head` immediately after the initial database bootstrap, but before Pytest execution.
**The Lesson:** A CI/CD pipeline must perfectly mirror the production deployment sequence. Bootstrapping a legacy schema from a `.sql` script is insufficient if the application code expects the post-migration state. Test environments must undergo the exact same state transitions as the live database.

## 5. API Optimization: Protecting the Backend from N+1 Exhaustion

**The Problem:** Refactoring the database into a three-tier hierarchy meant that fetching a specific sample now required retrieving its parent patient, multiple child runs, and all associated file pointers.
**The Solution:** Leveraged SQLAlchemy's `selectinload()` in the FastAPI routers.
**The Lesson:** When serializing deeply nested Pydantic models, naive ORM queries will trigger a separate database round-trip for every child record (the N+1 problem). Using eager loading (`selectinload` or `joinedload`) batches these lookups, reducing a potentially massive query cascade into just 2-3 highly optimized SQL statements.

## 6. Orchestration: Decoupling Compute from State

**The Problem:** Nextflow scripts (`db_fetch_inputs.py` and `db_log_outputs.py`) were tightly coupled to `sample_id`.
**The Solution:** Parameterized the pipeline to accept and act upon `run_id`.
**The Lesson:** Bioinformatics DAGs are workflow executions, not physical entities. A workflow should only care about the specific sequencing event (`Run`) it was asked to process. Decoupling the compute layer from the sample layer ensures that a failed pipeline run only affects that specific computational event, preserving the integrity of the core biospecimen record.