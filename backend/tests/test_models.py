from datetime import date

from app.models.child import Child
from app.models.family import Family, User


def test_create_family_user_child(db_session):
    family = Family(name="Familia García")
    db_session.add(family)
    db_session.flush()

    user = User(family_id=family.id, email="papa@example.com", password_hash="x")
    child = Child(
        family_id=family.id, name="Lucía", birthdate=date(2018, 1, 1), pin_hash="y"
    )
    db_session.add_all([user, child])
    db_session.commit()

    assert user.id is not None
    assert child.id is not None
    assert child.family_id == family.id


def test_child_age_property():
    child = Child(name="Lucía", birthdate=date(2018, 1, 1), pin_hash="y")
    # Edad calculada respecto a hoy; debe ser >= 6 en 2024+.
    assert child.age >= 6
