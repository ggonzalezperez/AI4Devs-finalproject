# Estado de implementación — Entrega 2 · Chispa ✨

> **Alumno:** Germán González Pérez · **Máster:** LIDR – AI4Devs
> **Fecha:** 14 de septiembre de 2026, ampliado el 15, el 21 y el 22 · **Rama:** `entrega_2`
>
> Este documento se escribe en **presente y pasado**: dice qué existe y qué se verificó.
> [`docs/entrega-1/`](../entrega-1/README.md) conserva el futuro ("el sistema deberá") porque es el
> documento de propuesta, y reescribirlo borraría la evidencia de que hubo diseño previo a la
> implementación. Cuando ambos discrepan, la divergencia se registra aquí con su motivo.

---

## 1. Resumen

El MVP está completo: **las 10 historias de usuario están implementadas y verificadas**.

| Medida | Entrega 1 (documental) | Hoy |
|---|---|---|
| Historias implementadas | 0 (propuesta) | **10 de 10** |
| Tests backend | 0 | **182** (36 ficheros) |
| Tests frontend | 0 | **74** (32 ficheros) |
| Endpoints | 27 previstos | **28 implementados** (+ `/health`) |
| Migraciones | 11 previstas | **11 aplicadas** (SQLite y PostgreSQL) |

`ruff` y `tsc --noEmit` limpios. CI verde en GitHub Actions.

## 2. Historias de usuario

| HU | Épica | Estado | Dónde vive |
|---|---|---|---|
| US1 · Cuenta familiar y perfiles | E1 | ✅ | `CreateFamily`, `AddExplorer`, `ChildAccess`, `ChangePassword`, `ResetPassword` |
| US2 · Encender la chispa | E2 | ✅ | `Spark` · `POST /lessons` |
| US3 · Lección por edad + voz | E2 | ✅ | `LessonScreen`, `SpeakButton` |
| US4 · Reto que sube la maestría | E2 | ✅ | `POST /lessons/{id}/answer` |
| US7 · Archipiélago y buscador | E3 | ✅ | `MyKnowledge` |
| US8 · Chat con contexto e islas | E3 | ✅ | `POST /lessons/{id}/ask`, `GET /lessons/{id}/thread` |
| US9 · Cuentos con aprobación parental | E4 | ✅ | `StoryLibrary`, `StoryReader`, `FamilyStories` |
| US10 · IA multiproveedor por familia | E5 | ✅ | `AIConfigPanel` · `/family/ai-config/*` |
| **US5/US6 · Panel de familia** | E6 | ✅ | `FamilyPanel` · `GET /children/{id}/profile` y `/knowledge` |
| **US5/US6 · Salir de la sesión del niño** (`RF-SEG-04`) | E6 | ✅ | `ExitChildSession` · `POST /auth/verify-password` |
| US11 · Voz, imágenes, QR/LAN, i18n | E6 | ✅ | `MicButton`, `ConnectDevice`, contexto i18n |

US5/US6 era la única que faltaba. El resto ya estaba construido antes de esta jornada.

## 3. Divergencias respecto a la Entrega 1

Las encontró una auditoría sistemática del 14-09-2026 contrastando `docs/entrega-1/` contra el
código, documento a documento y requisito a requisito.

| # | Divergencia | Resolución | Por qué |
|---|---|---|---|
| 1 | `RF-PLT-01` suponía servir el panel desde `/me/*` | **Se corrigió la HU** | `/me/*` exige token `child` por diseño (ADR-002). Dar acceso a la familia habría roto el JWT tipado, que es una garantía de seguridad. Se crearon endpoints propios de familia |
| 2 | `RF-ONB-03` exigía PIN `^\d{4}$`, aplicado solo en el formulario | **Se corrigió el código** | Una regla de negocio que solo vive en el cliente no es una regla. Ahora se valida en servidor. `contratos-api.md` y `modelo-datos.md` decían 4-8 y se alinearon |
| 3 | `RF-CUE-01` documentaba una entrada de título/cuerpo | **Se corrigió el documento** | El cuento se genera del archipiélago del niño: él lo protagoniza, no lo escribe. El diseño implementado es mejor que el documentado |
| 4 | `RF-APR-03` prometía adaptación por edad, ausente en modo demo | **Se corrigió el código** | El stub daba el mismo texto a un niño de 4 años y a uno de 11. Ahora tiene tres cuerpos, uno por banda |
| 5 | Moderación por subcadena bloqueaba curiosidades legítimas | **Se corrigió el código** | «arma» cortaba «armadura», «armario» y «Armada Invencible» |
| 6 | El 409 de avatar confundía «desactivado» con «proveedor caído» | **Se corrigió el código** | Mandaba a activar algo ya activado. Ahora 409 y 502 son casos distintos |

