# Seguridad (perspectiva OWASP) — Chispa

**Proyecto:** Chispa — Máster LIDR / AI4Devs · Entrega 1 (diseño técnico previo a la implementación)
**Ámbito:** aplicación educativa para **niños**. La privacidad y protección del menor es el requisito rector: cualquier decisión de diseño se resolverá, en caso de duda, a favor de la seguridad del niño.
**Naturaleza del documento:** diseño de seguridad de un proyecto **académico**. Los controles descritos son los que se **implementarán** (se nombran los componentes y funciones previstos), mientras que el alcance operativo (despliegue endurecido, TLS, monitorización, pentesting) será limitado y se declara honestamente en la sección de riesgos residuales.

> Convención: en este documento "familia" designa la cuenta del adulto/tutor (modelo `User` + `Family`), y "niño" designa el perfil supervisado (modelo `Child`). Son **dos superficies de identidad distintas**, deliberadamente aisladas.

---

## 1. Modelo de amenazas (resumen)

### 1.1 Activos a proteger

| Activo | Sensibilidad | Por qué importa |
|---|---|---|
| **Datos del menor** (nombre, avatar, edad/fecha de nacimiento, curiosidades que escribe, lecciones e historias generadas) | **Crítica** | Es un menor. La minimización y la no exposición son obligatorias. |
| **Credenciales de la familia** (contraseña del tutor, PIN del niño, código de recuperación) | Alta | Dan acceso a la cuenta y al perfil del menor. |
| **Claves de IA BYOK** (OpenAI, Gemini, HuggingFace… que la familia aporta) | Alta | Son secretos de terceros con coste económico si se filtran. |
| **Integridad del contenido educativo** (respuesta correcta del quiz, moderación) | Media | Su fuga permite trampas; su ausencia expone al niño a contenido inadecuado. |

### 1.2 Actores

| Actor | Intención | Capacidad asumida |
|---|---|---|
| **Niño** (usuario legítimo) | Aprender; puede escribir texto libre ("curiosidades") | Solo token de tipo `child`; no debe poder alcanzar funciones de administración. |
| **Familia / tutor** (usuario legítimo) | Administrar, supervisar y aprobar | Token de tipo `family`; controla configuración y aprobación parental. |
| **Atacante externo** | Robar datos del menor, credenciales o claves de IA; enumerar usuarios | Sin credenciales válidas; puede sondear la API, probar tokens, medir tiempos. |
| **Proveedor de IA / servicio externo** | Generación de texto e imagen | Semi-confiable: se le envía el concepto de la lección, **nunca** datos personales del niño. |

### 1.3 Superficies principales

- API REST del backend (FastAPI), con **dos familias de tokens** (familia / niño).
- Endpoint local de generación de imagen (SDXL/Automatic1111) apuntado por la propia familia → riesgo SSRF.
- Proveedores de IA externos (texto e imagen) con claves BYOK cifradas.

---

## 2. Controles por categoría OWASP Top 10

### A01 — Broken Access Control (control de acceso roto)

**Control 1 · JWT tipado (aislamiento familia ↔ niño).**
La función `create_token(subject, token_type, expires_minutes)` firmará con HS256 un payload `{"sub", "type", "exp"}`. En el módulo de dependencias de autenticación:
- `get_current_family_user` exigirá `payload["type"] == "family"`; si no, responderá `401 "Tipo de token inválido"` y cargará el `User`.
- `get_current_child` exigirá `payload["type"] == "child"` y cargará el `Child`.

El token de familia se emitirá en registro/login; el token de niño **solo** se emitirá tras verificar el PIN. Consecuencia: un token de niño **no podrá** invocar endpoints de familia y viceversa — las dos superficies quedarán aisladas por construcción, no por convención de rutas.

**Control 2 · Aislamiento de datos por propietario.**
Cada consulta filtrará explícitamente por el dueño del recurso, en los repositorios:
- Repositorio de lecciones → `get_for_child`: `if lesson is None or lesson.child_id != child_id: return None` (y `list_thread` volverá a filtrar por `child_id`).
- Repositorio de niños → `get_child_for_family`: `if child is None or child.family_id != family_id: return None`.
- Repositorio de historias → `get_for_child` (por `child_id`), `get_for_family` (comprobará que la historia pertenece a un `Child` de esa familia), y `list_for_family` (join `Child.family_id == family_id`).

Cuando el recurso no pertenezca al solicitante, los routers responderán **404** (no 403) para **no revelar la existencia** del recurso ajeno. Esto proporcionará aislamiento **entre familias** y **entre niños de la misma familia**.

