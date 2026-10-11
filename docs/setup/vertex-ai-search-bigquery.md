# Vertex AI Search & BigQuery (enterprise productivity)

JIVANA uses these when environment variables are set on Cloud Run (or local backend with ADC).

## Vertex AI Search

1. In GCP Console, create a **Search** data store and ingest your policy PDFs / intranet HTML (synthetic corpus for demos).
2. Set GitHub Actions vars / Cloud Run env:

```env
VERTEX_SEARCH_DATA_STORE_ID=your-data-store-id
VERTEX_SEARCH_LOCATION=global
VERTEX_SEARCH_SERVING_CONFIG=default_search
```

3. Grant Cloud Run SA `discoveryengine.viewer` or broader search roles per [Discovery Engine IAM](https://cloud.google.com/generative-ai-app-builder/docs/access-control).

`GET /api/v1/search?q=...` returns Vertex hits merged with institutional JSON corpus.

## BigQuery productivity events

1. Create dataset and table, e.g.:

```sql
CREATE TABLE `PROJECT.jivana_analytics.productivity_events` (
  event_type STRING,
  user_id STRING,
  metadata JSON,
  recorded_at TIMESTAMP
);
```

2. Env:

```env
BIGQUERY_DATASET_ID=jivana_analytics
BIGQUERY_PRODUCTIVITY_TABLE=productivity_events
```

3. Grant `roles/bigquery.dataEditor` on the dataset to the Cloud Run runtime SA.

Copilot, search, meetings, research, and workflow agent routes append rows when configured.
