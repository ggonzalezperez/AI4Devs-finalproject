import secrets

from sqlalchemy.orm import Session

from app.models.family import User
from app.repositories import family as family_repo
from app.security import hash_secret, verify_secret

# Hash "señuelo" precomputado: cuando el email no existe, igualmente verificamos
# contra este hash para que el coste temporal sea indistinguible de un password
# incorrecto (evita enumeración de usuarios por timing).
_DUMMY_HASH = hash_secret("timing-attack-mitigation-dummy-value")


class EmailAlreadyExists(Exception):
    pass


def _new_recovery_code() -> str:
    # 128 bits de entropía (resetea la contraseña → debe ser inadivinable),
    # en grupos de 4 para que sea legible al guardarlo/copiarlo.
    h = secrets.token_hex(16).upper()  # 32 hex = 128 bits
    return "-".join(h[i : i + 4] for i in range(0, len(h), 4))


def register_family(db: Session, name: str, email: str, password: str) -> tuple[User, str]:
    if family_repo.get_user_by_email(db, email):
        raise EmailAlreadyExists()
    user = family_repo.create_family_with_user(db, name, email, hash_secret(password))
    code = _new_recovery_code()
    user.recovery_code_hash = hash_secret(code)
    db.commit()
    return user, code


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = family_repo.get_user_by_email(db, email)
    if user is None:
        verify_secret(password, _DUMMY_HASH)  # coste constante, resultado descartado
        return None
    if verify_secret(password, user.password_hash):
        return user
    return None


def change_password(db: Session, user: User, current: str, new: str) -> bool:
    if not verify_secret(current, user.password_hash):
        return False
    user.password_hash = hash_secret(new)
    db.commit()
    return True


def reset_password(db: Session, email: str, code: str, new: str) -> str | None:
    user = family_repo.get_user_by_email(db, email)
    if user is None or not user.recovery_code_hash:
        verify_secret(code, _DUMMY_HASH)  # coste constante (anti-enumeración)
        return None
    if not verify_secret(code, user.recovery_code_hash):
        return None
    user.password_hash = hash_secret(new)
    new_code = _new_recovery_code()
    user.recovery_code_hash = hash_secret(new_code)
    db.commit()
    return new_code
