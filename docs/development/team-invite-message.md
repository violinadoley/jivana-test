# Copy-paste invite for teammates

Send in Slack/Teams/email. **Do not** paste API keys in chat — use your team password manager for `GEMINI_API_KEY`.

---

**Subject:** JIVANA repo — local setup

Hi team,

Clone and run JIVANA locally:

**Repo:** https://github.com/violinadoley/JIVANA  
**Onboarding (start here):** https://github.com/violinadoley/JIVANA/blob/develop/docs/development/team-onboarding.md  
**Live demo:** https://project-bf77a013-c0b3-413c-a75.web.app/dashboard  

**Quick start**

1. `git clone git@github.com:violinadoley/JIVANA.git && cd JIVANA`
2. Backend: `cd backend` → venv → `pip install -r requirements-dev.txt` → `cp .env.example .env` → set `GEMINI_API_KEY` (from vault)
3. `uvicorn app.main:app --reload --port 8000`
4. Frontend: `cd frontend` → `npm ci` → `cp .env.local.example .env.local` → set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`
5. `npm run dev` → open http://localhost:3000/dashboard

**Branching:** feature branches → PR to `develop` ([CONTRIBUTING.md](https://github.com/violinadoley/JIVANA/blob/develop/CONTRIBUTING.md)). Commits under your GitHub user — no Cursor co-author trailers.

**Env (see onboarding doc for full list):**

- **Minimum:** `GEMINI_API_KEY` + `NEXT_PUBLIC_API_URL` (in-memory med rec — restarts wipe cases).
- **Recommended:** also Firebase web vars (`NEXT_PUBLIC_FIREBASE_*`) + backend `FIREBASE_PROJECT_ID` / bucket + `gcloud auth application-default login` (shared Firestore like prod).
- **Full GCP:** copy integration IDs from team vault / GitHub Variables (Document AI, Vertex Search, FHIR, BigQuery) into `backend/.env`.

Ping me if you’re stuck on env or deploy access.
