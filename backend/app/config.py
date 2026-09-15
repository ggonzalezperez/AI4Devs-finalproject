from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Default usable solo en desarrollo/tests. En cualquier entorno "production-class"
# DEBE sobrescribirse vía env JWT_SECRET con un valor largo y propio.
INSECURE_DEFAULT_SECRET = "dev-insecure-secret-change-me-in-production-please"
MIN_SECRET_LENGTH = 32
# Entornos que NO requieren secreto fuerte. Cualquier otro se trata como production-class.
DEV_ENVIRONMENTS = {"development", "dev", "local", "test", "testing"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    jwt_secret: str = INSECURE_DEFAULT_SECRET
    jwt_expire_minutes: int = 60 * 24 * 30  # 30 días (app familiar auto-alojada)
    database_url: str = "sqlite+pysqlite:///./chispa.db"
    cors_origins: str = "http://localhost:5173"
    ai_config_key: str | None = None
    media_dir: str = "media"
    image_timeout: float = 60.0

    @model_validator(mode="after")
    def _enforce_strong_secret_outside_dev(self) -> "Settings":
        # Fail-closed: todo entorno cuyo nombre no esté en la lista de dev se trata
        # como production-class y exige un secreto propio y suficientemente largo.
        if self.environment.strip().lower() not in DEV_ENVIRONMENTS:
            if self.jwt_secret == INSECURE_DEFAULT_SECRET:
                raise ValueError(
                    "JWT_SECRET debe configurarse explícitamente fuera de desarrollo "
                    "(no se permite el valor por defecto inseguro)."
                )
            if len(self.jwt_secret) < MIN_SECRET_LENGTH:
                raise ValueError(
                    f"JWT_SECRET debe tener al menos {MIN_SECRET_LENGTH} caracteres "
                    "fuera de desarrollo."
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
