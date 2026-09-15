import pytest
from pydantic import ValidationError

from app.config import INSECURE_DEFAULT_SECRET, Settings


def test_production_rejects_insecure_default_secret():
    with pytest.raises(ValidationError):
        Settings(environment="production", jwt_secret=INSECURE_DEFAULT_SECRET)


def test_production_accepts_custom_secret():
    s = Settings(environment="production", jwt_secret="a-properly-configured-long-secret-value")
    assert s.jwt_secret != INSECURE_DEFAULT_SECRET


def test_development_allows_default_secret():
    s = Settings(environment="development")
    assert s.jwt_secret == INSECURE_DEFAULT_SECRET


def test_production_rejects_too_short_secret():
    with pytest.raises(ValidationError):
        Settings(environment="production", jwt_secret="too-short")


def test_unknown_environment_treated_as_production_class():
    # Un nombre de entorno desconocido es fail-closed (exige secreto propio).
    with pytest.raises(ValidationError):
        Settings(environment="staging", jwt_secret=INSECURE_DEFAULT_SECRET)
