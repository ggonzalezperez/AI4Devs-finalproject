import ipaddress

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.config import get_settings
from app.database import get_db
from app.models.child import Child
from app.models.family import User
from app.security import decode_token
from app.services import rate_limit

bearer = HTTPBearer(auto_error=False)

# Cubo único para las peticiones sin socket (ASGI interno, tests de transporte).
_SIN_PEER = "desconocida"


def ip_cliente(request: Request, cabecera: str | None) -> str:
    """IP a la que imputar el intento.

    Fail-closed: si el despliegue no declara una cabecera de proxy, no se cree
    ninguna. Con `CLIENT_IP_HEADER` definida se lee su valor, pero se valida
    como IP: sin esa comprobación, cualquiera inventaría valores y haría crecer
    el diccionario del limitador sin freno.
    """
    peer = request.client.host if request.client else _SIN_PEER
    if not cabecera:
        return peer
    crudo = request.headers.get(cabecera)
    if not crudo:
        return peer
    # X-Forwarded-For llega como cadena "cliente, proxy1, proxy2".
    candidato = crudo.split(",")[0].strip()
    try:
        ipaddress.ip_address(candidato)
    except ValueError:
        return peer
    return candidato


class LimiteIntentos:
    """Corta la fuerza bruta contando intentos por IP y por cuenta.

    Es una dependencia y no un middleware porque el middleware no sabe a qué
    endpoint pertenece la petición sin mantener una tabla de rutas paralela,
    que se desincronizaría con el router a la primera.
    """

    def __init__(
        self,
        nombre: str,
        limite_ip: int,
        limite_cuenta: int,
        ventana: float,
        cuenta: str = "body:email",
    ) -> None:
        self.nombre = nombre
        self.limite_ip = limite_ip
        self.limite_cuenta = limite_cuenta
        self.ventana = ventana
        self.cuenta = cuenta

    async def __call__(self, request: Request) -> None:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return
        ip = ip_cliente(request, cabecera=settings.client_ip_header)
        self._consumir(f"{self.nombre}:ip:{ip}", self.limite_ip)
        cuenta = await self._clave_de_cuenta(request)
        if cuenta is not None:
            self._consumir(f"{self.nombre}:cuenta:{cuenta}", self.limite_cuenta)

    def _consumir(self, clave: str, limite: int) -> None:
        espera = rate_limit.limitador.consumir(clave, limite=limite, ventana=self.ventana)
        if espera is None:
            return
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            # Sin revelar si la cuenta existe, igual que el hash señuelo de
            # `auth_service` evita la enumeración por tiempos.
            detail="Demasiados intentos. Espera un momento e inténtalo de nuevo.",
            headers={"Retry-After": str(int(espera) + 1)},
        )

    async def _clave_de_cuenta(self, request: Request) -> str | None:
        """Identificador de la cuenta atacada, o None si no se puede saber.

        El email viaja en el cuerpo. Leerlo aquí es seguro porque Starlette
        cachea el cuerpo en la petición, así que el endpoint lo recibe intacto;
        si dejara de cachearse, los endpoints empezarían a ver cuerpos vacíos.
        """
        if self.cuenta == "path:child_id":
            valor = request.path_params.get("child_id")
            return str(valor) if valor is not None else None
        if self.cuenta == "token":
            credenciales = request.headers.get("authorization", "")
            token = credenciales[7:] if credenciales.lower().startswith("bearer ") else ""
            try:
                # Sin tocar la base de datos: solo se necesita el identificador.
                return str(decode_token(token).get("sub"))
            except jwt.InvalidTokenError:
                return None
        if self.cuenta == "body:email":
            try:
                cuerpo = await request.json()
            except Exception:
                # Cuerpo ausente o malformado: que responda la validación del
                # endpoint (422), no el limitador.
                return None
            email = cuerpo.get("email") if isinstance(cuerpo, dict) else None
            return email.strip().lower() if isinstance(email, str) else None
        return None


_QUINCE_MINUTOS = 15 * 60

# Cada intento de login cuesta un bcrypt: el límite protege la contraseña y de
# paso la CPU de una máquina modesta.
LIMITE_LOGIN = LimiteIntentos("login", limite_ip=10, limite_cuenta=5, ventana=_QUINCE_MINUTOS)
# Ventana larga: nadie da de alta familias en ráfaga, y el alta es lo que abre
# la puerta a un desconocido.
LIMITE_REGISTRO = LimiteIntentos("registro", limite_ip=5, limite_cuenta=3, ventana=60 * 60)
# El código de recuperación tiene 128 bits, pero el límite corta también el
# goteo lento contra una cuenta concreta.
LIMITE_RESET = LimiteIntentos("reset", limite_ip=10, limite_cuenta=5, ventana=_QUINCE_MINUTOS)
# La puerta que el niño tiene delante para salir de su sesión: la cuenta sale
# del token, no del cuerpo.
LIMITE_VERIFICAR = LimiteIntentos(
    "verificar", limite_ip=10, limite_cuenta=5, ventana=_QUINCE_MINUTOS, cuenta="token"
)
# El PIN son 4 dígitos, pero este endpoint ya exige token de familia: el
# atacante realista es el hermano, no internet. Umbral generoso porque el PIN
# se autoenvía al cuarto dígito y el error de tecleo de un niño es constante.
LIMITE_PIN = LimiteIntentos(
    "pin", limite_ip=20, limite_cuenta=10, ventana=_QUINCE_MINUTOS, cuenta="path:child_id"
)


def get_current_family_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta token")
    try:
        payload = decode_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido") from None
    if payload.get("type") != "family":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Tipo de token inválido"
        )
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user


def get_current_child(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Child:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta token")
    try:
        payload = decode_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido") from None
    if payload.get("type") != "child":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Tipo de token inválido"
        )
    child = db.get(Child, int(payload["sub"]))
    if child is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Niño no encontrado")
    return child