### 3.b · Segunda tanda de correcciones (15-09-2026)

Encontradas **usando la aplicación**, no leyendo el código. Cada una con su test.

| # | Qué fallaba | Por qué importaba | Resolución |
|---|---|---|---|
| 7 | Identificadores de modelo caducados en **todos** los proveedores | La serie **Imagen de Google se apagó el 17-08-2026** y la de **Kimi `moonshot-v1` el 31-08-2026**; el catálogo seguía ofreciéndolas. Un id caducado **no da error visible**: la llamada falla, el `except` la absorbe y el niño recibe stub mientras la familia cree pagar IA | Ids verificados contra la documentación de cada proveedor, no de memoria. Dos tests centinela fallan si reaparece uno retirado |
| 8 | OpenAI oculto tras un flag | Su adaptador ya existía y estaba cableado | Habilitado; `RF-IA-05` y seis documentos corregidos |
| 9 | Cualquier cadena se aceptaba como clave de IA | Caso real: se guardó una cadena de 156 caracteres; OpenAI devolvió 401 y el niño recibió lecciones del stub sin que nadie se enterara | Validación de **forma** al guardar (`RF-IA-02`) |
| 10 | Sin salida de la sesión del niño | Había que escribir la URL a mano para reconfigurar | `RF-SEG-04`: contraseña de familia, cierra solo la sesión del niño |
| 11 | El micrófono fallaba en silencio | El manejador descartaba la causa del error | Cinco mensajes según el código de la Web Speech API (`RF-PLT-02`) |
| 12 | Las ilustraciones desaparecían al redesplegar | El backend no tenía volumen: `MEDIA_DIR` moría con el contenedor y la BD quedaba apuntando a ficheros borrados | Volumen `media` (`RNF-08`) + el cliente oculta la imagen que no carga (`ADR-007`) |
| 13 | Sugerencias de inicio siempre idénticas | La pantalla que más se abre no cambiaba nunca | Repertorio de 25, muestra de 5 por visita (`RF-APR-01`) |
| 14 | Pantalla congelada esperando a la IA | Con el stub era instantáneo; con IA real son 2–5 s y el niño creía que se había roto | Indicador «Chispa está pensando…» (`RNF-07`) |

La #7 y la #12 comparten una lección que quedó escrita en la bitácora: **en esta aplicación el fallo
silencioso es la norma por diseño** —el niño nunca debe ver un error del proveedor— y eso convierte
cualquier avería en invisible también para el adulto. Varias de estas correcciones no añaden
función: hacen ruidoso hacia el operador lo que debe seguir siendo silencioso hacia el niño.


### 3.c · Endurecimiento del acceso (21-09-2026)

La aplicación se publicó en internet ese día (ver [demo pública](demo-publica.md)) y dos riesgos que
la Entrega 1 daba por aceptables dejaron de serlo. **No se reescribe `entrega-1`**: lo que decía era
cierto cuando se escribió, para una aplicación que solo corría en la red de casa. Se registra aquí
que ha dejado de serlo.

