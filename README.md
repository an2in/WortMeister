# WortMeister

WortMeister is a German vocabulary learning app organized as one cohesive repository.

## Architecture

```text
apps/backend  Python FastAPI API, OOP services, DSA algorithms
apps/web      Next.js UI, presentation and user interaction only
scripts       Root-level development commands
```

The DSA requirement is enforced by architecture: scheduling, maze generation, BFS/pathfinding, move validation, and adaptive drills live in Python services under `apps/backend/app/services/`. The web app calls those services through API endpoints and does not own algorithmic decisions.

## Setup

Install Python dependencies in the environment you use for the backend:

```bash
pip install fastapi uvicorn edge-tts pydantic
```

Install web dependencies:

```bash
npm --prefix apps/web install
```

Create the web environment file:

```bash
cp apps/web/.env.example apps/web/.env
```

Set values in `apps/web/.env`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
GEMINI_API_KEY=
```

`GEMINI_API_KEY` is only needed for Gemini-backed AI features.

## Run the full app

From the repository root:

```bash
npm run dev
```

This starts:

- Python backend: http://localhost:8000
- Next.js web UI: http://localhost:9002

## Useful commands

```bash
npm run dev:backend
npm run dev:web
npm run typecheck
```
