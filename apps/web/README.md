# WortMeister Web UI

This is the Next.js UI package for WortMeister. It renders the interface and delegates DSA behavior to the Python backend in `apps/backend`.

## Local setup

Install dependencies:

```bash
npm install
```

Create a local environment file from the example:

```bash
cp .env.example .env
```

Set the Python backend URL in `apps/web/.env`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

AI-only features can use Gemini when a key is available:

```bash
GEMINI_API_KEY=your_gemini_key_here
```

Real `.env` files are ignored by Git. Keep API keys out of commits.

## Development

Prefer running the whole app from the repository root with:

```bash
npm run dev
```

To run only the web UI from this folder:

```bash
npm run dev
```

Run Genkit AI flows when working on Gemini-backed features:

```bash
npm run genkit:dev
```