| # | Qué decía la Entrega 1 | Qué ocurre ahora | Por qué cambió |
|---|---|---|---|
| 15 | `seguridad.md:186` listaba *"sin rate limiting en la API (login, reset, PIN)"* como riesgo residual, con la mitigación propuesta *"throttling/back-off por IP y por cuenta"* | **Implementado exactamente así**: cinco endpoints, dos cubos (IP y cuenta), 429 con `Retry-After`. Ver [ADR-008](../entrega-1/02-technical-design/adr/ADR-008-rate-limiting-en-memoria-por-proceso.md) | Con la app en internet, reventar una contraseña permite **gastar** la clave de IA de esa familia, aunque nunca leerla: la API solo devuelve `has_api_key` |
| 16 | `seguridad.md:141` y `requisitos.md:619` aceptaban que `RF-SEG-04` (salir de la sesión del niño) fuese *"sin límite de intentos, igual que el resto de flujos de contraseña"* | `/auth/verify-password` limitado por usuario del token | Es la puerta que impide que el niño salga solo de su sesión, y la tiene delante con el dispositivo en la mano |
| 17 | `contratos-api.md:23-27,40` describe los endpoints de credenciales sin códigos de límite | Acepta `invite_code` en el alta y los cinco endpoints pueden devolver **429** (ver tabla abajo) | El registro estaba abierto a cualquiera con la URL. La regla vive en el servidor: sin `INVITE_CODE` definida, el alta se comporta como siempre |

**Contrato real de los endpoints de credenciales**, que sustituye a lo que describe
`contratos-api.md` para estas cinco rutas:

| Endpoint | Códigos nuevos | Límite (IP / cuenta) | Ventana |
|---|---|---|---|
| `POST /auth/register` | **403** código inválido · **429** | 5 / 3 por email | 60 min |
| `POST /auth/login` | **429** | 10 / 5 por email | 15 min |
| `POST /auth/reset-password` | **429** | 10 / 5 por email | 15 min |
| `POST /auth/verify-password` | **429** | 10 / 5 por usuario del token | 15 min |
| `POST /children/{id}/login` | **429** | 20 / 10 por `child_id` | 15 min |

Toda respuesta 429 incluye la cabecera **`Retry-After`** con los segundos que faltan, que
`contratos-api.md` no contempla porque en la Entrega 1 ningún endpoint la usaba. El cuerpo sigue el
formato `{"detail": "..."}` ya documentado, con un mensaje que **no revela si la cuenta existe**.

**Capacidades nuevas y su trazabilidad** (identificadores propios, sin editar la matriz de
`requisitos.md`, que pertenece a la Entrega 1):

| RF | Capacidad | Endpoint | Tests | Evidencia |
|---|---|---|---|---|
| `RF-SEG-05` | Código de invitación en el alta | `POST /auth/register` | `backend/tests/test_invite_code.py` (8) · `frontend/src/screens/CreateFamily.test.tsx` (2) | [verificacion.md](verificacion.md) |
| `RF-SEG-06` | Límite de intentos por IP y por cuenta | los cinco de credenciales | `test_rate_limit.py` (9) · `test_client_ip.py` (6) · `test_rate_limit_api.py` (12) · 4 de frontend | [verificacion.md](verificacion.md) |


### 3.d · Lo que solo se vio usando la app publicada (21-09-2026, noche)

Ninguno de estos fallos aparecía en desarrollo ni en la suite: los tres son **diferencias entre el
entorno local y la imagen de producción**. Detalle en [AI-LOG-011](../entrega-1/05-ai-log/decisiones.md).

