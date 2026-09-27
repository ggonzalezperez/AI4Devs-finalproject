import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importa todos los modelos para que Base.metadata los conozca.
# Nota: usar `from app import models` (no `import app.models`) para no
# sobrescribir el nombre `app` (la instancia FastAPI importada arriba).
from app import models  # noqa: F401
from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.services import rate_limit

test_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _contadores_limpios():
    """El limitador guarda estado de proceso y los tests comparten proceso.

    Sin esto, los intentos se acumularían de un test a otro y la suite empezaría
    a fallar según el orden de ejecución. El `TestClient` además presenta
    siempre el mismo peer, así que todos caen en el mismo cubo.
    """
    rate_limit.limitador.limpiar()
    yield
    rate_limit.limitador.limpiar()


@pytest.fixture(autouse=True)
def _ajustes_neutros(monkeypatch):
    """Aísla la suite del `.env` de quien la ejecuta.

    `Settings` lee `.env`: en cuanto el `.env` local defina INVITE_CODE para
    probar el despliegue, los tests fallarían en esa máquina y pasarían en CI.
    """
    ajustes = get_settings()
    monkeypatch.setattr(ajustes, "invite_code", None)
    monkeypatch.setattr(ajustes, "rate_limit_enabled", True)
    monkeypatch.setattr(ajustes, "client_ip_header", None)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
