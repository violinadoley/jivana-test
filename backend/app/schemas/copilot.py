from pydantic import BaseModel, Field


class CopilotMessage(BaseModel):
    role: str
    content: str


class CopilotSessionCreateRequest(BaseModel):
    title: str = Field(default="New conversation", max_length=120)


class CopilotSessionResponse(BaseModel):
    success: bool = True
    session_id: str
    title: str
    messages: list[CopilotMessage] = Field(default_factory=list)


class CopilotChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(..., min_length=1, max_length=16000)


class CopilotChatResponse(BaseModel):
    success: bool = True
    session_id: str
    response: str
    messages: list[CopilotMessage]