| # | Qué fallaba | Por qué importaba | Resolución |
|---|---|---|---|
| 18 | El navegador servía el bundle del despliegue **anterior** | El formulario de alta salía sin el campo de código de invitación. nginx no mandaba cabeceras de caché, así que el navegador y el borde de Cloudflare no volvían a preguntar: durante una hora la pantalla se mostraba **sin que llegara ni una petición al servidor** | `index.html` con `no-store`; los assets, que llevan hash en el nombre, marcados inmutables |
| 19 | `VITE_API_URL` horneada en el `.env` del despliegue | La app publicada llamaba a `http://192.168.31.18:8000`: otro origen, `http` desde una página `https`, y un puerto ya cerrado. El navegador no daba código HTTP, solo error de red | Retirada del `.env`; el aviso ya estaba escrito en `docker-compose.yml` y ahora también en el manual |
| 20 | `??` donde hacía falta `||` al calcular la base de la API | El `Dockerfile` define `VITE_API_URL` como cadena **vacía**, y `??` solo cubre `undefined`: las peticiones salían a `/auth/register`, que nginx sirve como estático → **405**. En desarrollo la variable no existe, así que nunca se veía | `?.trim() \|\| "/api"`, con un test que recarga el módulo con la variable vacía |
| 21 | Ilustraciones de 1,5 a 3 MB por lección | A OpenAI no se le pedían formato ni calidad y devuelve PNG al máximo. Megas al móvil del niño en cada lección, y pagados | WebP con compresión 80 y calidad media: **74 KB** medidos. Extensión según el formato real y tipo MIME registrado; nginx sirve los medios sin buffering y cacheables un año |

Y cuatro divergencias más que deja este trabajo, encontradas al auditar la documentación contra el
código el 22-09:

| # | Qué dice la Entrega 1 | Realidad hoy |
|---|---|---|
| 22 | `arquitectura.md:138`: *"guardará la imagen en `media/lessons/{id}.png`"* | La extensión sigue al formato real del fichero. Con OpenAI se guarda **`.webp`**, y la app registra ese tipo MIME porque la imagen base del contenedor no lo traía |
| 23 | `arquitectura.md:149`: *"`ApiError(status, detail)`"* | Tiene un tercer campo, `retryAfter`, con los segundos del 429. Cinco pantallas lo distinguen del error de credenciales |
| 24 | `despliegue.md:11,29,36,46`: la API se expondría en el puerto **8000** a la red local | Atado a `127.0.0.1:8000`. Exponerlo permitiría falsificar la cabecera de IP en la que se apoya el límite de intentos |
| 25 | `despliegue.md:78,126-127`: receta de acceso por LAN con `VITE_API_URL=http://IP_DEL_PC:8000` | **Obsoleta y dañina.** Con el origen único no hace falta, y definirla ata el bundle a una máquina: fue la causa de uno de los fallos del 21-09. La tabla de variables tampoco recoge `INVITE_CODE`, `CLIENT_IP_HEADER` ni `RATE_LIMIT_ENABLED` |

Queda también ampliada, sin editarla, la **matriz de amenazas** de `seguridad.md` §4: no tenía fila
para la fuerza bruta contra credenciales ni para el alta abierta, que son los dos huecos que cubren
`RF-SEG-05` y `RF-SEG-06`. Y `historias-usuario.md:378` listaba el límite de intentos como fuera de
alcance: ya no lo está.

La #18 y la #19 comparten con la #7 y la #12 de la segunda tanda la misma moraleja: **el fallo
silencioso es la norma en esta aplicación**, y eso lo vuelve invisible también para quien opera. Lo
que los cazó fue leer los registros del servidor y contrastarlos con lo que mostraba la pantalla.


## 4. Deuda conocida

Se declara en lugar de ocultarse.