### A02 — Cryptographic Failures (fallos criptográficos)

**Control 3 · Cifrado de claves de IA (Fernet).**
El servicio de cifrado (`crypto`) cifrará/descifrará con `Fernet(AI_CONFIG_KEY)`. `_resolve_key` lanzará `RuntimeError("AI_CONFIG_KEY no configurada")` si falta la clave (fail-closed: sin clave no se opera). Las claves BYOK se persistirán cifradas (`api_key_encrypted`, `image_api_key_encrypted`) y **nunca** se devolverán por la API: el esquema público solo expondrá los booleanos `has_api_key` / `has_image_api_key`. El descifrado (`_decrypt_key` en el módulo de proveedores de imagen) usará `except Exception: return None` para **no filtrar** detalles de error ni la clave.

**Control 8 · Hashing de credenciales.**
El módulo de seguridad usará `passlib.CryptContext(schemes=["bcrypt"])`. Tanto la contraseña de la familia (`password_hash`) como el PIN del niño (`pin_hash`) y el código de recuperación (`recovery_code_hash`) se almacenarán **hasheados con bcrypt** (salt + factor de coste). La verificación pasará por `verify_secret`.

### A03 — Injection (inyección)

- **SQL:** el acceso a datos será exclusivamente vía **SQLAlchemy ORM** con sentencias parametrizadas (`select(...).where(...)`, `db.get(...)`); no habrá concatenación de SQL. Se eliminará la superficie de inyección SQL clásica.
- **Validación de entrada:** los esquemas **Pydantic** validarán y tiparán los cuerpos de petición en la frontera de la API (coacción de tipos, campos esperados), reduciendo entradas malformadas.
- **Salida a proveedores IA:** el texto del niño se someterá a moderación (ver A04) antes de propagarse.

### A04 — Insecure Design (diseño inseguro) — núcleo de la protección del menor

**Control 4 · Moderación de la entrada del niño + degradación segura (requisito D6).**
El servicio de moderación → `check_curiosity(text)` comparará en minúsculas contra una `_BLOCKLIST` (`arma`, `armas`, `violencia`, `droga(s)`, `sexo`, `sexual`, `suicid`, `matar`, `porno`…). Si detecta un término, lanzará `ModerationError`; el router lo traducirá a **422** y la UI mostrará el mensaje amable *"Esta la vemos con un adulto"* 🛟. El niño no recibirá contenido sensible ni un error técnico.

**Degradación / fallback seguro del proveedor.** La generación de imagen será *best-effort*: si un proveedor falla o su URL no es válida, la fábrica `build_image_generator` caerá al `StubImageGenerator`. Principio de diseño explícito: *"el niño nunca ve un fallo del proveedor"*.

**Control 5 · El backend nunca enviará la respuesta correcta del quiz.**
`quiz_correct_index` y `quiz_explanation` **no se serializarán jamás**: el esquema `QuizPublic` expondrá únicamente `{question, options}`. La corrección se evaluará en servidor (`answer_lesson`). Esto prevendrá tanto las trampas como la fuga de la solución al cliente.

**Aprobación parental (supervisión por diseño).** El flujo contempla que ciertos contenidos (p. ej. historias) requieran aprobación de la familia antes de llegar al niño, reforzando el control humano sobre el material que consume el menor.

### A05 — Security Misconfiguration (configuración insegura)

**Control 2 (config) · Fail-closed del secreto JWT.**
La configuración definirá `INSECURE_DEFAULT_SECRET` y `DEV_ENVIRONMENTS = {development, dev, local, test, testing}`. El `model_validator` `_enforce_strong_secret_outside_dev` tratará **cualquier entorno cuyo nombre no esté en esa lista** como *production-class* y entonces:
- **rechazará** arrancar si `jwt_secret` sigue siendo el valor por defecto inseguro, y
- **exigirá** `len(jwt_secret) >= 32` (`MIN_SECRET_LENGTH`).

Será un **fail-closed**: un despliegue mal configurado no arrancará en lugar de arrancar débil.

**Expiración del token.** `jwt_expire_minutes = 60*24*30` (30 días). Es un valor alto, **justificado y consciente**: Chispa es una app familiar auto-alojada donde forzar reautenticación frecuente perjudicaría la experiencia del niño. Se documenta como trade-off usabilidad/seguridad (mitigable acortándolo si se despliega en entorno menos confiable).

