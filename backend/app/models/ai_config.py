from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class FamilyAIConfig(Base):
    __tablename__ = "family_ai_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), unique=True, index=True)
    # tier: free | byok | managed
    tier: Mapped[str] = mapped_column(String(20), default="free")
    # provider: stub | ollama | claude | openai | gemini | deepseek | kimi
    provider: Mapped[str] = mapped_column(String(20), default="stub")
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(String(500), nullable=True)
    monthly_quota: Mapped[int] = mapped_column(Integer, default=0)  # 0 = ilimitado
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    # Imagen (Fase C). image_provider: none | huggingface | local_sdxl | openai | gemini
    image_provider: Mapped[str] = mapped_column(String(20), default="none")
    image_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    image_base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_api_key_encrypted: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
