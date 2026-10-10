import json
from pathlib import Path

from app.ai.prompts.loader import load_prompt, render_generate_text_prompt
from app.ai.schemas.structured import PlaceholderStructuredResponse
from evaluators.schema import validate_json_schema

DATASET = Path(__file__).resolve().parents[1] / "datasets" / "v1" / "sample_cases.json"


def test_prompt_template_loads() -> None:
    text = load_prompt("v1", "generate_text")
    assert "{{user_message}}" in text
    assert "TODO" in text


def test_prompt_render_replaces_placeholder() -> None:
    rendered = render_generate_text_prompt("test message")
    assert "test message" in rendered
    assert "{{user_message}}" not in rendered


def test_dataset_file_valid_json() -> None:
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    assert len(cases) >= 1


def test_structured_schema_validator() -> None:
    assert validate_json_schema({"summary": "ok"}, PlaceholderStructuredResponse)
    assert not validate_json_schema({"summary": 1}, PlaceholderStructuredResponse)
