### 📄 MASTER DOCUMENT META-SCHEMA

**`[DOCUMENT_TITLE]`** Frontend Architecture & E2E Integration Retrospective
**`[LAST_UPDATED]`** 2026-02-23
**`[VERSION]`** v1.0.0.0
**`[DOMAIN]`** System Architecture / Retrospectives
**`[FILE_PATH]`** `docs/retrospectives/2026-02-23_frontend_e2e_integration.md`

---

#### 1. STRATEGIC DECISION: CLOSING THE E2E LOOP

**The Problem:** The backend hierarchy, Zero-Trust data layer, and Nextflow parameterization were complete, but the 14-day End-to-End (E2E) Proof of Concept lacked a client to consume the data.
**The Decision:** Prioritized the local browser UI (Path B) over AWS Cloud Infrastructure (Path A). Path A would have prematurely introduced AWS Batch, violating the local Modular Monolith constraint required for the $200/month FinOps budget. The UI proves the API contracts immediately.

#### 2. ARCHITECTURAL MILESTONES ACHIEVED

**A. Modern Vite & Tailwind v4 Integration**

* **Challenge:** Legacy `tailwindcss init` commands failed due to dependency mismatches.
* **Solution:** Pivoted to Tailwind CSS v4's Vite-native architecture. Replaced `postcss` and `autoprefixer` with the `@tailwindcss/vite` plugin and native `@theme` CSS imports.
* **Outcome:** Eliminated Vite boilerplate CSS (`App.css`), enabling seamless edge-to-edge application rendering.

**B. Zero-Trust API Ingress & CORS Implementation**

* **Challenge:** The frontend (`localhost:5173`) was blocked from reading the backend (`localhost:8000`) by browser Same-Origin policies. Complex OAuth was out of scope for the PoC.
* **Solution:** 1.  Injected `CORSMiddleware` into the FastAPI backend (`api/main.py`) to explicitly whitelist the Vite dev server.
2.  Built an Axios client instance with request interceptors to natively inject a hardcoded `X-API-Key` header, securing the REST endpoints without heavy identity providers.

**C. Asynchronous State Polling (React Query)**

* **Challenge:** The UI must display long-running Nextflow pipeline states dynamically without crushing the PostgreSQL database with requests.
* **Solution:** Implemented TanStack React Query (`useSamples`, `useSampleDetail`). Configured a 10-second `refetchInterval` for background polling, delegating cache invalidation and loading states entirely to the React Query provider.

**D. The "Dumb Terminal" Visualization Strategy**

* **Challenge:** Rendering complex biological data without parsing gigabytes of raw `.vcf` or `.bam` files on the client.
* **Solution:** 1.  **Data Engineering:** Updated the Python ETL seed script (`seed_database.py`) to simulate and inject pre-aggregated `coverage_profile` and `quality_profile` arrays directly into the PostgreSQL `JSONB` metadata column.
2.  **ECharts Canvas:** Built `RunQualityChart.tsx` utilizing Apache ECharts (`echarts-for-react`) to render a dual-axis line chart (Depth of Coverage vs. Phred Quality Score).
3.  **UI Grid Optimization:** Implemented a 1/3 (Metadata) to 2/3 (Canvas) responsive CSS grid to ensure the charts maintain aspect ratios and do not overflow from massive JSON string dumps.

**E. Automated UI Gating (DevSecOps)**

* **Challenge:** The `main` branch must remain pristine. Frontend code cannot bypass the CI/CD requirements applied to the backend.
* **Solution:** 1.  Bootstrapped Vitest and React Testing Library (`jsdom` environment).
2.  Authored core tests verifying API key injection and component degradation (fallback text rendering).
3.  Appended a `ui-tests` Node.js job to `.github/workflows/ci_pipeline.yaml` to enforce frontend validation alongside backend Pytest and Trivy container scanning.

#### 3. CORE LESSONS COMMITTED TO MEMORY

1. **Database Ephemerality:** When altering the structure of data injected by an ETL script (e.g., adding arrays to a JSONB column), the local database volume must be entirely destroyed (`./stop_dev.sh --clean`) and re-seeded. Stale rows will violently break strict frontend TypeScript components.
2. **Types are Contracts:** Mirroring backend Pydantic models with frontend TypeScript interfaces (`src/types/api.ts`) is mandatory. It immediately flags structural discrepancies between the database view and the UI expectation.
3. **UI Layout Triggers:** When `Object.entries().map()` is used to render arbitrary metadata, large arrays must be explicitly filtered out. Otherwise, React attempts to render them as massive text strings, destroying the DOM grid calculations.