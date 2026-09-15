from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_family_user
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
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResult, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResult:
    try:
        user, recovery_code = auth_service.register_family(db, payload.name, payload.email, payload.password)
    except auth_service.EmailAlreadyExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado") from None
    return RegisterResult(
        access_token=create_token(subject=str(user.id), token_type="family"),
        recovery_code=recovery_code,
    )


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = auth_service.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
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


@router.post("/reset-password", response_model=RecoveryResult)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> RecoveryResult:
    new_code = auth_service.reset_password(db, payload.email, payload.recovery_code, payload.new_password)
    if new_code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email o código de recuperación incorrectos")
    return RecoveryResult(recovery_code=new_code)


@router.post("/verify-password")
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