**Otros endurecimientos de despliegue (Control 10).**
- **Contenedor no-root:** el Dockerfile ejecutará como usuario sin privilegios.
- **Ollama ligado a `127.0.0.1`:** el motor LLM local no se expondrá a la red.
- **Imágenes generadas fuera del control de versiones:** el contenido del menor no se filtrará al repositorio git.
- **CORS restringido** por `settings.cors_origins`.

### A07 — Identification and Authentication Failures

**Control 8 · bcrypt** para contraseña, PIN y código de recuperación (ver A02).

**Control 9 · Recuperación de contraseña sin email y anti-enumeración.**
En el servicio de autenticación (`auth_service`):
- `_new_recovery_code()` generará **128 bits** de entropía (`secrets.token_hex(16)`), formateado en grupos de 4 para copiarlo; se guardará hasheado con bcrypt.
- Se precomputará un `_DUMMY_HASH`. En `authenticate` y `reset_password`, si el email **no existe** (o no hay código), se ejecutará igualmente `verify_secret(..., _DUMMY_HASH)` para que el **coste temporal sea constante** — mitigando **enumeración de usuarios por timing**.
- El código de recuperación **rotará** tras cada reset exitoso (`reset_password` generará y guardará un `new_code`), evitando su reutilización.

Diseño sin email = menos PII almacenada y ausencia de superficie de phishing por correo (coherente con la minimización de datos).

### A10 — Server-Side Request Forgery (SSRF)

**Control 6 · Mitigación SSRF en el endpoint de imagen local.**
La función `validate_local_url()` (en el módulo de proveedores de imagen):
- rechazará esquemas que no sean `http`/`https` y URLs sin hostname;
- resolverá el host con `socket.getaddrinfo` y **rechazará direcciones link-local** (`169.254.0.0/16`, `fe80::/10`) — el objetivo típico de SSRF hacia **endpoints de metadatos de nube**;
- todos los clientes HTTP de imagen usarán `follow_redirects=False` (salvo Pollinations, servicio público de imagen), evitando redirecciones a destinos internos.

**Trade-off consciente y documentado:** `validate_local_url` **no** bloqueará `localhost` ni rangos privados (LAN), porque **apuntar al SDXL local del propio usuario es el uso previsto** de la función. La mitigación se centrará en el vector realmente peligroso (metadatos de nube vía link-local) sin romper el caso de uso legítimo. Si Chispa se desplegara en infraestructura cloud multiinquilino, esta política debería endurecerse.

---

## 3. Privacidad del menor

| Principio | Cómo se aplicará en Chispa |
|---|---|
| **Minimización de datos** | En el alta de la familia **no se recogerán datos del menor**; el perfil del niño se creará después con lo imprescindible (nombre, avatar, edad para adaptar el nivel). |
| **PIN en lugar de contraseña para el niño** | El niño accederá con un **PIN** (hasheado con bcrypt) tras el gesto del tutor; no gestionará una contraseña "adulta" ni email. Barrera de edad y de complejidad. |
| **Supervisión parental** | Superficies separadas (token `family` vs `child`), aprobación parental de contenido y configuración de IA en manos de la familia. |
| **No exposición a proveedores** | A los proveedores de IA se les enviará el **concepto de la lección**, no datos personales del niño (nota explícita prevista en `PollinationsImageGenerator`). |
| **Moderación de entrada** | El texto libre del niño pasará por `check_curiosity` antes de generar nada; el contenido sensible se derivará a "verlo con un adulto". |
| **No fuga de solución** | La respuesta correcta del quiz nunca saldrá del servidor. |

---

## 4. Matriz Amenaza → Control → Componente de diseño

