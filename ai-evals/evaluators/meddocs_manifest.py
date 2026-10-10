import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "datasets" / "meddocs" / "manifest.json"

REQUIRED_CASES = {
    "baseline_match",
    "dose_mismatch",
    "documented_change",
    "docai_misconfigured",
    "docai_unconfigured_vertex_only",
    "vertex_only_matching_meds",
    "cross_document_block_id",
    "invalid_source_block_id",
}


def load_manifest() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def validate_manifest_entry(entry: dict) -> list[str]:
    errors: list[str] = []
    if not entry.get("case_id"):
        errors.append("missing case_id")
    if not entry.get("expected_status"):
        errors.append("missing expected_status")
    return errors
