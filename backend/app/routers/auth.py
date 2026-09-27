import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import (
    LIMITE_LOGIN,
    LIMITE_REGISTRO,
    LIMITE_RESET,
    LIMITE_VERIFICAR,
    get_current_family_user,
)
from app.models.family import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RecoveryResult,
    RegisterRequest,
    RegisterResult,
    ResetPasswordRequest,
    Token,
    VerifyPasswordRequest,
)
from app.security import create_token, verify_secret
from app.services import auth_service, rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


def _check_invite_code(given: str | None) -> None:
    """Cierra el alta cuando el servidor define una palabra de invitación.

    Se consulta `get_settings()` en tiempo de petición, no al importar: el
    singleton está cacheado y leerlo a nivel de módulo congelaría el valor.
    """
    expected = get_settings().invite_code
    if expected is None:
        return
    if not secrets.compare_digest((given or "").strip(), expected.strip()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Código de invitación no válido"
        )


@router.post(
    "/register",
    response_model=RegisterResult,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(LIMITE_REGISTRO)],
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResult:
    _check_invite_code(payload.invite_code)
    try:
        user, recovery_code = auth_service.register_family(db, payload.name, payload.email, payload.password)
    except auth_service.EmailAlreadyExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado") from None
    return RegisterResult(
        access_token=create_token(subject=str(user.id), token_type="family"),
        recovery_code=recovery_code,
    )


@router.post("/login", response_model=Token, dependencies=[Depends(LIMITE_LOGIN)])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = auth_service.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    # Credenciales demostradas válidas no son fuerza bruta: se olvida el cubo de
    # esta cuenta para que una familia con varios dispositivos no se autobloquee.
    # El cubo por IP no se toca, o bastaría tener una cuenta válida para
    # reiniciar la cuota a voluntad.
    rate_limit.limitador.olvidar(f"login:cuenta:{payload.email.strip().lower()}")
    return Token(access_token=create_token(subject=str(user.id), token_type="family"))


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> dict:
    if not auth_service.change_password(db, user, payload.current_password, payload.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña actual incorrecta")
    return {"status": "ok"}


@router.post(
    "/reset-password", response_model=RecoveryResult, dependencies=[Depends(LIMITE_RESET)]
)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> RecoveryResult:
    new_code = auth_service.reset_password(db, payload.email, payload.recovery_code, payload.new_password)
    if new_code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email o código de recuperación incorrectos")
    return RecoveryResult(recovery_code=new_code)


@router.post("/verify-password", dependencies=[Depends(LIMITE_VERIFICAR)])
def verify_password(
    payload: VerifyPasswordRequest,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> dict:
    """Confirma que quien pulsa es el adulto, no el niño.

    Mientras el niño juega, el token de familia sigue en el dispositivo: tenerlo
    no prueba nada. Por eso salir de su sesión pide la contraseña otra vez.
    """
    if not verify_secret(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta"
        )
    return {"status": "ok"}
