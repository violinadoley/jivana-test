from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any


async def run_agent_text(agent: Any, user_text: str, *, app_name: str = "jivana") -> str:
    """Run one ADK agent turn and return concatenated model text."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    runner = InMemoryRunner(agent=agent, app_name=app_name)
    user_id = "jivana-api"
    session_id = uuid.uuid4().hex
    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id,
    )

    chunks: list[str] = []
    message = types.Content(role="user", parts=[types.Part.from_text(text=user_text)])

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=message,
    ):
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            if part.text:
                chunks.append(part.text)

    return "".join(chunks).strip()


def function_tools(*funcs: Callable[..., Any]) -> list[Any]:
    from google.adk.tools.function_tool import FunctionTool

    return [FunctionTool(func=f) for f in funcs]
