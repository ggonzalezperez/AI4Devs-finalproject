# Task PWD-a: Cambiar y recuperar contraseña (backend)

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-password`. SIN push. TDD, migración NO destructiva.
No hay servicio de email → recuperación mediante **código de recuperación** (formato `XXXX-XXXX`) que se entrega **una vez al registrarse** y se **rota** en cada reseteo. Guardamos solo su **hash** (bcrypt). Además, cambio de contraseña estando logueado (requiere la actual).

**Files:**
- Modify: `app/models/family.py` (User.recovery_code_hash)
- Modify: `app/schemas/auth.py` (RegisterResult, ChangePasswordRequest, ResetPasswordRequest, RecoveryResult)
- Modify: `app/services/auth_service.py` (código + change_password + reset_password)
- Modify: `app/routers/auth.py` (register devuelve código; endpoints change/reset)
- Migración Alembic (add_column, no destructiva)
- Test: `tests/test_password.py`

## Step 1: `app/models/family.py`
En `User` añade (String ya importado): `recovery_code_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)`

## Step 2: `app/schemas/auth.py`
Asegura `from pydantic import BaseModel, EmailStr, Field` y añade:
```python
class RegisterResult(BaseModel):
    access_token: str
    token_type: str = "bearer"
    recovery_code: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    recovery_code: str
    new_password: str = Field(min_length=8)


class RecoveryResult(BaseModel):
    recovery_code: str
```
(Mantén `RegisterRequest`, `LoginRequest`, `Token`.)

## Step 3: `app/services/auth_service.py`
Añade `import secrets` arriba. Añade el generador y modifica/añade funciones:
```python
def _new_recovery_code() -> str:
    h = secrets.token_hex(4).upper()  # 8 hex
    return f"{h[:4]}-{h[4:]}"
```
Cambia `register_family` para fijar el código y devolverlo:
```python
def register_family(db: Session, name: str, email: str, password: str) -> tuple[User, str]:
    if family_repo.get_user_by_email(db, email):
        raise EmailAlreadyExists()
    user = family_repo.create_family_with_user(db, name, email, hash_secret(password))
    code = _new_recovery_code()
    user.recovery_code_hash = hash_secret(code)
    db.commit()
    return user, code
```
Añade:
```python
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
```

## Step 4: `app/routers/auth.py`
Importa los nuevos schemas y `get_current_family_user` (de `app.deps`) y `User` (de `app.models.family`). Cambia `register` y añade endpoints:
```python
@router.post("/register", response_model=RegisterResult, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResult:
    try:
        user, recovery_code = auth_service.register_family(db, payload.name, payload.email, payload.password)
    except auth_service.EmailAlreadyExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")
    return RegisterResult(
        access_token=create_token(subject=str(user.id), token_type="family"),
        recovery_code=recovery_code,
    )


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> dict:
    if not auth_service.change_password(db, user, payload.current_password, payload.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña actual incorrecta")
    return {"status": "ok"}


@router.post("/reset-password", response_model=RecoveryResult)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> RecoveryResult:
    new_code = auth_service.reset_password(db, payload.email, payload.recovery_code, payload.new_password)
    if new_code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email o código de recuperación incorrectos")
    return RecoveryResult(recovery_code=new_code)
```
(Mantén `login`.)

## Step 5: Migración
- `./.venv/Scripts/alembic.exe revision --autogenerate -m "user recovery_code_hash"`
- Verifica que SOLO añade `op.add_column('users', sa.Column('recovery_code_hash', ...))`. Si hay drops/alters sobre otras tablas, DETENTE y reporta DONE_WITH_CONCERNS sin aplicar.
- Aplica: `./.venv/Scripts/alembic.exe upgrade head`.

## Step 6: Test `tests/test_password.py`
Cubre (reutiliza el patrón de registro existente):
- `POST /auth/register` devuelve `recovery_code` con formato `XXXX-XXXX` (regex `^[0-9A-F]{4}-[0-9A-F]{4}$`) y `access_token`.
- **Cambiar (logueado)**: con token de familia, `POST /auth/change-password` con `current_password` incorrecta → 400; con la correcta → 200 y luego `login` funciona con la nueva y falla con la vieja.
- **Recuperar**: `POST /auth/reset-password` con email + código correctos → 200 y devuelve un `recovery_code` NUEVO (distinto); la contraseña vieja ya no entra y la nueva sí; el código viejo ya NO sirve (rotado) → segundo reset con el viejo → 400.
- `reset-password` con código incorrecto → 400; con email inexistente → 400.
- Mantén verdes los tests existentes (OJO: los tests que hacían `register` y leían solo `access_token` siguen valiendo; si alguno afirmaba el shape exacto del body, ajústalo).
- `./.venv/Scripts/python.exe -m pytest -q` → todo PASS. `./.venv/Scripts/ruff.exe check app tests` → limpio.

## Step 7: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): change password + recovery-code reset (email-free)"
```
