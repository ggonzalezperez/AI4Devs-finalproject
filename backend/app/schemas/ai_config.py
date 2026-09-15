from pydantic import BaseModel, Field


class HardwareQuery(BaseModel):
    vram_gb: float = Field(ge=0)
    ram_gb: float = Field(ge=0)


class Recommendation(BaseModel):
    can_run_local: bool
    fits: list[str]
    recommended: str
    note: str


class AIConfigRead(BaseModel):
    tier: str
    provider: str
    model: str | None
    base_url: str | None
    has_api_key: bool
    monthly_quota: int
    used_count: int
    image_provider: str
    image_model: str | None
    image_base_url: str | None
    image_enabled: bool
    has_image_api_key: bool


class AIConfigUpdate(BaseModel):
    tier: str
    provider: str
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    image_provider: str = "none"
    image_model: str | None = None
    image_base_url: str | None = None
    image_api_key: str | None = None
    image_enabled: bool = False
