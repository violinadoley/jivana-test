# Development

## Prerequisites

- Node.js 20+ (22 recommended for CI parity)
- Python 3.11+
- Optional: Docker for containerized backend
- Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Environment files

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Edit `backend/.env` and set at least:

```env
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
```

## Backend (local)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Health: [http://localhost:8000/health](http://localhost:8000/health)
- API docs (dev): [http://localhost:8000/docs](http://localhost:8000/docs)

## Frontend (local)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`.

## Authentication (optional)

- Backend: `AUTH_REQUIRED=true` and Firebase Admin credentials (`FIREBASE_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS` or default credentials on GCP).
- Frontend: fill `NEXT_PUBLIC_FIREBASE_*` and set `NEXT_PUBLIC_AUTH_REQUIRED=true`.

With `AUTH_REQUIRED=false` (default), API routes work without login for faster hackathon iteration.

## Docker Compose (backend only)

```bash
docker compose up --build backend
```

Backend listens on [http://localhost:8000](http://localhost:8000).

## Testing

```bash
cd backend && pytest -q
cd frontend && npm run lint && npx tsc --noEmit
```

## Helper script

```bash
./scripts/dev.sh
```

Prints the recommended two-terminal workflow.
