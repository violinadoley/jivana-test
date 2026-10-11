from pydantic import BaseModel, Field


class CapabilityStatus(BaseModel):
    id: str
    label: str
    configured: bool
    description: str


class PlatformCapabilitiesResponse(BaseModel):
    success: bool = True
    environment: str
    capabilities: list[CapabilityStatus] = Field(default_factory=list)