| # | Amenaza | Control previsto | Componente de diseño (función) |
|---|---|---|---|
| 1 | Un token de niño accede a funciones de administración de la familia (o viceversa) | JWT **tipado** con verificación de `type` | Dependencias de auth · `get_current_family_user`, `get_current_child`; módulo de seguridad · `create_token` |
| 2 | Un usuario ve/edita datos de otra familia u otro niño (IDOR) | Filtrado por propietario + **404** en lugar de 403 | Repositorio de lecciones · `get_for_child`; repositorio de niños · `get_child_for_family`; repositorio de historias · `get_for_family`, `list_for_family` |
| 3 | Robo de claves BYOK de IA en base de datos o vía API | Cifrado **Fernet** + solo se exponen booleanos `has_*` | Servicio `crypto` · `encrypt`/`decrypt`/`_resolve_key`; proveedores de imagen · `_decrypt_key` |
| 4 | Robo/craqueo de contraseña, PIN o código de recuperación | Hash **bcrypt** con salt y coste | Módulo de seguridad · `hash_secret`/`verify_secret` |
| 5 | Enumeración de usuarios por diferencia de tiempos en login/reset | Hash **señuelo** de coste constante | Servicio `auth_service` · `_DUMMY_HASH`, `authenticate`, `reset_password` |
| 6 | Código de recuperación adivinable o reutilizable | 128 bits de entropía + **rotación** tras cada reset | Servicio `auth_service` · `_new_recovery_code`, `reset_password` |
| 7 | El niño introduce/recibe contenido inapropiado | **Moderación** por blocklist + mensaje amable (422) | Servicio de moderación · `check_curiosity`, `_BLOCKLIST` |
| 8 | El niño ve un error técnico del proveedor de IA | **Degradación** a stub (best-effort) | Proveedores de imagen · `build_image_generator`, `StubImageGenerator` |
| 9 | Fuga de la respuesta correcta del quiz al cliente | La corrección **no se serializa**; validación en servidor | Esquema `QuizPublic` (`{question, options}`); `answer_lesson` |
| 10 | SSRF hacia metadatos de nube vía URL de imagen | `validate_local_url` (bloqueo link-local) + `follow_redirects=False` | Proveedores de imagen · `validate_local_url`, adaptadores HTTP |
| 11 | Despliegue con secreto JWT por defecto o débil | **Fail-closed**: no arranca fuera de dev sin secreto propio ≥32 | Configuración · `_enforce_strong_secret_outside_dev` |
| 12 | Escalada de privilegios en el contenedor / exposición del LLM | Usuario **no-root**, Ollama en `127.0.0.1`, CORS restringido | Dockerfile; configuración · `cors_origins` |
| 13 | Inyección SQL / entradas malformadas | ORM parametrizado + validación **Pydantic** | SQLAlchemy `select().where()` en los repositorios; esquemas Pydantic |

---

## 5. Riesgos residuales y mejoras futuras

Coherente con su naturaleza de proyecto académico, quedan límites conocidos y honestamente declarados:

| Riesgo residual | Impacto | Mejora recomendada |
|---|---|---|
| **Fallback silencioso** de proveedores (`except → stub`/`None`) protege al niño de errores pero puede **ocultar fallos operativos** al administrador | Diagnóstico difícil; degradación inadvertida | Añadir **logging estructurado** del error absorbido (sin volcar secretos) y/o métricas, manteniendo el mensaje amable para el niño. |
| **Sin rate limiting** en la API (login, reset, PIN) | Fuerza bruta contra PIN/contraseña/código | Introducir throttling/back-off por IP y por cuenta (p. ej. límite de intentos de PIN). |
| **Moderación por blocklist** es básica (coincidencia de subcadenas, cobertura limitada, evadible con faltas ortográficas) | Falsos negativos / falsos positivos | Sustituir por un servicio de moderación real (misma firma `check_curiosity`) o modelo de clasificación; ya está previsto en el propio comentario del módulo. |
| **TLS/HTTPS** es responsabilidad del despliegue, no del código | Tráfico en claro si se despliega mal | Terminación TLS obligatoria (reverse proxy) documentada en la guía de despliegue. |
| **Expiración de token de 30 días** | Ventana amplia si un token se filtra | Acortar en despliegues menos confiables; considerar revocación/refresh. |
| **SSRF** permite localhost/LAN por diseño | Aceptable en auto-hosting; peligroso en cloud multiinquilino | Endurecer `validate_local_url` (allowlist explícita) si cambia el modelo de despliegue. |
| **Sin auditoría/2FA** para la cuenta de familia | Trazabilidad y robustez de la autenticación limitadas | Registro de accesos y, opcionalmente, segundo factor para el tutor. |

---

## 6. Conclusión

Chispa parte de un **modelo de amenazas centrado en el menor** y traduce ese principio en controles concretos de diseño que se implementarán: **aislamiento por tipo de token y por propietario** (A01), **cifrado Fernet y hashing bcrypt** (A02), **acceso a datos por ORM parametrizado y validación Pydantic** (A03), **moderación con degradación segura y no fuga de la solución del quiz** (A04), **arranque fail-closed y contenedor endurecido** (A05), **autenticación con anti-enumeración por timing** (A07) y **mitigación SSRF con trade-off documentado** (A10). Los controles previstos serán **sólidos para el alcance del proyecto**; las carencias (rate limiting, logging del fallback, moderación avanzada, TLS y auditoría) quedan **identificadas y priorizadas** como trabajo futuro desde el propio diseño.
