import json
from pathlib import Path

from evaluators.meddocs_manifest import REQUIRED_CASES, load_manifest, validate_manifest_entry

MANIFEST_PATH = Path(__file__).resolve().parents[1] / "datasets" / "meddocs" / "manifest.json"


def test_meddocs_manifest_is_valid_json() -> None:
    cases = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    assert len(cases) >= len(REQUIRED_CASES)


def test_meddocs_manifest_covers_plan_cases() -> None:
    cases = load_manifest()
    ids = {c["case_id"] for c in cases}
    missing = REQUIRED_CASES - ids
    assert not missing, f"missing cases: {missing}"


def test_meddocs_manifest_entries_well_formed() -> None:
    for entry in load_manifest():
        errors = validate_manifest_entry(entry)
        assert not errors, f"{entry.get('case_id')}: {errors}"


def test_documented_change_never_completed() -> None:
    entry = next(c for c in load_manifest() if c["case_id"] == "documented_change")
    assert entry["expected_status"] == "needs_review"


def test_baseline_match_requires_completed() -> None:
    entry = next(c for c in load_manifest() if c["case_id"] == "baseline_match")
    assert entry["expected_status"] == "completed"


def test_vertex_only_matching_meds_needs_review() -> None:
    entry = next(c for c in load_manifest() if c["case_id"] == "vertex_only_matching_meds")
    assert entry["expected_status"] == "needs_review"
    assert entry.get("weak_evidence") is True
