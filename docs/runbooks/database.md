# Firestore / database changes

## Principles

1. **Cloud project first** — validate schema or index changes against your hackathon Firebase/GCP project before wide rollout.
2. **Backward compatibility** — prefer additive changes (new fields) over destructive renames.
3. **No production credentials in dev** — use Firebase Emulator Suite locally when possible.
4. **Separate from prod elsewhere** — do not use employer or personal production Firebase/GCP credentials for the hackathon app.

## Change process

1. Document the change in a GitHub Issue and PR (schema section of PR template).
2. Update Firestore security rules and indexes (`firestore.rules`, `firestore.indexes.json`) in repo when you add Firebase config files.
3. Deploy rules/indexes to your hackathon Firebase project.
4. Deploy application code to Cloud Run; run integration tests.
5. Migrate data if required (batch script, idempotent, logged).
6. Repeat for production during a release window.

## Migrations

- Store one-off migration scripts in `scripts/migrations/` (create when needed) with README steps.
- Never run untested migrations against production.

## Emulator (development)

```bash
# When firebase.json is configured:
firebase emulators:start --only firestore,auth,storage
```

Point local backend at emulator hosts via env vars (document in `backend/.env.example` when wired).
