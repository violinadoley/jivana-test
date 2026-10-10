# ADR-002: Firebase / Firestore for application data

## Context

Hackathon apps need auth, document storage, and optional file storage with minimal backend code.

## Decision

Use **Firebase Auth**, **Firestore**, and **Firebase Storage** with separate projects per environment.

## Alternatives considered

- Cloud SQL — stronger relational needs not yet proven
- Supabase — adds another vendor outside Google stack goal

## Consequences

- Schema flexibility requires documented migration discipline
- Security rules must be versioned and reviewed
