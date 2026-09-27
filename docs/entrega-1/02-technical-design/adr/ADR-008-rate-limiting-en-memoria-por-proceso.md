# ADR-008 — Límite de intentos en memoria, por proceso

**Estado:** Aceptada (implementada el 21-09-2026)

## Contexto

Hasta ahora la API no tenía ningún freno a la fuerza bruta. Estaba declarado y asumido en
[seguridad.md](../seguridad.md) como riesgo residual, y era defendible mientras Chispa solo corriera
en la red de casa: quien está dentro de tu WiFi ya tiene problemas mayores que adivinar una
contraseña.

El 21-09-2026 la aplicación se publicó en internet (`chispa.chispalearn.com`). Eso cambia el cálculo:

- Un atacante puede probar contraseñas sin límite contra `/auth/login`.
- Quien reviente una cuenta **no puede leer** la clave de IA de esa familia —la API jamás la
  devuelve, solo `has_api_key`— pero **sí puede gastarla** pidiendo lecciones.
- `/auth/verify-password` es la puerta que impide que el niño salga solo de su sesión. Con el
  dispositivo en la mano y sin límite, un niño con paciencia acaba pasando.

## Decisión

Un contador propio de ventana deslizante, **en memoria del proceso**, aplicado como dependencia de
FastAPI a los cinco endpoints de credenciales, con **dos cubos independientes por intento**: uno por
IP y otro por cuenta.

**Por qué dos cubos y no uno.** El cubo por IP frena a quien machaca una cuenta; el cubo por cuenta
frena a quien rota direcciones. Y hay una asimetría que importa: la IP llega en una cabecera cuando
hay un proxy delante, así que es falsificable; el email y el `child_id` viajan en el cuerpo y en la
ruta, de modo que el cubo por cuenta se sostiene aunque el de IP se esquive.

**Por qué fail-closed con la IP.** Sin `CLIENT_IP_HEADER` definida no se cree ninguna cabecera y se
usa el peer del socket. Fiarse por defecto de `X-Forwarded-For` habría convertido el control en
decorativo: cualquiera con acceso al puerto del backend inventa una IP por intento. El valor leído
se valida además como dirección IP, o el diccionario del limitador crecería sin freno con claves
inventadas.

**Por qué se olvida el contador de cuenta al acertar.** Unas credenciales demostradas válidas no son
fuerza bruta, y una familia con varios dispositivos no debe autobloquearse. El cubo por IP no se
limpia: si se limpiara, bastaría tener una cuenta válida para reiniciar la cuota a voluntad.

| Endpoint | Por IP | Por cuenta | Ventana |
|---|---|---|---|
| `POST /auth/login` | 10 | 5 (email) | 15 min |
| `POST /auth/register` | 5 | 3 (email) | 60 min |
| `POST /auth/reset-password` | 10 | 5 (email) | 15 min |
| `POST /auth/verify-password` | 10 | 5 (usuario del token) | 15 min |
| `POST /children/{id}/login` | 20 | 10 (`child_id`) | 15 min |

El umbral del PIN es deliberadamente generoso: se autoenvía al cuarto dígito y el error de tecleo de
un niño es constante. Ese endpoint exige además token de familia, así que el atacante realista es el
hermano, no internet.

## Alternativas consideradas

- **`slowapi` + Redis.** La librería limita por una función de clave **síncrona** que recibe la
  petición; para contar por cuenta hay que leer el cuerpo, que es asíncrono. Habría que escribir
  igualmente la parte difícil, peleada con la librería, y añadir Redis al compose para el único modo
  que la justifica.
- **`limit_req` de nginx.** Limita por IP y no sabe nada de cuentas, así que no cubre al atacante que
  rota direcciones. Tampoco distingue un login fallido de uno correcto.
- **WAF de Cloudflare.** Protección perimetral externa: útil, pero vive fuera del producto. Si un día
  se despliega sin Cloudflare delante, la aplicación vuelve a estar desnuda.
- **Middleware en lugar de dependencia.** Un middleware no sabe a qué endpoint pertenece la petición
  sin mantener una tabla de rutas paralela, que se desincronizaría con el router a la primera.

## Consecuencias

- **El control es válido solo con un proceso.** El backend arranca con `uvicorn` sin `--workers`
  (`docker-entrypoint.sh`). Si algún día se añaden procesos o réplicas, cada uno contaría por su
  cuenta y el límite efectivo se multiplicaría **en silencio**. Ese es el disparador para mover el
  almacén a Redis o al proxy.
- **Los contadores mueren al reiniciar el contenedor.** Un atacante que provoque un reinicio recupera
  su cuota; no es un vector realista contra un despliegue casero.
- **Tope de claves con desalojo.** El diccionario tiene un máximo y desaloja la clave menos usada
  recientemente. Es un bypass teórico: para provocarlo hay que emitir decenas de miles de peticiones,
  lo que exige antes saltarse el cubo por IP.
- **Un hermano puede dejar al otro sin intentos** durante 15 minutos si agota los suyos. Se acepta a
  cambio del control, y se suaviza con un mensaje amable en lugar de un error técnico.
- **El limitador lee el cuerpo antes que Pydantic** para saber a qué cuenta imputar el intento.
  Funciona porque Starlette lo cachea en la petición; un test de regresión lo sujeta (un JSON
  malformado debe seguir devolviendo 422, no 500).

## Componentes

- `backend/app/services/rate_limit.py` — el contador, sin dependencias de FastAPI.
- `backend/app/deps.py` — `ip_cliente()` y la dependencia `LimiteIntentos`.
- `backend/app/routers/auth.py` y `children.py` — los cinco endpoints.
- `backend/tests/test_rate_limit.py`, `test_client_ip.py`, `test_rate_limit_api.py`.

Relacionada con ADR-002 (JWT tipado: la cuenta de `verify-password` sale del token sin tocar la base
de datos) y con el hash señuelo de `auth_service`, cuya lógica anti-enumeración se respeta: el 429 no
revela si la cuenta existe.
