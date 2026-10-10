# ADR-004: RAG before fine-tuning

## Context

Competition apps often need domain knowledge; fine-tuning is expensive and slow to iterate.

## Decision

**Defer fine-tuning.** Prefer retrieval-augmented generation (RAG) when domain docs are required.

## Status

Placeholder — implement RAG in product phase if needed.

## Consequences

- Need ingestion pipeline, evals for retrieval quality, and grounding checks in `ai-evals/`
