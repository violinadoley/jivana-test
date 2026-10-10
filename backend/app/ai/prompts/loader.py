from pathlib import Path

PROMPTS_ROOT = Path(__file__).resolve().parent


def load_prompt(version: str, name: str) -> str:
    path = PROMPTS_ROOT / version / f"{name}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {version}/{name}")
    return path.read_text(encoding="utf-8")


def render_generate_text_prompt(user_message: str, version: str = "v1") -> str:
    template = load_prompt(version, "generate_text")
    return template.replace("{{user_message}}", user_message)