| Asunto | Estado | Decisión |
|---|---|---|
| `monthly_quota` nunca se comprueba | `used_count` se incrementa pero el límite no actúa: el contador existe, la cuota no | Se aborda en la Entrega 3, donde la cuota es necesaria de verdad (ver [diseño de demo pública](../superpowers/specs/2026-09-14-despliegue-demo-publica-design.md)) |
| Tier `managed` sin implementar | El modelo lo contempla; no hay claves a nivel de servidor | Entrega 3 |
| Migración a `httpx2` | 1 aviso de deprecación en la suite | No se toca a dos días de la entrega: `httpx` lo usan los proveedores de IA |
| Moderación como *blocklist* | Es un marcador de posición declarado, no un servicio real | Suficiente para el MVP; la costura permite sustituirlo |
| El PIN acepta dígitos Unicode (`١٢٣٤`) | `\d` de Python es Unicode-aware | Sin impacto: el formulario solo produce `[0-9]` y el PIN se hashea igual |
| ~~Sin despliegue público~~ | **Resuelto el 21-09-2026**: `https://chispa.chispalearn.com` por túnel de Cloudflare | Ver [demo pública](demo-publica.md) |
| El limitador vive en memoria del proceso | Los contadores mueren al reiniciar el contenedor, y el control se invalidaría **en silencio** si algún día hubiera varios procesos o réplicas | Aceptado: el backend arranca con un solo proceso. Disparador de revisión escrito en [ADR-008](../entrega-1/02-technical-design/adr/ADR-008-rate-limiting-en-memoria-por-proceso.md) |
| Un hermano puede agotar los intentos de PIN del otro | 10 fallos por niño en 15 minutos dejan fuera también al legítimo | Aceptado a cambio del control; el niño ve un mensaje amable, no un error técnico |
| `sudo` sin contraseña conocida en la VM de la demo | Impide actualizaciones de seguridad de Ubuntu | Pendiente: se recupera por consola VNC |
| ~~El panel no avisa si hay proveedor de imagen configurado pero desactivado~~ | Se podía guardar proveedor y clave con `image_enabled=false` y no ocurría nada, sin señal | **Resuelto el 27-09-2026.** El aviso se deriva del render, así que aparece también al *abrir* una configuración guardada así —el motivo por el que el fallo llevaba invisible desde el 15-09—. En el mismo trabajo se cerró un segundo fallo silencioso del mismo patrón: `image_provider` no se validaba contra el catálogo y un id inventado se guardaba con 200 (`RF-IA-06` lo declaraba); ahora 422 |
| Un alta falló una vez en la demo publicada y funcionó al reintentar | El 27-09-2026, tras cruzar Cloudflare Access, `POST /auth/register` mostró el mensaje genérico. **Causa raíz desconocida**: al reintentar funcionó y la evidencia se perdió (no se capturó la pestaña de red) | Mitigado, no resuelto. El cliente destruía el motivo real —`JSON.parse` sin protección antes de mirar `res.ok`, y `fetch` sigue las redirecciones, así que un corte de Access llega como 200 con HTML—. Ahora se lanza un `ApiError` con mensaje útil, así que **si reaparece, el siguiente lo verá**. Dos tests lo cubren |
| Voz de lectura robótica | `SpeakButton` no selecciona voz, así que usa la del sistema, que en Windows suele ser la antigua de SAPI5 | Decisión explícita del propietario: se deja como está |

## 5. Metodología

Construido con un flujo SDD propio (`.superpowers/sdd/`: brief → implementación → informe →
libro mayor), reforzado esta jornada con material adaptado de repositorios de referencia:

- **`docs/estandares/`** — estándares de proyecto adaptados de `lidr-specboot`, en español
  (el original impone *English Only*, incompatible con una entrega en español).
- **`.claude/skills/`** — seis skills: `chispa-brief`, `chispa-verificar`,
  `chispa-revision-adversaria`, `chispa-auditoria`, `chispa-bitacora`, `chispa-commit`.
- **TDD Guard** (`nizos/tdd-guard`) con reporters de pytest y vitest: hooks que **bloquean**
  escribir implementación sin un test que falle antes. No es una intención documentada; es una
  barrera que el programa aplica.

La cadena de verificación obligatoria (tests dirigidos → suite → migración reversible → `curl`
real → E2E con capturas → documentación → informe) viene de `openspec-tasks-mandatory-steps.md` y
convierte las evidencias en subproducto de cada tarea en lugar de en una tarea final.

Detalle en [`docs/estandares/verificacion.md`](../estandares/verificacion.md).

## 6. Qué demuestra que funciona

- [`verificacion.md`](verificacion.md) — salida real de suites, linters, Docker y `curl`.
- [`evidencias/`](evidencias/) — 16 capturas del recorrido completo y la salida literal del despliegue en Docker.
- `.superpowers/sdd/reports/task-panel-familia-report.md` — informe de la última tarea.
