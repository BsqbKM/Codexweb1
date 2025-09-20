# WineLens

WineLens is a production-ready wine label recognition service. It combines OCR, vector embeddings, hybrid retrieval, and quality scoring to deliver best-effort predictions from a single photo of a wine bottle.

## Features

- 📸 Image upload with drag & drop UI (React + Vite + Tailwind)
- 🔍 OCR abstraction supporting Tesseract or EasyOCR
- 🧠 Deterministic CLIP/SBERT-style embedding stubs with Faiss-compatible indexes
- ⚖️ Hybrid ranking over image & text vectors, enriched with rule-based boosts
- 🍷 Quality scoring with database lookups or gradient boosted regression fallback
- 🪟 Explainability blocks (OCR tokens, similar wines, feature importances)
- 🧾 Feedback logging, request history (IndexedDB) and inference logging
- 🛠️ Tooling: Alembic migrations, pytest unit tests, Playwright e2e, benchmark script, Docker + docker-compose, GitHub Actions CI

## Architecture

```text
frontend/ (React SPA)  -->  FastAPI backend  -->  SQLite/Postgres
                                 |                   |
                             ML services        Embedding store
                                 |                   |
                          Seed script & CLI   storage/*.npz indices
```

The inference pipeline performs:

1. **Preprocessing** – EXIF stripping, basic auto-crop, contrast preserving resize.
2. **OCR** – adapter pattern; default uses Tesseract with multilingual configuration.
3. **Embeddings** – deterministic projections for images/text (CLIP/SBERT style).
4. **Retrieval** – cosine similarity with hybrid image/text fusion and reranking.
5. **Scoring** – reuse database quality if available, otherwise apply GradientBoosting regressor.
6. **Explainability** – highlights key OCR tokens, embedding neighbours, and regressor feature gains.
7. **Logging** – inference rows, uploads metadata, optional feedback channel.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+ (for frontend dev or Playwright)
- Optional: Tesseract OCR binary for `pytesseract`

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

Install optional ML dependencies (torch/transformers/onnxruntime, etc.) if required:

```bash
pip install ".[ml]"
```

Install frontend toolchain:

```bash
cd frontend
npm install
```

### Environment

Create a `.env` file (values below are defaults):

```dotenv
WINELENS_SYNC_DATABASE_URL=sqlite:///./winelens.db
WINELENS_DATABASE_URL=sqlite+aiosqlite:///./winelens.db
WINELENS_ALLOWED_ORIGINS=http://localhost:5173
WINELENS_MAX_UPLOAD_SIZE_MB=8
WINELENS_RATE_LIMIT_CALLS=60
WINELENS_RATE_LIMIT_PERIOD_SECONDS=60
WINELENS_STORE_IMAGES=false
```

### Database & Data

Run migrations (SQLite dev by default):

```bash
alembic upgrade head
```

Seed the catalog and train the quality regressor:

```bash
make seed
```

Build vector indexes consumed by the retrieval service:

```bash
make build-index
```

### Running locally

#### Backend only

```bash
make run
```

API docs available at `http://localhost:8000/docs` and `http://localhost:8000/openapi.json`.

#### Backend + Frontend + Postgres (Docker)

```bash
make dev
```

Front-end dev server is exposed at `http://localhost:5173` (proxied to backend on port 8000).

### Testing & Quality

```bash
make test           # pytest suite
make frontend-test  # Playwright smoke test (requires browsers)
```

To execute the benchmark against local samples:

```bash
python scripts/benchmark.py
```

### CLI helpers

```bash
python -m app.cli build-index
```

### Frontend build

```bash
cd frontend
npm run build
```

### Directory Overview

- `app/` – FastAPI application, services, schemas, ORM models
- `scripts/` – database seeding, benchmarking helpers
- `alembic/` – migration env & initial schema revision
- `frontend/` – Vite + React SPA
- `storage/` – persisted uploads, trained artifacts, vector indexes
- `data/seed_wines.json` – synthetic catalog used for bootstrapping

## API Summary

- `POST /api/v1/infer` – multipart image upload, returns ranked candidates and quality estimate
- `GET /api/v1/wines/{id}` – retrieve wine metadata
- `POST /api/v1/feedback` – submit user-correctness feedback
- `GET /api/v1/healthz` – readiness/liveness probe

See [`openapi.yaml`](openapi.yaml) for the full schema and response bodies.

## Privacy & Observability

- Upload storage is opt-in (`store_image` flag, default disabled)
- Metadata logging avoids PII and removes EXIF/GPS data
- Settings capture dependency and model versions for reproducibility

## CI/CD

GitHub Actions workflow runs backend pytest and frontend build for every PR/push. Dockerfile provides a reproducible production container (uvicorn + FastAPI + static bundle).

## Troubleshooting

- **OCR empty?** Ensure the Tesseract binary is installed or switch to EasyOCR by instantiating `OCRService(EasyOCRBackend())`.
- **Slow inference?** Run `python scripts/benchmark.py` to collect latency stats and identify regressions.
- **Indexes missing?** Re-run `make build-index` after seeding or updating embeddings.

Happy tasting! 🍷
