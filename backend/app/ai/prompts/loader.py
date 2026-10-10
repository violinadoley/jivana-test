from pathlib import Path

PROMPTS_ROOT = Path(__file__).resolve().parent


def load_prompt(version: str, name: str) -> str:
    path = PROMPTS_ROOT / version / f"{name}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {version}/{name}")
    return path.read_text(encoding="utf-8")


def _render(template: str, **replacements: str) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def render_generate_text_prompt(
    user_message: str,
    version: str = "v1",
    *,
    institutional_context: str = "",
) -> str:
    template = load_prompt(version, "generate_text")
    context = institutional_context.strip() or "No matching institutional excerpts."
    return _render(
        template,
        user_message=user_message,
        institutional_context=context,
    )


def render_named_prompt(version: str, name: str, **replacements: str) -> str:
    template = load_prompt(version, name)
    return _render(template, **replacements)
