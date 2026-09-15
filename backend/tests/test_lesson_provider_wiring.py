from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.security import create_token
from app.services import lesson_service
from app.services.lesson_generator import GeneratedLesson


def _child_token(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return create_token(subject=str(child.id), token_type="child")


def test_default_family_uses_stub_and_creates_lesson(client, db_session):
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué llueve?"},
    )
    assert r.status_code == 201  # provider stub por defecto


def test_provider_failure_falls_back_to_stub(client, db_session, monkeypatch):
    class _Boom:
        def generate(self, *a, **k):
            raise RuntimeError("proveedor caído")

    monkeypatch.setattr(lesson_service, "build_generator", lambda cfg: _Boom())
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué llueve?"},
    )
    assert r.status_code == 201  # cayó al stub, el niño no ve el error
    assert r.json()["quiz"]["question"]


def test_provider_success_uses_configured_generator(client, db_session, monkeypatch):
    class _Fake:
        def generate(self, curiosity, age, subject):
            return GeneratedLesson(
                subject="arte", concept="c", title="TÍTULO IA", body="b", fun_fact="f",
                quiz_question="¿?", quiz_options=["a", "b", "c"], quiz_correct_index=2,
                quiz_explanation="e",
            )

    monkeypatch.setattr(lesson_service, "build_generator", lambda cfg: _Fake())
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "dinosaurios"},
    )
    assert r.status_code == 201
    assert r.json()["title"] == "TÍTULO IA"
    assert r.json()["subject"] == "arte"
