from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    # Opcional en el contrato aunque el servidor lo exija: quien despliega en
    # casa no configura ninguno, y su registro no debe empezar a dar 422.
    invite_code: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


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


class VerifyPasswordRequest(BaseModel):
    password: str
