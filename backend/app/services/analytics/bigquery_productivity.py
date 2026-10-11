import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings

logger = logging.getLogger(__name__)


class BigQueryProductivityService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def enabled(self) -> bool:
        return self._settings.bigquery_analytics_configured

    def record_event(
        self,
        *,
        event_type: str,
        user_id: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return
        project = self._settings.effective_gcp_project_id
        dataset = self._settings.bigquery_dataset_id
        table = self._settings.bigquery_productivity_table
        if not project or not dataset:
            return
        table_id = f"{project}.{dataset}.{table}"
        now = datetime.now(UTC)
        row = {
            "event_type": event_type,
            "user_id": user_id,
            # BigQuery JSON columns expect a JSON-encoded string in streaming inserts.
            "metadata": json.dumps(metadata or {}),
            # Streaming insert expects TIMESTAMP-compatible string (not all ISO-8601 variants).
            "recorded_at": now.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
        try:
            from google.cloud import bigquery

            client = bigquery.Client(project=project)
            errors = client.insert_rows_json(table_id, [row])
            if errors:
                logger.error("BigQuery insert errors: %s", errors)
        except Exception:
            logger.exception("BigQuery productivity event failed")
