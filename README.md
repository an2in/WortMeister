# WortMeister

WortMeister is a German vocabulary learning app organized as one cohesive monorepo. The app keeps the polished Next.js UI while moving Data Structures and Algorithms work into the Python backend.

## Architecture

```text
DSA_BTL/
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── core/          # Backend settings and configuration
│   │   │   ├── dsa/           # Manual Python DSA primitives
│   │   │   │   ├── heap.py        # Array-backed Min Heap for scheduling
│   │   │   │   ├── queue.py       # Array-backed FIFO Queue for BFS
│   │   │   │   ├── randomized.py  # Fisher-Yates Shuffle and random selection
│   │   │   │   ├── search.py      # Binary Search (lower_bound)
│   │   │   │   ├── sort.py        # Stable Merge Sort
│   │   │   │   └── text_scan.py   # Manual Token Scanner
│   │   │   ├── models/        # Domain models and API schemas
│   │   │   ├── routers/       # FastAPI route/controller layer
│   │   │   └── services/      # OOP application services
│   │   ├── data.json          # German vocabulary dataset
│   │   ├── main.py            # FastAPI entrypoint
│   │   └── requirements.txt   # Python dependencies
│   └── web/
│       ├── src/
│       │   ├── app/           # Next.js pages/routes
│       │   ├── components/    # UI components
│       │   ├── hooks/         # React hooks
│       │   └── lib/           # API client and UI utilities
│       ├── .env.example       # Safe environment template
│       ├── next.config.ts     # Next.js config
│       └── package.json       # Web dependencies and scripts
├── scripts/
│   └── dev.sh                 # Starts backend and web together
├── package.json               # Root commands
└── README.md
```

The backend owns the app logic and DSA-heavy features: SRS scheduling, article/plural drills, search indexing, context analysis, maze generation, BFS shortest-path hints, user state, notebook persistence, image lookup, and text-to-speech audio generation. The frontend renders UI, stores an anonymous local user id, and calls backend APIs.

## Manual DSA requirement

Core algorithmic helpers are implemented manually in Python under `apps/backend/app/dsa/` instead of relying on Python algorithm libraries:

- `heap.py` — array-backed min heap for scheduling.
- `search.py` — iterative lower-bound binary search.
- `sort.py` — stable merge sort.
- `queue.py` — array-backed FIFO queue for BFS.
- `randomized.py` — Fisher-Yates shuffle and random selection helpers.
- `text_scan.py` — manual token scanning, word matching, whitespace compaction, and identifier checks.

Framework and IO libraries such as FastAPI, Pydantic, `json`, `pathlib`, `urllib`, `datetime`, `time`, `uuid`, and Edge TTS remain normal dependencies.

## User state

User state is created lazily only when a real user uses the app. The web app creates an anonymous id in localStorage and sends it to the backend via `X-User-Id`.

Runtime user files live under:

```text
apps/backend/user_state/{user_id}/
├── srs_state.json
├── learning_progress.json
└── notebook.json
```

`apps/backend/user_state/` is ignored by git and must not be committed.

## Features

- Dashboard linked to real backend SRS stats, learning streak, and recent notebook words.
- Flashcards powered by Python SM-2 scheduling.
- Article/plural reaction drill with backend scheduling.
- Search and reader/context analyzer backed by Python services.
- Per-user notebook CRUD with automatic Wikimedia image lookup and user-editable image URLs.
- Python Edge TTS pronunciation/audio endpoints.
- Maze game generated in Python with randomized layouts, ordered letter collection, duplicate-letter support, session recovery, and optional shortest-path hints to the next correct letter.

## Setup

Install web dependencies:

```bash
npm --prefix apps/web install
```

The root dev command automatically creates `apps/backend/.venv` if needed and installs backend dependencies from `apps/backend/requirements.txt`.

Create the web environment file:

```bash
cp apps/web/.env.example apps/web/.env
```

Set values in `apps/web/.env`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Run the full app

From the repository root:

```bash
npm run dev
```

This starts:

- Python backend: http://localhost:8000
- Next.js web UI: http://localhost:9002

The dev script also warms common Next.js routes so first navigation feels faster during development.