from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    ai_prompt_version: str = Field(default="v1", alias="AI_PROMPT_VERSION")

    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    git_sha: str = Field(default="dev", alias="GIT_SHA")

    firebase_project_id: str | None = Field(default=None, alias="FIREBASE_PROJECT_ID")
    firebase_storage_bucket: str | None = Field(default=None, alias="FIREBASE_STORAGE_BUCKET")
    google_application_credentials: str | None = Field(
        default=None, alias="GOOGLE_APPLICATION_CREDENTIALS"
    )

    auth_required: bool = Field(default=False, alias="AUTH_REQUIRED")
    max_upload_size_mb: int = Field(default=10, alias="MAX_UPLOAD_SIZE_MB")

    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    gcp_project_id: str | None = Field(default=None, alias="GCP_PROJECT_ID")
    gcp_location: str = Field(default="us-central1", alias="GCP_LOCATION")
    vertex_location: str | None = Field(default=None, alias="VERTEX_LOCATION")
    document_ai_processor_id: str | None = Field(default=None, alias="DOCUMENT_AI_PROCESSOR_ID")
    document_ai_location: str = Field(default="us", alias="DOCUMENT_AI_LOCATION")
    vertex_model: str = Field(default="gemini-2.5-flash", alias="VERTEX_GEMINI_MODEL")

    healthcare_dataset_id: str | None = Field(default=None, alias="HEALTHCARE_DATASET_ID")
    healthcare_fhir_store_id: str | None = Field(default=None, alias="HEALTHCARE_FHIR_STORE_ID")
    healthcare_location: str = Field(default="us-central1", alias="HEALTHCARE_LOCATION")

    vertex_search_data_store_id: str | None = Field(
        default=None, alias="VERTEX_SEARCH_DATA_STORE_ID"
    )
    vertex_search_location: str = Field(default="global", alias="VERTEX_SEARCH_LOCATION")
    vertex_search_serving_config: str = Field(
        default="default_search", alias="VERTEX_SEARCH_SERVING_CONFIG"
    )

    bigquery_dataset_id: str | None = Field(default=None, alias="BIGQUERY_DATASET_ID")
    bigquery_productivity_table: str = Field(
        default="productivity_events", alias="BIGQUERY_PRODUCTIVITY_TABLE"
    )

    # legacy | adk | auto (prefer ADK when google-adk is installed)
    agent_backend: str = Field(default="auto", alias="AGENT_BACKEND")
    # Optional hosted runtime (Agent Engine). In-process ADK used when unset.
    vertex_agent_engine_id: str | None = Field(default=None, alias="VERTEX_AGENT_ENGINE_ID")

    smart_client_id: str | None = Field(default=None, alias="SMART_CLIENT_ID")
    smart_fhir_iss: str | None = Field(default=None, alias="SMART_FHIR_ISS")
    smart_app_launch_url: str | None = Field(default=None, alias="SMART_APP_LAUNCH_URL")

    @property
    def effective_gcp_project_id(self) -> str | None:
        return self.gcp_project_id or self.firebase_project_id

    @property
    def document_ai_configured(self) -> bool:
        return bool(self.document_ai_processor_id and self.document_ai_processor_id.strip())

    @property
    def healthcare_fhir_configured(self) -> bool:
        return bool(
            self.healthcare_dataset_id
            and self.healthcare_dataset_id.strip()
            and self.healthcare_fhir_store_id
            and self.healthcare_fhir_store_id.strip()
        )

    @property
    def vertex_search_configured(self) -> bool:
        return bool(self.vertex_search_data_store_id and self.vertex_search_data_store_id.strip())

    @property
    def bigquery_analytics_configured(self) -> bool:
        return bool(self.bigquery_dataset_id and self.bigquery_dataset_id.strip())

    @property
    def effective_vertex_location(self) -> str:
        if self.vertex_location and self.vertex_location.strip():
            return self.vertex_location.strip()
        return self.gcp_location

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Treat Cloud Run `cloud` like production for error masking and OpenAPI."""
        return self.environment.lower() in ("production", "cloud")

    @property
    def firebase_configured(self) -> bool:
        return bool(self.firebase_project_id)

    @property
    def vertex_agent_engine_configured(self) -> bool:
        return bool(self.vertex_agent_engine_id and self.vertex_agent_engine_id.strip())

    @property
    def smart_on_fhir_configured(self) -> bool:
        return bool(self.smart_client_id and self.smart_app_launch_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
