# NGS Variant Validator - Frontend UI

A lightweight, browser-targeted React/Vite application designed to visualize bioinformatics workflow states and genomic quality metrics. 

This client acts as a "dumb terminal". It contains zero bioinformatics logic and does not parse raw, multi-gigabyte genomic files (e.g., `.vcf`, `.bam`). Instead, it consumes strictly typed, deeply nested JSON payloads and pre-aggregated metadata directly from the FastAPI backend.

## 🏗️ Architecture & Core Technologies

* **Framework:** React 18 + Vite (TypeScript)
* **Styling:** Tailwind CSS v4 (using native `@theme` CSS variables)
* **State & Data Fetching:** TanStack React Query (configured for 10-second background polling of Nextflow states)
* **Routing:** React Router v6
* **Visualizations:** Apache ECharts (`echarts-for-react`) for high-performance Canvas/SVG rendering of biological metrics
* **Testing:** Vitest + React Testing Library

## 📂 Project Structure

```text
ngs-variant-ui/
├── src/
│   ├── api/          # Axios client configuration and HTTP interceptors (Zero-Trust API Key injection)
│   ├── components/   # Reusable UI elements (e.g., RunQualityChart.tsx for dual-axis plotting)
│   ├── hooks/        # React Query custom hooks (useSamples, useSampleDetail)
│   ├── pages/        # Top-level route components (SampleList.tsx, RunDetail.tsx)
│   ├── types/        # Strict TypeScript interfaces mirroring backend Pydantic models
│   ├── App.tsx       # React Router configuration
│   └── main.tsx      # React Query Provider and DOM mount
├── vite.config.ts    # Vite bundler and Vitest test environment configuration
└── package.json      # NPM dependencies and scripts
```

## 🚀 Local Development

### Prerequisites

* Node.js v20+
* A running instance of the `ngs-variant-validator` FastAPI backend (`localhost:8000`).

### 1. Environment Variables

Create a `.env` file in the root of the `ngs-variant-ui` directory to configure the API connection:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_FRONTEND_API_KEY=your_development_api_key

```

### 2. Run the Development Server

```bash
npm install
npm run dev

```

The application will be accessible at `http://localhost:5173`.

## 🧪 Testing

The repository enforces a strict testing requirement for CI/CD gating. Tests are executed via Vitest utilizing a `jsdom` environment.

```bash
# Run tests locally
npm run test
```