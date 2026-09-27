# Chispa ✨ — Entrega 1 · Producto

**Documento:** Especificación de requisitos (RF, RNF y trazabilidad)
**Proyecto:** Chispa (aprendizaje por curiosidad para niños)
**Alumno:** Germán González Pérez · **Máster:** LIDR – AI4Devs
**Repositorio:** github.com/ggonzalezperez/chispa (privado) · **Entrega 1:** 22 de julio de 2026

> Documentos relacionados: [PRD](prd.md) · [Historias de usuario](historias-usuario.md) · [Contratos de la API](../02-technical-design/contratos-api.md) · [Casos de aceptación](../03-testing/casos-aceptacion.md)

---

## Cómo leer este documento

Este documento recoge la **especificación de requisitos de Chispa antes de escribir código**. Está redactado en clave de propuesta (futuro): describe lo que el sistema **deberá** hacer y con qué criterios se considerará correcto, no lo que ya existe ni lo que se ha verificado.

- Un **requisito funcional (RF)** describe una capacidad concreta que el sistema deberá ofrecer (una entrada, una salida y unas reglas). Cada RF se traza a la(s) **historia(s) de usuario (US1–US11)** que lo motivan y condensa sus criterios de aceptación en formato **Given/When/Then (GWT)**, tomados de los escenarios Gherkin ya escritos en [historias-usuario.md](historias-usuario.md).
- Un **requisito no funcional (RNF)** describe una cualidad transversal del sistema (seguridad, rendimiento percibido, accesibilidad, portabilidad…) con un **criterio de verificación** comprobable.
- La relación con la **Definition of Ready (DoR)**: cada RF nace de una HU que ya cumple la plantilla de 6 bloques (contexto, alcance, funcional, validación, operativa y trazabilidad IA). Los RF concretan el bloque funcional en unidades verificables y sus GWT reutilizan el bloque de validación de cada HU.
- La **matriz de trazabilidad** (Parte 3) sirve un **doble propósito**: enlaza HU ↔ RF y, además, es la **base para el diseño de las pruebas funcionales** (pantalla + endpoint + prueba prevista por cada RF), que se desarrollarán en [casos-aceptacion.md](../03-testing/casos-aceptacion.md).

**Coherencia de modelo de datos:** todo lo aquí especificado se apoya en el modelo de **7 entidades** de la Entrega 1 (`families`, `users`, `children`, `lessons`, `knowledge_nodes`, `stories`, `family_ai_config`). No se introducen entidades adicionales.

**Prioridad:** Alta (núcleo o crítico de seguridad) · Media (valor relevante no bloqueante) · Baja (mejora incremental).

---

# PARTE 1 — Requisitos funcionales (RF)

## Módulo ONB — Onboarding y perfiles (US1)

### RF-ONB-01 — Crear cuenta familiar

| Campo | Descripción |
|---|---|
| **ID** | `RF-ONB-01` |
| **Módulo** | ONB — Onboarding y perfiles |
| **Nombre del requisito** | Crear cuenta familiar |
| **HU / CU relacionada** | US1 |
| **Descripción funcional** | El sistema deberá permitir a un adulto crear una cuenta familiar con nombre, email y contraseña. El alta hará autologin devolviendo un token de tipo `family` y, **una sola vez**, un código de recuperación con formato `XXXX-XXXX`. No se pedirán datos del menor. |
| **Entradas** | `RegisterRequest` `{name, email:EmailStr, password (≥8)}` vía `POST /auth/register`. |
| **Salidas esperadas** | `RegisterResult` `{access_token, token_type="bearer", recovery_code}`. El código de recuperación se mostrará una única vez. |
| **Criterios de aceptación (GWT)** | **Given** estoy en la pantalla de crear cuenta familiar **When** introduzco nombre, email y una contraseña de al menos 8 caracteres con confirmación coincidente **Then** se crea la cuenta, recibo un token de tipo `family` y se me muestra una sola vez un código `XXXX-XXXX`.<br>**Given** un email ya registrado **When** intento registrarme **Then** la respuesta es 409. |
| **Reglas de negocio** | Contraseña ≥8 caracteres. `users.email` único e indexado. El código de recuperación se almacena hasheado (`recovery_code_hash`) y se muestra una sola vez. Nunca se serializan `password_hash` ni `family_id`. |
| **Prioridad** | Alta |
| **Dependencias** | — |
| **Riesgos** | Pérdida del código de recuperación por el usuario (no hay email de respaldo): se mitiga con aviso explícito de guardado. |

### RF-ONB-02 — Validación de contraseña en cliente

| Campo | Descripción |
|---|---|
| **ID** | `RF-ONB-02` |
| **Módulo** | ONB — Onboarding y perfiles |
| **Nombre del requisito** | Validación de contraseña en cliente |
| **HU / CU relacionada** | US1 |
| **Descripción funcional** | El frontend deberá validar que la contraseña y su confirmación coinciden **antes** de llamar a la API, mostrando el error localmente. |
| **Entradas** | Campos de contraseña y confirmación en el formulario de alta. |
| **Salidas esperadas** | Mensaje de error en cliente si no coinciden; sin llamada a la API. |
| **Criterios de aceptación (GWT)** | **Given** estoy en la pantalla de crear cuenta familiar **When** la contraseña y su confirmación no coinciden **Then** se muestra un error antes de llamar a la API. |
| **Reglas de negocio** | La validación de coincidencia es previa al envío; la API sigue validando longitud y unicidad como fuente de verdad. |
| **Prioridad** | Media |
| **Dependencias** | `RF-ONB-01` |
| **Riesgos** | N/A |

### RF-ONB-03 — Alta de explorador (niño)

| Campo | Descripción |
|---|---|
| **ID** | `RF-ONB-03` |
| **Módulo** | ONB — Onboarding y perfiles |
| **Nombre del requisito** | Alta de explorador (niño) |
| **HU / CU relacionada** | US1 |
| **Descripción funcional** | La familia autenticada deberá poder dar de alta exploradores con avatar (SVG del set diseñado o generado por IA si la imagen está activa), alias, fecha de nacimiento (de la que se calcula la edad) y un PIN de 4 dígitos con confirmación. |
| **Entradas** | `ChildCreate` `{name, birthdate, pin, avatar="fox"}` vía `POST /children` con token `family`. |
| **Salidas esperadas** | `ChildRead` `{id, name, birthdate, avatar, avatar_image_url, age}`, con `age` derivada de `birthdate`. |
| **Criterios de aceptación (GWT)** | **Given** estoy autenticado como familia **When** añado un explorador con avatar, alias, fecha de nacimiento y un PIN de 4 dígitos (`^\d{4}$`) confirmado **Then** se crea el perfil con la edad calculada.<br>**Given** estoy añadiendo un explorador **When** el PIN no tiene exactamente 4 dígitos o no coincide con su confirmación **Then** se rechaza y no se crea el perfil. |
| **Reglas de negocio** | PIN debe cumplir `^\d{4}$` y coincidir con su confirmación. `pin_hash` con bcrypt. `age` es `@property`/`computed_field`, no columna. Nunca se serializan `pin_hash` ni `family_id`. Avatar generado por IA solo si la imagen está activa (ver `RF-PLT-03`). |
| **Prioridad** | Alta |
| **Dependencias** | `RF-ONB-01` |
| **Riesgos** | N/A |

### RF-ONB-04 — Acceso del niño con PIN

| Campo | Descripción |
|---|---|
| **ID** | `RF-ONB-04` |
| **Módulo** | ONB — Onboarding y perfiles |
| **Nombre del requisito** | Acceso del niño con PIN |
| **HU / CU relacionada** | US1 |
| **Descripción funcional** | Dentro de una sesión de familia autenticada, el niño deberá poder acceder introduciendo su PIN; un PIN correcto emitirá un token de tipo `child`. El alta de sesión del niño la autoriza el adulto. |
| **Entradas** | `ChildPinLogin` `{pin}` vía `POST /children/{id}/login` con token `family`. |
| **Salidas esperadas** | `Token` `{access_token, token_type}` con `type=child`. |
| **Criterios de aceptación (GWT)** | **Given** existe un explorador con PIN y la familia está autenticada en el dispositivo **When** el niño introduce el PIN correcto **Then** recibe un token de tipo `child`.<br>**Given** un PIN incorrecto **When** intento acceder **Then** la respuesta es 401. |
| **Reglas de negocio** | `POST /children/{id}/login` exige token de familia válido. El adulto abre la sesión del niño. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-ONB-03` |
| **Riesgos** | N/A |

### RF-ONB-05 — Cambio y recuperación de contraseña sin email

| Campo | Descripción |
|---|---|
| **ID** | `RF-ONB-05` |
| **Módulo** | ONB — Onboarding y perfiles |
| **Nombre del requisito** | Cambio y recuperación de contraseña sin email |
| **HU / CU relacionada** | US1 |
| **Descripción funcional** | La familia deberá poder cambiar su contraseña estando autenticada, y restablecerla sin email mediante el código de recuperación; el reset consumirá el código anterior y emitirá uno nuevo. |
| **Entradas** | `ChangePasswordRequest` `{current_password, new_password:min8}` (autenticado) · `ResetPasswordRequest` `{email, recovery_code, new_password:min8}` (sin auth). |
| **Salidas esperadas** | `{"status":"ok"}` en cambio · `RecoveryResult` `{recovery_code}` (nuevo) en reset. |
| **Criterios de aceptación (GWT)** | **Given** olvidé mi contraseña y tengo mi código `XXXX-XXXX` **When** lo introduzco junto a una nueva contraseña válida **Then** mi contraseña se restablece, puedo iniciar sesión y recibo un código nuevo.<br>**Given** una contraseña actual incorrecta **When** intento cambiarla **Then** la respuesta es 400. |
| **Reglas de negocio** | `reset-password` consume el `recovery_code_hash` anterior y rota a uno nuevo. Nueva contraseña ≥8. No hay servicio de email. |
| **Prioridad** | Media |
| **Dependencias** | `RF-ONB-01` |
| **Riesgos** | Si el usuario perdió el código, la cuenta no es recuperable: se mitiga con el aviso de guardado de `RF-ONB-01`. |

---

## Módulo APR — Bucle de aprendizaje (US2, US3, US4)

### RF-APR-01 — Crear lección desde una curiosidad o sugerencia

| Campo | Descripción |
|---|---|
| **ID** | `RF-APR-01` |
| **Módulo** | APR — Bucle de aprendizaje |
| **Nombre del requisito** | Crear lección desde una curiosidad o sugerencia |
| **HU / CU relacionada** | US2 |
| **Descripción funcional** | El niño deberá poder crear una lección a partir de una curiosidad escrita (`POST /lessons`) o desde una de las sugerencias propuestas (`GET /me/suggestions`); tras crearla, la app navegará a la lección. |
| **Entradas** | `LessonCreate` `{curiosity:2-300, subject?}` con token `child`; o selección de una `Suggestion` `{curiosity, emoji}`. |
| **Salidas esperadas** | `LessonRead` (sin `quiz_correct_index` ni `quiz_explanation`); 5 sugerencias. |
| **Criterios de aceptación (GWT)** | **Given** estoy autenticado como niño en la pantalla de encender la chispa **When** envío una curiosidad **Then** se crea una lección (`POST /lessons`) y la app navega a ella.<br>**Given** veo "Islas para empezar" (`GET /me/suggestions`) **When** pincho una sugerencia **Then** se crea y se abre una lección para ese tema.<br>**Given** vuelvo a la pantalla de encender la chispa **Then** las sugerencias no son siempre las mismas: se muestra una muestra distinta de un repertorio mayor. |
| **Reglas de negocio** | La curiosidad debe tener 2–300 caracteres. El endpoint exige token `child`. La moderación de entrada puede bloquear con 422 (ver `RF-SEG-03`). **Corregido en implementación (15-09-2026):** las sugerencias eran 5 fijas y la pantalla de inicio resultaba idéntica en cada visita; ahora se sirve una muestra aleatoria de 5 sobre un repertorio de 25 que cubre las cinco materias. Mientras se espera la respuesta se muestra un indicador de actividad (ver `RNF-07`). |
| **Prioridad** | Alta |
| **Dependencias** | — |
| **Riesgos** | N/A |

### RF-APR-02 — Lección determinista en modo stub

| Campo | Descripción |
|---|---|
| **ID** | `RF-APR-02` |
| **Módulo** | APR — Bucle de aprendizaje |
| **Nombre del requisito** | Lección determinista en modo stub |
| **HU / CU relacionada** | US2 |
| **Descripción funcional** | Sin proveedor de IA configurado (modo demo), la generación de la lección deberá ser **determinista** y respetar el contrato pedagógico: materia acotada y quiz de exactamente 3 opciones. |
| **Entradas** | Curiosidad del niño con `provider=stub` (por defecto). |
| **Salidas esperadas** | Lección con `subject ∈ {ciencia, matematicas, lenguaje, arte, cultura}`, quiz de exactamente 3 opciones e índice correcto en `0..2`. |
| **Criterios de aceptación (GWT)** | **Given** no hay proveedor de IA configurado (modo demo) **When** se genera una lección **Then** su `subject` está en {ciencia, matematicas, lenguaje, arte, cultura}, el quiz tiene exactamente 3 opciones y el índice correcto está entre 0 y 2. |
| **Reglas de negocio** | El stub es reproducible (mismo input → mismo output). El contrato pedagógico lo fija el sistema, no el prompt. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-APR-01` |
| **Riesgos** | N/A |

### RF-APR-03 — Lección adaptada por banda de edad

| Campo | Descripción |
|---|---|
| **ID** | `RF-APR-03` |
| **Módulo** | APR — Bucle de aprendizaje |
| **Nombre del requisito** | Lección adaptada por banda de edad |
| **HU / CU relacionada** | US3 |
| **Descripción funcional** | El contenido de la lección deberá adaptarse a la banda de edad del explorador (3–5 / 6–8 / 9–12): una sola idea con analogía, un dato sorprendente y 2–3 follow-ups. |
| **Entradas** | `children.age` (derivada de `birthdate`) y la curiosidad. |
| **Salidas esperadas** | `lessons.body` adaptado a la banda, `lessons.fun_fact` y `lessons.follow_ups` (2–3, `nullable`). |
| **Criterios de aceptación (GWT)** | **Given** soy un explorador con una edad concreta **When** abro una lección **Then** su contenido corresponde a mi banda de edad (3-5, 6-8 o 9-12) y presenta una sola idea con analogía, un dato sorprendente y 2 o 3 follow-ups. |
| **Reglas de negocio** | La banda se deriva de `children.age`. Una sola idea por lección (aprendizaje corto y recordable). |
| **Prioridad** | Alta |
| **Dependencias** | `RF-APR-01` |
| **Riesgos** | N/A |

### RF-APR-04 — Lectura de la lección en voz alta

| Campo | Descripción |
|---|---|
| **ID** | `RF-APR-04` |
| **Módulo** | APR — Bucle de aprendizaje |
| **Nombre del requisito** | Lectura de la lección en voz alta |
| **HU / CU relacionada** | US3 |
| **Descripción funcional** | La lección deberá poder leerse en voz alta con Web Speech Synthesis, en el idioma activo; si el navegador no soporta síntesis de voz, el control no se mostrará (degradación elegante). |
| **Entradas** | Acción sobre el botón 🔊; idioma activo del contexto i18n. |
| **Salidas esperadas** | Reproducción de audio de la lección en el idioma activo; sin control si no hay soporte. |
| **Criterios de aceptación (GWT)** | **Given** estoy en una lección y el navegador soporta síntesis de voz **When** pulso el botón 🔊 **Then** la lección se lee con Web Speech Synthesis en el idioma activo.<br>**Given** un navegador sin síntesis de voz **Then** el botón 🔊 no ofrece lectura y la lección se lee en pantalla. |
| **Reglas de negocio** | Best-effort: solo se ofrece con soporte del navegador. El texto canónico se mantiene siempre en pantalla. |
| **Prioridad** | Media |
| **Dependencias** | `RF-APR-03` |
| **Riesgos** | Variabilidad de voces/soporte entre navegadores: se mitiga ocultando el control cuando no hay soporte. |

### RF-APR-05 — Responder el reto (quiz)

| Campo | Descripción |
|---|---|
| **ID** | `RF-APR-05` |
| **Módulo** | APR — Bucle de aprendizaje |
| **Nombre del requisito** | Responder el reto (quiz) |
| **HU / CU relacionada** | US4 |
| **Descripción funcional** | El niño deberá poder responder el reto de la lección (`POST /lessons/{id}/answer`); al acertar subirá la maestría del nodo de conocimiento; al fallar no se penaliza. |
| **Entradas** | `AnswerRequest` `{choice_index}` con token `child`. |
| **Salidas esperadas** | `AnswerResult` `{correct, explanation, concept}`. Al acertar, `lessons.answered=true` y `knowledge_nodes.mastery` incrementa. |
| **Criterios de aceptación (GWT)** | **Given** estoy resolviendo el reto **When** respondo correctamente **Then** `correct=true` y sube la maestría del `KnowledgeNode` asociado.<br>**Given** estoy resolviendo el reto **When** respondo de forma incorrecta **Then** `correct=false` y no se penaliza mi maestría.<br>**Given** una lección inexistente o ajena **When** intento responder **Then** la respuesta es 404. |
| **Reglas de negocio** | La corrección se calcula solo en servidor. *Upsert* del nodo por `concept`+`subject`. No existe descenso de maestría. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-APR-01` |
| **Riesgos** | N/A |

---

## Módulo CON — Conocimiento vivo (US7, US8)

### RF-CON-01 — Isla automática al crear lección

| Campo | Descripción |
|---|---|
| **ID** | `RF-CON-01` |
| **Módulo** | CON — Conocimiento vivo |
| **Nombre del requisito** | Isla automática al crear lección |
| **HU / CU relacionada** | US8 |
| **Descripción funcional** | Al crear una lección, el sistema deberá crear automáticamente una isla (`knowledge_node`) para ese tema, aun sin responder el quiz; `GET /me/knowledge` la deberá devolver. |
| **Entradas** | Creación de lección (`RF-APR-01`). |
| **Salidas esperadas** | `list[KnowledgeNodeRead]` con al menos un nodo para el tema recién creado. |
| **Criterios de aceptación (GWT)** | **Given** enciendo una chispa y se crea una lección **When** consulto `GET /me/knowledge` sin haber respondido el quiz **Then** aparece 1 nodo (isla) para ese tema. |
| **Reglas de negocio** | 1 isla por tema al crear la lección. `knowledge_nodes.root_lesson_id` enlaza a la conversación. Aislamiento por `child_id`. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-APR-01` |
| **Riesgos** | N/A |

### RF-CON-02 — Buscador del archipiélago

| Campo | Descripción |
|---|---|
| **ID** | `RF-CON-02` |
| **Módulo** | CON — Conocimiento vivo |
| **Nombre del requisito** | Buscador del archipiélago |
| **HU / CU relacionada** | US7 |
| **Descripción funcional** | El niño deberá poder buscar sus islas por texto de forma insensible a acentos y mayúsculas; el mensaje "sin resultados" solo aparecerá si ya tiene al menos una isla. |
| **Entradas** | Texto de búsqueda; conjunto de islas del niño (`GET /me/knowledge`). |
| **Salidas esperadas** | Islas cuyo `concept` coincide de forma tolerante; mensaje de vacío condicionado. |
| **Criterios de aceptación (GWT)** | **Given** tengo varias islas **When** busco un texto (con o sin acentos, en mayúsculas o minúsculas) **Then** se muestran las islas cuyo nombre coincide de forma insensible.<br>**Given** tengo al menos una isla **When** mi búsqueda no coincide **Then** se muestra "sin resultados"; **But** si no tengo ninguna isla, no se muestra ese mensaje. |
| **Reglas de negocio** | Normalización de texto (sin acentos) resuelta en cliente. Aislamiento por `child_id`. |
| **Prioridad** | Media |
| **Dependencias** | `RF-CON-01` |
| **Riesgos** | N/A |

### RF-CON-03 — Reabrir la conversación guardada de una isla

| Campo | Descripción |
|---|---|
| **ID** | `RF-CON-03` |
| **Módulo** | CON — Conocimiento vivo |
| **Nombre del requisito** | Reabrir la conversación guardada de una isla |
| **HU / CU relacionada** | US7 |
| **Descripción funcional** | Al pinchar una isla, el sistema deberá abrir su conversación guardada a partir de `knowledge_nodes.root_lesson_id`. |
| **Entradas** | Selección de una isla del mapa; `root_lesson_id` del nodo. |
| **Salidas esperadas** | Apertura de la lección/hilo raíz asociado a la isla. |
| **Criterios de aceptación (GWT)** | **Given** veo una isla en el mapa **When** la pincho **Then** se abre su conversación guardada (`root_lesson_id`).<br>**Given** una isla de otro niño **When** intento abrirla **Then** no es accesible (aislamiento por `child_id`). |
| **Reglas de negocio** | Enlace lógico vía `root_lesson_id`. Un niño solo accede a sus propias islas. |
| **Prioridad** | Media |
| **Dependencias** | `RF-CON-01` |
| **Riesgos** | N/A |

### RF-CON-04 — Repreguntar en el hilo con contexto

| Campo | Descripción |
|---|---|
| **ID** | `RF-CON-04` |
| **Módulo** | CON — Conocimiento vivo |
| **Nombre del requisito** | Repreguntar en el hilo con contexto |
| **HU / CU relacionada** | US8 |
| **Descripción funcional** | El niño deberá poder seguir preguntando en el mismo hilo (`POST /lessons/{root}/ask`), creando un turno con `parent_id`/`root_id` que mantiene el contexto; `GET /lessons/{root}/thread` deberá devolver los turnos en orden, con la raíz primero. |
| **Entradas** | `LessonCreate` `{curiosity:2-300, subject?}` sobre `POST /lessons/{id}/ask`; consulta `GET /lessons/{id}/thread`. |
| **Salidas esperadas** | `LessonRead` (nuevo turno); `list[LessonRead]` en orden (raíz primero). |
| **Criterios de aceptación (GWT)** | **Given** tengo una lección raíz **When** repregunto (`POST /lessons/{root}/ask`) **Then** se crea un turno con `parent_id` y `root_id` manteniendo el contexto.<br>**Given** una conversación con varios turnos **When** consulto `GET /lessons/{root}/thread` **Then** los turnos se devuelven en orden, con la raíz primero.<br>**Given** una lección inexistente o ajena **When** repregunto **Then** la respuesta es 404. |
| **Reglas de negocio** | `parent_id`/`root_id` son enteros lógicos (sin FK), resueltos por consulta. Moderación puede bloquear con 422. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-APR-01` |
| **Riesgos** | N/A |

### RF-CON-05 — La maestría solo sube con el reto acertado

| Campo | Descripción |
|---|---|
| **ID** | `RF-CON-05` |
| **Módulo** | CON — Conocimiento vivo |
| **Nombre del requisito** | La maestría solo sube con el reto acertado |
| **HU / CU relacionada** | US8 |
| **Descripción funcional** | Repreguntar en el hilo no deberá modificar la maestría; solo el quiz respondido correctamente la incrementa. |
| **Entradas** | Repreguntas en el hilo sin responder quiz. |
| **Salidas esperadas** | `knowledge_nodes.mastery` inalterada tras repreguntar. |
| **Criterios de aceptación (GWT)** | **Given** estoy en una conversación **When** repregunto sin responder ningún quiz correctamente **Then** mi maestría no cambia; **And** solo el quiz respondido correctamente la sube. |
| **Reglas de negocio** | Única vía de incremento de maestría: `RF-APR-05`. |
| **Prioridad** | Media |
| **Dependencias** | `RF-APR-05` |
| **Riesgos** | N/A |

---

## Módulo CUE — Cuentos (US9)

### RF-CUE-01 — Crear cuento (queda pendiente)

| Campo | Descripción |
|---|---|
| **ID** | `RF-CUE-01` |
| **Módulo** | CUE — Cuentos |
| **Nombre del requisito** | Crear cuento (queda pendiente) |
| **HU / CU relacionada** | US9 |
| **Descripción funcional** | El niño deberá poder crear un cuento (`POST /me/stories`) que quedará en estado `pending` y no aparecerá en su lista ni en su detalle (404) hasta ser aprobado. El cuento se **genera a partir de su propio archipiélago** (sus `knowledge_nodes`, su nombre y su edad): el niño no escribe el texto, lo protagoniza. |
| **Entradas** | Ninguna en el cuerpo de la petición: solo el token `child`. El contexto (nombre, edad y conceptos ya explorados) lo aporta el servidor. |
| **Salidas esperadas** | `StoryRead` con `status=pending`; el niño solo lista sus cuentos `approved`. |
| **Criterios de aceptación (GWT)** | **Given** estoy autenticado como niño **When** creo un cuento (`POST /me/stories`) **Then** queda en estado `pending` y no aparece en mi lista ni en mi detalle (404) hasta ser aprobado. |
| **Reglas de negocio** | Aprobación parental obligatoria. Estado inicial `pending`. `stories.child_id` base del aislamiento. |
| **Prioridad** | Media |
| **Dependencias** | — |
| **Riesgos** | N/A |

### RF-CUE-02 — Aprobar/editar cuento

| Campo | Descripción |
|---|---|
| **ID** | `RF-CUE-02` |
| **Módulo** | CUE — Cuentos |
| **Nombre del requisito** | Aprobar/editar cuento |
| **HU / CU relacionada** | US9 |
| **Descripción funcional** | La familia deberá poder aprobar un cuento (`PUT /family/stories/{id}` con `action=approve`), pudiendo editar `title`/`body`; tras aprobarlo el niño ya lo verá. |
| **Entradas** | `{action: approve, title?, body?}` con token `family`. |
| **Salidas esperadas** | `StoryRead` con `status=approved` y `reviewed_at` fijado. |
| **Criterios de aceptación (GWT)** | **Given** hay un cuento pendiente **When** la familia lo aprueba (`action=approve`) editando título o cuerpo **Then** el cuento pasa a aprobado y el niño ya lo ve. |
| **Reglas de negocio** | Flujo `pending → approved`. Se registra `reviewed_at`. El texto que ve el niño es el canónico aprobado. |
| **Prioridad** | Media |
| **Dependencias** | `RF-CUE-01` |
| **Riesgos** | N/A |

### RF-CUE-03 — Rechazar cuento

| Campo | Descripción |
|---|---|
| **ID** | `RF-CUE-03` |
| **Módulo** | CUE — Cuentos |
| **Nombre del requisito** | Rechazar cuento |
| **HU / CU relacionada** | US9 |
| **Descripción funcional** | La familia deberá poder rechazar un cuento (`action=reject`): quedará en estado `rejected` y conservará su texto original. |
| **Entradas** | `{action: reject}` con token `family`. |
| **Salidas esperadas** | `StoryRead` con `status=rejected` y texto original intacto. |
| **Criterios de aceptación (GWT)** | **Given** hay un cuento pendiente **When** la familia lo rechaza (`action=reject`) **Then** el cuento queda en estado `rejected` y conserva su texto original. |
| **Reglas de negocio** | Flujo `pending → rejected`. Se registra `reviewed_at`. No se altera el texto al rechazar. |
| **Prioridad** | Media |
| **Dependencias** | `RF-CUE-01` |
| **Riesgos** | N/A |

---

## Módulo IA — IA configurable (US10)

### RF-IA-01 — Configuración por defecto (modo demo)

| Campo | Descripción |
|---|---|
| **ID** | `RF-IA-01` |
| **Módulo** | IA — IA configurable |
| **Nombre del requisito** | Configuración por defecto (modo demo) |
| **HU / CU relacionada** | US10 |
| **Descripción funcional** | Una familia sin configurar deberá quedar en modo demo: `tier=free`, `provider=stub`, `has_api_key=false`. |
| **Entradas** | `GET /family/ai-config` con token `family`. |
| **Salidas esperadas** | `AIConfigRead` con `tier=free`, `provider=stub`, `has_api_key=false` (nunca claves). |
| **Criterios de aceptación (GWT)** | **Given** no he configurado nada **When** consulto la configuración de IA **Then** `tier=free`, `provider=stub` y `has_api_key=false`. |
| **Reglas de negocio** | Relación 1:1 con la familia (`family_ai_config.family_id` único). Imagen por defecto `none`/`image_enabled=false`. |
| **Prioridad** | Alta |
| **Dependencias** | — |
| **Riesgos** | N/A |

### RF-IA-02 — BYOK con clave cifrada

| Campo | Descripción |
|---|---|
| **ID** | `RF-IA-02` |
| **Módulo** | IA — IA configurable |
| **Nombre del requisito** | BYOK con clave cifrada |
| **HU / CU relacionada** | US10 |
| **Descripción funcional** | Al guardar un proveedor con clave propia (BYOK), `has_api_key` deberá pasar a `true` y la respuesta nunca deberá contener la clave; se almacenará cifrada con Fernet. |
| **Entradas** | `AIConfigUpdate` `{tier, provider, api_key?, ...}` vía `PUT /family/ai-config`. |
| **Salidas esperadas** | `AIConfigRead` con `has_api_key=true`, sin `api_key_encrypted`. |
| **Criterios de aceptación (GWT)** | **Given** quiero usar Claude **When** guardo `provider=claude` con mi `api_key` **Then** `has_api_key` pasa a `true` y la respuesta NO contiene la clave (se almacena cifrada con Fernet).<br>**Given** falta `AI_CONFIG_KEY` **When** intento cifrar **Then** la respuesta es 400.<br>**Given** pego algo que no tiene la forma de una clave del proveedor **When** guardo **Then** la respuesta es 422 y se explica qué prefijo se esperaba. |
| **Reglas de negocio** | Claves en claro solo en la petición de escritura; cifrado Fernet antes de persistir; requiere `AI_CONFIG_KEY`. **Añadido en implementación (15-09-2026):** antes de cifrar se comprueba la **forma** de la clave (`sk-` OpenAI y compatibles, `sk-ant-` Claude, `AIza` Gemini, `hf_` HuggingFace). Es una comprobación de forma, no de validez: no dice si la clave funciona, solo descarta lo que no puede funcionar. Sin ella una clave errónea se aceptaba, el proveedor devolvía 401, el `except` lo absorbía y el niño recibía lecciones del stub mientras la familia creía estar usando —y pagando— la IA que configuró. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-IA-01` |
| **Riesgos** | Fuga de clave si se serializara por error: mitigado por el esquema (solo booleanos) y `AI_CONFIG_KEY` obligatoria. |

### RF-IA-03 — Rechazo de proveedor deshabilitado

| Campo | Descripción |
|---|---|
| **ID** | `RF-IA-03` |
| **Módulo** | IA — IA configurable |
| **Nombre del requisito** | Rechazo de proveedor deshabilitado |
| **HU / CU relacionada** | US10 |
| **Descripción funcional** | Intentar guardar un `tier`/`provider` fuera del conjunto válido deberá devolver 422. **El mismo código cubre ahora una segunda causa**: una clave cuya forma no corresponde al proveedor (ver `RF-IA-02`). El cuerpo de la respuesta distingue ambos casos. |
| **Entradas** | `AIConfigUpdate` con proveedor no habilitado. |
| **Salidas esperadas** | Respuesta 422. |
| **Criterios de aceptación (GWT)** | **Given** intento configurar un proveedor no habilitado **When** guardo la configuración **Then** la respuesta es 422. |
| **Reglas de negocio** | `tier ∈ {free, byok, managed}`, `provider ∈ {stub, ollama, claude, openai, gemini, deepseek, kimi}`; valor fuera del conjunto habilitado → 422. |
| **Prioridad** | Media |
| **Dependencias** | `RF-IA-01` |
| **Riesgos** | N/A |

### RF-IA-04 — Recomendador de modelo local por hardware

| Campo | Descripción |
|---|---|
| **ID** | `RF-IA-04` |
| **Módulo** | IA — IA configurable |
| **Nombre del requisito** | Recomendador de modelo local por hardware |
| **HU / CU relacionada** | US10 |
| **Descripción funcional** | La familia deberá poder recibir una recomendación de modelo local acorde a su hardware (`POST /family/ai-config/recommend`) según VRAM/RAM disponibles. |
| **Entradas** | `HardwareQuery` `{vram_gb≥0, ram_gb≥0}`. |
| **Salidas esperadas** | `Recommendation` `{can_run_local, fits, recommended, note}`. |
| **Criterios de aceptación (GWT)** | **Given** quiero un modelo local **When** envío mi VRAM y RAM (`POST /family/ai-config/recommend`) **Then** recibo una recomendación de modelo acorde a mi hardware. |
| **Reglas de negocio** | No descarga ni instala modelos; solo orienta la elección. |
| **Prioridad** | Baja |
| **Dependencias** | `RF-IA-01` |
| **Riesgos** | N/A |

### RF-IA-05 — Proveedores de texto

| Campo | Descripción |
|---|---|
| **ID** | `RF-IA-05` |
| **Módulo** | IA — IA configurable |
| **Nombre del requisito** | Proveedores de texto |
| **HU / CU relacionada** | US10 |
| **Descripción funcional** | El catálogo de proveedores de texto ofrece `stub`, Ollama (local), Claude y **OpenAI** habilitados; Gemini/DeepSeek/Kimi quedan previstos pero no habilitados. |
| **Entradas** | `GET /family/ai-config/catalog` con token `family`. |
| **Salidas esperadas** | `{providers, ollama_models, default_local_model, image_providers}` con el estado de habilitación por proveedor. |
| **Criterios de aceptación (GWT)** | **Given** consulto el catálogo de IA **When** reviso los proveedores de texto **Then** `stub`, Ollama, Claude y OpenAI figuran habilitados y Gemini/DeepSeek/Kimi figuran previstos pero no habilitados. |
| **Reglas de negocio** | Los proveedores no habilitados se rechazan en el `PUT` con 422 (ver `RF-IA-03`). Degradación elegante al `stub`. Los identificadores de modelo se verifican contra la documentación del proveedor, no de memoria: se actualizaron en 09-2026 porque los originales (`gpt-4o`) eran de 2024. |
| **Prioridad** | Media |
| **Dependencias** | `RF-IA-02` |
| **Riesgos** | N/A |

### RF-IA-06 — Proveedores de imagen

| Campo | Descripción |
|---|---|
| **ID** | `RF-IA-06` |
| **Módulo** | IA — IA configurable |
| **Nombre del requisito** | Proveedores de imagen |
| **HU / CU relacionada** | US10 |
| **Descripción funcional** | El catálogo de imagen deberá contemplar HuggingFace, SDXL local, OpenAI, Gemini y Pollinations; Ollama no genera imágenes. La generación estará desactivada por defecto. |
| **Entradas** | `AIConfigUpdate` `{image_provider, image_api_key?, image_enabled=false, ...}`. |
| **Salidas esperadas** | `AIConfigRead` con `image_provider`, `image_enabled`, `has_image_api_key` (nunca la clave de imagen). |
| **Criterios de aceptación (GWT)** | **Given** configuro un proveedor de imagen con clave **When** guardo la configuración **Then** `has_image_api_key=true` y la respuesta no contiene la clave de imagen.<br>**Given** el estado por defecto **Then** `image_provider=none` e `image_enabled=false`. |
| **Reglas de negocio** | `image_provider ∈ {none, huggingface, local_sdxl, openai, gemini, pollinations}`. Clave de imagen cifrada con Fernet. Ollama no genera imágenes. |
| **Prioridad** | Baja |
| **Dependencias** | `RF-IA-02` |
| **Riesgos** | SSRF en el endpoint de imagen local: mitigado (ver `RNF-02`). |

---

## Módulo PLT — Plataforma y accesibilidad (US5/US6, US11)

### RF-PLT-01 — Panel de familia (actividad, historial y ficha)

| Campo | Descripción |
|---|---|
| **ID** | `RF-PLT-01` |
| **Módulo** | PLT — Plataforma y accesibilidad |
| **Nombre del requisito** | Panel de familia (actividad, historial y ficha) |
| **HU / CU relacionada** | US5/US6 |
| **Descripción funcional** | La familia deberá disponer de un panel que muestre la actividad y la ficha del niño (conceptos fuertes/emergentes), con selector de niño. |
| **Entradas** | `GET /children/{id}/profile` y `GET /children/{id}/knowledge`, ambos con token `family`; selección de niño. |
| **Salidas esperadas** | `ChildProfile` `{name, age, islands, avatar, avatar_image_url}` y ficha con conceptos por `mastery`. |
| **Criterios de aceptación (GWT)** | **Given** estoy autenticado como familia con al menos un niño **When** abro el panel y selecciono un niño **Then** veo su actividad e historial y su ficha de conocimiento con conceptos fuertes y emergentes.<br>**Given** tengo varios niños **When** cambio de niño en el selector **Then** el panel muestra los datos del niño seleccionado. |
| **Reglas de negocio** | `islands` es campo derivado = número de `knowledge_nodes` del niño. El selector no mezcla información entre hijos. La familia solo ve a sus niños (cruzado → 404). **Fuerte vs emergente se deriva de `mastery`**: la isla nace con `mastery = 1` al encender la chispa y solo sube al acertar el reto, así que `mastery >= 2` es *dominado* y `mastery == 1` es *emergente*. **Nota de implementación:** el panel NO puede servirse desde `/me/*`, que exige token `child` por diseño (JWT tipado); de ahí los endpoints propios de familia. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-CON-01` |
| **Riesgos** | N/A |

### RF-PLT-02 — Dictado de la pregunta por voz

| Campo | Descripción |
|---|---|
| **ID** | `RF-PLT-02` |
| **Módulo** | PLT — Plataforma y accesibilidad |
| **Nombre del requisito** | Dictado de la pregunta por voz |
| **HU / CU relacionada** | US11 |
| **Descripción funcional** | El niño deberá poder dictar su curiosidad por voz (Web Speech API, multiidioma) y, al terminar de hablar, la pregunta deberá enviarse sola sin pulsar ningún botón más; si el navegador no soporta reconocimiento de voz, el botón de micrófono no se mostrará. |
| **Entradas** | Acción sobre el botón 🎤; idioma activo. |
| **Salidas esperadas** | Transcripción de la voz como texto de la curiosidad en el idioma activo; sin control si no hay soporte. |
| **Criterios de aceptación (GWT)** | **Given** el navegador soporta la Web Speech API **When** pulso el micrófono 🎤 y hablo **Then** mi voz se transcribe en el idioma activo como texto de la curiosidad.<br>**Given** un navegador sin reconocimiento de voz **Then** el botón de micrófono no se muestra.<br>**Given** pulso el micrófono **Then** el botón indica visiblemente que está escuchando.<br>**Given** el reconocimiento falla **Then** se explica el motivo (permiso denegado, sin micrófono, sin conexión, no se oyó nada) en lugar de no ocurrir nada.<br>**Given** la transcripción devuelve texto **Then** la pregunta se envía sola, sin pulsar el botón de enviar.<br>**Given** la transcripción viene vacía **Then** no se envía nada.<br>**Given** la app se sirve sin contexto seguro (http por IP de la red local) **Then** se explica que la voz necesita conexión segura, en vez de pedir un permiso que el navegador nunca va a ofrecer. |
| **Reglas de negocio** | Best-effort: solo con soporte del navegador. Usa el idioma activo (ver `RF-PLT-05`). **Corregido en implementación (15-09-2026):** el manejador de error descartaba la causa, así que cualquier fallo terminaba igual —el botón parpadeaba y volvía a su sitio sin decir nada— y era imposible saber qué pasaba. Los códigos de la Web Speech API se traducen ahora a cinco mensajes distintos. El fallo silencioso sigue valiendo para el proveedor de IA, pero no para un permiso que el adulto puede conceder. |
| **Prioridad** | Baja |
| **Dependencias** | `RF-APR-01` |
| **Riesgos** | Precisión de reconocimiento variable entre navegadores. **Cambio de mitigación (15-09-2026):** hasta ahora se mitigaba dejando editar el texto transcrito antes de enviarlo, pero ese segundo paso era fricción real para un niño pequeño —ya había hablado con Chispa y la app no reaccionaba—, así que el dictado pasa a enviarse solo y se acepta el riesgo de transcripción imperfecta. Queda mitigado en parte: el texto sigue visible en el campo y la lección errónea solo añade una isla, no destruye nada, por lo que el niño puede volver a preguntar. |

### RF-PLT-03 — Imágenes IA en lecciones y avatares (desactivadas por defecto)

| Campo | Descripción |
|---|---|
| **ID** | `RF-PLT-03` |
| **Módulo** | PLT — Plataforma y accesibilidad |
| **Nombre del requisito** | Imágenes IA en lecciones y avatares (desactivadas por defecto) |
| **HU / CU relacionada** | US11 |
| **Descripción funcional** | La generación de imágenes IA (avatares y lecciones) deberá estar desactivada por defecto; generar un avatar por IA con la imagen inactiva deberá devolver 409. |
| **Entradas** | `AvatarGenerate` `{description:2-120}` vía `POST /children/{id}/avatar/generate`. |
| **Salidas esperadas** | `ChildRead` con `avatar_image_url` si la imagen está activa; 409 si está desactivada. |
| **Criterios de aceptación (GWT)** | **Given** la generación de imágenes está desactivada (por defecto) **When** intento generar un avatar por IA **Then** la respuesta es 409. |
| **Reglas de negocio** | `family_ai_config.image_enabled` gobierna el 409. Requiere un proveedor de imagen configurado (ver `RF-IA-06`). |
| **Prioridad** | Baja |
| **Dependencias** | `RF-IA-06` |
| **Riesgos** | N/A |

### RF-PLT-04 — Conectar dispositivo (QR/LAN)

| Campo | Descripción |
|---|---|
| **ID** | `RF-PLT-04` |
| **Módulo** | PLT — Plataforma y accesibilidad |
| **Nombre del requisito** | Conectar dispositivo (QR/LAN) |
| **HU / CU relacionada** | US11 |
| **Descripción funcional** | La app deberá ofrecer una pantalla "Conectar móvil" que muestre la URL de la LAN (`window.location.origin`) y su código QR para el acceso desde otro dispositivo. |
| **Entradas** | Acceso a la pantalla "Conectar móvil"; `window.location.origin`. |
| **Salidas esperadas** | URL de la LAN y su código QR generado localmente. |
| **Criterios de aceptación (GWT)** | **Given** estoy en la pantalla "Conectar móvil" **Then** veo la URL basada en `window.location.origin` y su código QR. |
| **Reglas de negocio** | QR generado localmente. Asume misma red WiFi y `VITE_API_URL`/`CORS_ORIGINS` configurados por el operador. |
| **Prioridad** | Baja |
| **Dependencias** | — |
| **Riesgos** | Acceso LAN dependiente de la red del operador: fuera del control de la app. |

### RF-PLT-05 — Multilenguaje es/en

| Campo | Descripción |
|---|---|
| **ID** | `RF-PLT-05` |
| **Módulo** | PLT — Plataforma y accesibilidad |
| **Nombre del requisito** | Multilenguaje es/en |
| **HU / CU relacionada** | US11 |
| **Descripción funcional** | La app deberá detectar el idioma del navegador (es/en) y permitir cambiarlo; la lectura y el dictado por voz usarán el idioma activo. |
| **Entradas** | Idioma del navegador; selección manual de idioma. |
| **Salidas esperadas** | Interfaz en el idioma activo; voz (lectura/dictado) en ese idioma. |
| **Criterios de aceptación (GWT)** | **Given** abro la app **Then** el idioma se detecta del navegador (es/en) y puedo cambiarlo manualmente.<br>**Given** cambio el idioma **Then** la lectura en voz alta usa el idioma activo. |
| **Reglas de negocio** | Solo es/en en esta entrega. El idioma activo guía voz de lectura (`RF-APR-04`) y dictado (`RF-PLT-02`). |
| **Prioridad** | Media |
| **Dependencias** | — |
| **Riesgos** | N/A |

---

## Módulo SEG — Seguridad transversal

### RF-SEG-01 — El backend nunca envía la respuesta correcta del quiz

| Campo | Descripción |
|---|---|
| **ID** | `RF-SEG-01` |
| **Módulo** | SEG — Seguridad transversal |
| **Nombre del requisito** | El backend nunca envía la respuesta correcta del quiz |
| **HU / CU relacionada** | US4 (y transversal) |
| **Descripción funcional** | `LessonRead` nunca deberá exponer `quiz_correct_index` ni `quiz_explanation`; la corrección se validará solo en servidor y la explicación solo se devolverá al responder. |
| **Entradas** | `GET /lessons/{id}` y `POST /lessons/{id}/answer`. |
| **Salidas esperadas** | `LessonRead` con `quiz: QuizPublic{question, options}` (sin índice ni explicación); explicación solo en `AnswerResult`. |
| **Criterios de aceptación (GWT)** | **Given** recibo una lección con su reto **When** inspecciono la respuesta del backend **Then** no contiene el índice ni el texto de la opción correcta. |
| **Reglas de negocio** | Garantía en tres capas: esquema `QuizPublic`, serialización `to_read_dict` y validación en `answer_lesson`. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-APR-05` |
| **Riesgos** | Filtrado accidental por un cambio de esquema: mitigado con las tres capas independientes y pruebas de seguridad. |

### RF-SEG-02 — Aislamiento de datos por niño y por familia + JWT tipado

| Campo | Descripción |
|---|---|
| **ID** | `RF-SEG-02` |
| **Módulo** | SEG — Seguridad transversal |
| **Nombre del requisito** | Aislamiento de datos por niño y por familia + JWT tipado |
| **HU / CU relacionada** | US1, US9, US5/US6 (transversal) |
| **Descripción funcional** | El sistema deberá aislar los datos por niño y por familia (accesos cruzados → 404) y tipar el JWT (`family`/`child`) con rechazo cruzado (401). |
| **Entradas** | Peticiones con token `family` o `child` a endpoints propios y ajenos. |
| **Salidas esperadas** | 404 en accesos a datos de otra familia/niño; 401 con token de tipo incorrecto. |
| **Criterios de aceptación (GWT)** | **Given** tengo un token `child` **When** llamo a un endpoint de familia **Then** la respuesta es 401; **And** con un token `family` en un endpoint de niño la respuesta también es 401.<br>**Given** un recurso de otra familia/niño **When** intento acceder **Then** la respuesta es 404. |
| **Reglas de negocio** | Claim `type` en el JWT. Cada niño accede solo a sus datos; aislamiento estricto entre familias. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-ONB-01` |
| **Riesgos** | Enumeración de recursos: mitigada devolviendo 404 (no 403) en accesos cruzados. |

### RF-SEG-03 — Moderación de la entrada del niño con fallback seguro

| Campo | Descripción |
|---|---|
| **ID** | `RF-SEG-03` |
| **Módulo** | SEG — Seguridad transversal |
| **Nombre del requisito** | Moderación de la entrada del niño con fallback seguro |
| **HU / CU relacionada** | US2 (y transversal) |
| **Descripción funcional** | La entrada del niño (curiosidad) deberá pasar por moderación; una entrada inapropiada se bloqueará con 422 y un mensaje amable ("Esta la vemos con un adulto" 🛟). |
| **Entradas** | Curiosidad en `POST /lessons` y `POST /lessons/{id}/ask`. |
| **Salidas esperadas** | 422 con mensaje seguro cuando la entrada se bloquea. |
| **Criterios de aceptación (GWT)** | **Given** el niño envía una curiosidad inapropiada **When** se procesa la petición **Then** la moderación la bloquea con 422 y un mensaje amable orientado a la familia. |
| **Reglas de negocio** | Blocklist con fallback seguro. Aplica tanto a la creación como a las repreguntas del hilo. |
| **Prioridad** | Alta |
| **Dependencias** | `RF-APR-01` |
| **Riesgos** | Falsos positivos/negativos de la blocklist: se mitiga con el fallback seguro por defecto y revisión parental. |


### RF-SEG-04 — Salir de la sesión del niño con verificación parental

> **Añadido en implementación (15-09-2026).** No estaba previsto en la Entrega 1 y apareció al usar
> la app: desde la sesión del niño no había forma de volver a la zona de familia, y para
> reconfigurar había que escribir la URL a mano.

| Campo | Descripción |
|---|---|
| **ID** | `RF-SEG-04` |
| **Módulo** | SEG — Seguridad transversal |
| **Nombre del requisito** | Salir de la sesión del niño con verificación parental |
| **HU / CU relacionada** | US5/US6 (y transversal con US1) |
| **Descripción funcional** | Desde la sesión del niño deberá poder volverse a la zona de familia, pero **solo tras verificar la contraseña de la familia**. Al verificarla se cierra únicamente la sesión del **niño**; la de familia permanece. |
| **Entradas** | `VerifyPasswordRequest` `{password}` vía `POST /auth/verify-password` con token `family`. |
| **Salidas esperadas** | `{"status":"ok"}` y cierre del token de niño · `401` si la contraseña es incorrecta. |
| **Criterios de aceptación (GWT)** | **Given** estoy en la sesión de un niño **When** pulso el acceso de salida e introduzco la contraseña correcta de la familia **Then** se cierra la sesión del niño y vuelvo a la zona de familia.<br>**Given** introduzco una contraseña incorrecta **Then** la respuesta es 401 y la sesión del niño **no** se cierra.<br>**Given** no hay token de familia **Then** la respuesta es 401. |
| **Reglas de negocio** | **El token de familia sigue en el dispositivo mientras el niño juega, así que tenerlo no demuestra nada**: quien pulsa podría ser el niño. Por eso se exige la contraseña de nuevo, y no basta con la sesión abierta. El acceso es deliberadamente discreto (texto pequeño y apagado) para que un adulto lo encuentre y un niño no se sienta invitado a pulsarlo. Solo se invalida el token de niño. |
| **Prioridad** | Media |
| **Dependencias** | `RF-ONB-04` (sesión del niño), `RF-SEG-02` (JWT tipado) |
| **Riesgos** | Que un niño insista con la contraseña: el 401 no cierra nada y no revela información. Sin límite de intentos, igual que en el resto de flujos de contraseña de esta entrega. |

---

# PARTE 2 — Requisitos no funcionales (RNF)

Los RNF se derivan de la §5 del [PRD](prd.md#5-requisitos-no-funcionales). Su criterio de verificación se redacta como algo comprobable en las Entregas 2–3.

### RNF-01 — Seguridad del menor

| Campo | Descripción |
|---|---|
| **ID** | `RNF-01` |
| **Categoría** | Seguridad del menor |
| **Descripción** | La entrada del niño se moderará con fallback seguro; el backend nunca enviará la respuesta correcta del quiz; los cuentos requerirán aprobación parental antes de mostrarse. |
| **Criterio de verificación / métrica** | Deberá comprobarse que una entrada inapropiada devuelve 422; que `LessonRead` no contiene `quiz_correct_index`/`quiz_explanation`; y que un cuento `pending` no es visible para el niño (404) hasta aprobarse. |
| **Prioridad** | Alta |
| **HUs/RF relacionados** | US2, US4, US9 · `RF-SEG-01`, `RF-SEG-03`, `RF-CUE-01` |
| **Riesgos / mitigación** | Falsos negativos de moderación → fallback seguro por defecto y aprobación parental como segunda barrera. |

### RNF-02 — Seguridad técnica

| Campo | Descripción |
|---|---|
| **ID** | `RNF-02` |
| **Categoría** | Seguridad técnica |
| **Descripción** | JWT tipado (familia/niño) con rechazo cruzado; claves de IA cifradas con Fernet; SSRF mitigado en el endpoint de imagen local; aislamiento de datos por niño y familia; imágenes generadas fuera del control de versiones. |
| **Criterio de verificación / métrica** | Deberá comprobarse el 401 por token cruzado y el 404 por acceso cruzado; que `AIConfigRead` nunca expone claves (solo `has_api_key`/`has_image_api_key`); y que el endpoint de imagen local rechaza URLs internas. |
| **Prioridad** | Alta |
| **HUs/RF relacionados** | US1, US9, US10 · `RF-SEG-02`, `RF-IA-02`, `RF-IA-06` |
| **Riesgos / mitigación** | Fuga de secretos → esquema con solo booleanos y `AI_CONFIG_KEY` obligatoria; SSRF → validación de destino en el endpoint de imagen. |

### RNF-03 — Privacidad / minimización de datos del menor

| Campo | Descripción |
|---|---|
| **ID** | `RNF-03` |
| **Categoría** | Privacidad / minimización de datos del menor |
| **Descripción** | No se pedirán datos del menor en el alta de la cuenta; la recuperación de contraseña se resolverá sin servicio de email (por código). |
| **Criterio de verificación / métrica** | Deberá comprobarse que el alta de cuenta no solicita datos del menor y que el reset funciona solo con el código de recuperación, sin dependencia de email. |
| **Prioridad** | Alta |
| **HUs/RF relacionados** | US1 · `RF-ONB-01`, `RF-ONB-05` |
| **Riesgos / mitigación** | Pérdida del código sin email de respaldo → aviso explícito de guardado único. |

### RNF-04 — Fiabilidad y degradación elegante

| Campo | Descripción |
|---|---|
| **ID** | `RNF-04` |
| **Categoría** | Fiabilidad y degradación elegante |
| **Descripción** | Sin proveedor configurado o ante fallo del proveedor, el sistema caerá al stub determinista; el niño nunca verá un error del proveedor. |
| **Criterio de verificación / métrica** | Deberá comprobarse que, sin claves, la app es plenamente usable y que un fallo simulado del proveedor conmuta al stub sin exponer errores al niño. |
| **Prioridad** | Alta |
| **HUs/RF relacionados** | US2, US10 · `RF-APR-02`, `RF-IA-01`, `RF-IA-05` |
| **Riesgos / mitigación** | Fallo silencioso no detectado → pruebas de conmutación al stub y logging del lado servidor. |

### RNF-05 — Accesibilidad

| Campo | Descripción |
|---|---|
| **ID** | `RNF-05` |
| **Categoría** | Accesibilidad |
| **Descripción** | Interfaz táctil y grande; voz (dictado + lectura) con APIs nativas del navegador; contraste y tipografías legibles (Fredoka/Mulish); respeto de `reduced-motion`. |
| **Criterio de verificación / métrica** | Deberá comprobarse el contraste mínimo AA en pantallas del niño, que los controles de voz se degradan si no hay soporte y que las animaciones se reducen con `prefers-reduced-motion`. **Los estados en curso se anuncian a lectores de pantalla**: el indicador de espera usa `role="status"` y los errores de voz `role="alert"`. Toda animación nueva (`chispa-pulse`, `chispa-dot`) entra en la regla de `prefers-reduced-motion`. |
| **Prioridad** | Media |
| **HUs/RF relacionados** | US3, US11 · `RF-APR-04`, `RF-PLT-02`, `RF-PLT-05` |
| **Riesgos / mitigación** | Soporte de voz variable → ocultar controles cuando no exista. |

### RNF-06 — Responsive / multidispositivo

| Campo | Descripción |
|---|---|
| **ID** | `RNF-06` |
| **Categoría** | Responsive / multidispositivo |
| **Descripción** | La app funcionará en móvil, tablet y PC, con acceso desde la red doméstica (LAN) mediante QR. |
| **Criterio de verificación / métrica** | Deberá comprobarse el diseño responsive en anchos de móvil/tablet/PC y la conexión de un móvil por QR sobre la URL de la LAN. |
| **Prioridad** | Media |
| **HUs/RF relacionados** | US11 · `RF-PLT-04` |
| **Riesgos / mitigación** | Dependencia de la red del operador → documentar `VITE_API_URL`/`CORS_ORIGINS`. |

### RNF-07 — Rendimiento percibido

| Campo | Descripción |
|---|---|
| **ID** | `RNF-07` |
| **Categoría** | Rendimiento percibido |
| **Descripción** | El stub responderá de forma inmediata y determinista, garantizando una experiencia fluida sin dependencia de red externa. **Con un proveedor real la respuesta tarda varios segundos**, así que la interfaz debe indicar que está trabajando en lugar de quedarse congelada. |
| **Criterio de verificación / métrica** | Deberá comprobarse que, en modo demo, la creación de una lección responde de forma inmediata y que el mismo input produce el mismo output. **Con proveedor real:** mientras se espera aparece un indicador («Chispa está pensando…») en el lugar donde surgirá la respuesta, con `role="status"` para lectores de pantalla, y los controles que dispararían otra petición quedan desactivados. |
| **Prioridad** | Media |
| **HUs/RF relacionados** | US2 · `RF-APR-01`, `RF-APR-02` |
| **Añadido en implementación** | El indicador de espera se incorporó el 15-09-2026: con el stub la respuesta era instantánea y no hacía falta; con IA real son 2–5 segundos en los que el niño veía la pantalla congelada y concluía que se había roto. |
| **Riesgos / mitigación** | Latencia de proveedores reales → el stub sostiene la experiencia base. |

### RNF-08 — Portabilidad / despliegue

| Campo | Descripción |
|---|---|
| **ID** | `RNF-08` |
| **Categoría** | Portabilidad / despliegue |
| **Descripción** | Autoalojable con Docker (Postgres + backend + frontend + Ollama); SQLite en desarrollo/tests; migraciones Alembic siempre aditivas. **Las imágenes generadas se guardan en un volumen persistente**, no en el sistema de ficheros del contenedor. |
| **Criterio de verificación / métrica** | Deberá comprobarse el arranque completo con Docker Compose, la ejecución de tests sobre SQLite y que las migraciones son aditivas (sin borrado destructivo). **Y que una imagen generada sobrevive a `docker compose up --build`.** |
| **Prioridad** | Media |
| **HUs/RF relacionados** | Transversal (infraestructura) · soporte de todos los RF |
| **Riesgos / mitigación** | Divergencia SQLite/Postgres → pruebas en ambos y migraciones aditivas. **Corregido en implementación (15-09-2026):** el servicio backend no tenía volumen, así que `MEDIA_DIR` moría con el contenedor y la base de datos quedaba apuntando a ficheros borrados. Se añadió el volumen `media` y el directorio se crea en la imagen con el propietario correcto, porque si no Docker monta el punto como root y el proceso, que corre sin privilegios, no puede escribir. |

### RNF-09 — Calidad y mantenibilidad

| Campo | Descripción |
|---|---|
| **ID** | `RNF-09` |
| **Categoría** | Calidad y mantenibilidad |
| **Descripción** | Arquitectura por capas; suite de pruebas backend (pytest) y frontend (Vitest + Testing Library); lint (ruff/eslint) y `tsc --noEmit`; CI en GitHub Actions. |
| **Criterio de verificación / métrica** | Deberá comprobarse que la CI ejecuta lint, tipos y pruebas en cada cambio y que las pruebas cubren los RF de la matriz (Parte 3). |
| **Prioridad** | Media |
| **HUs/RF relacionados** | Transversal · todos los RF (base de pruebas funcionales) |
| **Riesgos / mitigación** | Deuda técnica → separación por capas y revisión por agentes distintos del implementador. |

### RNF-10 — Internacionalización

| Campo | Descripción |
|---|---|
| **ID** | `RNF-10` |
| **Categoría** | Internacionalización |
| **Descripción** | Textos de interfaz en es/en; lectura y dictado por voz en el idioma activo. |
| **Criterio de verificación / métrica** | Deberá comprobarse la detección del idioma del navegador, el cambio manual es/en y que la voz (lectura/dictado) sigue el idioma activo. |
| **Prioridad** | Media |
| **HUs/RF relacionados** | US3, US11 · `RF-PLT-05`, `RF-APR-04`, `RF-PLT-02` |
| **Riesgos / mitigación** | Textos sin traducir → catálogo i18n centralizado y revisión previa a la entrega. |

---

# PARTE 3 — Matriz de trazabilidad (trazabilidad + pruebas funcionales)

> Esta matriz cumple un **doble propósito**: (A) traza cada historia de usuario a los RF que la realizan y (B) deriva, por cada RF, la pantalla, el endpoint y la **prueba funcional prevista**. La **Tabla B es la base para el diseño de las pruebas funcionales**, que se desarrollarán en [casos-aceptacion.md](../03-testing/casos-aceptacion.md).

## Tabla A — HU → RF

| HU | Épica | RF que la realizan | Prioridad |
|---|---|---|---|
| US1 | E1 · Onboarding y perfiles | `RF-ONB-01`, `RF-ONB-02`, `RF-ONB-03`, `RF-ONB-04`, `RF-ONB-05`, `RF-SEG-02` | Alta |
| US2 | E2 · Bucle de aprendizaje | `RF-APR-01`, `RF-APR-02`, `RF-SEG-03` | Alta |
| US3 | E2 · Bucle de aprendizaje | `RF-APR-03`, `RF-APR-04` | Alta |
| US4 | E2 · Bucle de aprendizaje | `RF-APR-05`, `RF-SEG-01` | Alta |
| US7 | E3 · Conocimiento vivo | `RF-CON-01`, `RF-CON-02`, `RF-CON-03` | Media |
| US8 | E3 · Conocimiento vivo | `RF-CON-04`, `RF-CON-05`, `RF-CON-01` | Media |
| US9 | E4 · Cuentos | `RF-CUE-01`, `RF-CUE-02`, `RF-CUE-03`, `RF-SEG-02` | Media |
| US10 | E5 · IA configurable | `RF-IA-01`, `RF-IA-02`, `RF-IA-03`, `RF-IA-04`, `RF-IA-05`, `RF-IA-06` | Alta |
| US5/US6 | E6 · Plataforma y accesibilidad | `RF-PLT-01`, `RF-SEG-02`, `RF-SEG-04` | Media |
| US11 | E6 · Plataforma y accesibilidad | `RF-PLT-02`, `RF-PLT-03`, `RF-PLT-04`, `RF-PLT-05` | Media |

## Tabla B — RF → prueba funcional

> Base para el **diseño de pruebas funcionales**. Pantallas, endpoints y pruebas se toman de forma coherente con [historias-usuario.md](historias-usuario.md) y [contratos-api.md](../02-technical-design/contratos-api.md). Las pruebas concretas se detallarán en [casos-aceptacion.md](../03-testing/casos-aceptacion.md).

| RF | Nombre | HU origen | Módulo | Pantalla prevista | Endpoint previsto | Prueba funcional prevista | Prioridad |
|---|---|---|---|---|---|---|---|
| `RF-ONB-01` | Crear cuenta familiar | US1 | ONB | `CreateFamily.tsx` | `POST /auth/register` | Registro con autologin, token `family` y código `XXXX-XXXX` único (test_auth.py) | Alta |
| `RF-ONB-02` | Validación de contraseña en cliente | US1 | ONB | `CreateFamily.tsx` | — (cliente) | Error de coincidencia antes de llamar a la API (CreateFamily.test.tsx) | Media |
| `RF-ONB-03` | Alta de explorador (niño) | US1 | ONB | `AddExplorer.tsx` | `POST /children` | Alta con PIN `^\d{4}$`, edad calculada y rechazo de PIN inválido (test_children.py) | Alta |
| `RF-ONB-04` | Acceso del niño con PIN | US1 | ONB | `ChildAccess.tsx` / `WhoExplores.tsx` | `POST /children/{id}/login` | PIN correcto → token `child`; PIN incorrecto → 401 (test_children.py) | Alta |
| `RF-ONB-05` | Cambio y recuperación de contraseña | US1 | ONB | `ChangePassword.tsx` / `ResetPassword.tsx` | `POST /auth/change-password`, `POST /auth/reset-password` | Reset por código que rota; cambio autenticado; 400 si actual incorrecta (test_password.py) | Media |
| `RF-APR-01` | Crear lección desde curiosidad/sugerencia | US2 | APR | `Spark.tsx` | `POST /lessons`, `GET /me/suggestions` | Crear lección y navegar; lanzar desde sugerencia (test_lessons_api.py, Spark.test.tsx) | Alta |
| `RF-APR-02` | Lección determinista en modo stub | US2 | APR | `Spark.tsx` / `LessonScreen.tsx` | `POST /lessons` (stub) | Subject acotado, 3 opciones, índice 0..2, reproducible (test_lesson_generator.py) | Alta |
| `RF-APR-03` | Lección adaptada por banda de edad | US3 | APR | `LessonScreen.tsx` | `POST /lessons`, `GET /lessons/{id}/thread` | Contenido por banda (3-5/6-8/9-12) con idea+analogía+dato+follow-ups (test_lesson_generator.py) | Alta |
| `RF-APR-04` | Lectura en voz alta | US3 | APR | `LessonScreen.tsx` / `SpeakButton` | — (Web Speech Synthesis) | Lectura en idioma activo; sin control si no hay soporte (SpeakButton.test.tsx) | Media |
| `RF-APR-05` | Responder el reto (quiz) | US4 | APR | `LessonScreen.tsx` | `POST /lessons/{id}/answer` | Acierto sube maestría; fallo no penaliza; 404 en ajena (test_answer_api.py) | Alta |
| `RF-CON-01` | Isla automática al crear lección | US8 | CON | `MyKnowledge.tsx` | `GET /me/knowledge` | Nodo creado sin responder quiz (test_knowledge_root_lesson_id.py) | Alta |
| `RF-CON-02` | Buscador del archipiélago | US7 | CON | `MyKnowledge.tsx` | `GET /me/knowledge` | Búsqueda sin acentos/mayúsculas; "sin resultados" solo con islas (MyKnowledge.test.tsx) | Media |
| `RF-CON-03` | Reabrir conversación de una isla | US7 | CON | `MyKnowledge.tsx` / `LessonScreen.tsx` | `GET /lessons/{id}/thread` (vía `root_lesson_id`) | Abrir conversación guardada; aislamiento por `child_id` (test_knowledge_root_lesson_id.py) | Media |
| `RF-CON-04` | Repreguntar en el hilo con contexto | US8 | CON | `LessonScreen.tsx` | `POST /lessons/{id}/ask`, `GET /lessons/{id}/thread` | Turno con `parent_id`/`root_id`; hilo en orden (raíz primero); 404 en ajena (test_conversation.py) | Alta |
| `RF-CON-05` | Maestría solo sube con reto acertado | US8 | CON | `LessonScreen.tsx` / `MyKnowledge.tsx` | `GET /me/knowledge` | Maestría invariable al repreguntar (test_conversation.py) | Media |
| `RF-CUE-01` | Crear cuento (pendiente) | US9 | CUE | `StoryLibrary.tsx` | `POST /me/stories`, `GET /me/stories/{id}` | Cuento `pending` invisible para el niño (404) (test_story_api.py) | Media |
| `RF-CUE-02` | Aprobar/editar cuento | US9 | CUE | `FamilyStories.tsx` | `PUT /family/stories/{id}` (approve) | Aprobar editando título/cuerpo; visible tras aprobar (FamilyStories.test.tsx) | Media |
| `RF-CUE-03` | Rechazar cuento | US9 | CUE | `FamilyStories.tsx` | `PUT /family/stories/{id}` (reject) | `rejected` conservando texto original (test_story_api.py) | Media |
| `RF-IA-01` | Configuración por defecto (demo) | US10 | IA | `AIConfigPanel.tsx` | `GET /family/ai-config` | `free`/`stub`/`has_api_key=false` por defecto (test_ai_config_api.py) | Alta |
| `RF-IA-02` | BYOK con clave cifrada | US10 | IA | `AIConfigPanel.tsx` | `PUT /family/ai-config` | `has_api_key=true` sin devolver clave; 400 sin `AI_CONFIG_KEY` (test_crypto.py) | Alta |
| `RF-IA-03` | Rechazo de proveedor deshabilitado | US10 | IA | `AIConfigPanel.tsx` | `PUT /family/ai-config` | Proveedor no habilitado → 422 (test_ai_config_api.py) | Media |
| `RF-IA-04` | Recomendador de modelo local | US10 | IA | `AIConfigPanel.tsx` | `POST /family/ai-config/recommend` | Recomendación acorde a VRAM/RAM (test_ai_config_api.py) | Baja |
| `RF-IA-05` | Proveedores de texto | US10 | IA | `AIConfigPanel.tsx` | `GET /family/ai-config/catalog` | stub/Ollama/Claude habilitados; resto previstos no habilitados (test_ai_config_api.py) | Media |
| `RF-IA-06` | Proveedores de imagen | US10 | IA | `AIConfigPanel.tsx` | `PUT /family/ai-config`, `GET /family/ai-config/catalog` | `has_image_api_key` sin clave; `image_enabled=false` por defecto (test_ai_config_api.py) | Baja |
| `RF-PLT-01` | Panel de familia (actividad/ficha) | US5/US6 | PLT | `FamilyPanel.tsx` | `GET /children/{id}/profile`, `GET /children/{id}/knowledge` | Perfil y ficha con token de familia; 404 cruzado; 401 con token de niño; selector sin mezclar hermanos (test_family_panel.py, FamilyPanel.test.tsx) | Alta |
| `RF-PLT-02` | Dictado por voz | US11 | PLT | `Spark.tsx` (micrófono) | — (Web Speech API) | Transcripción en idioma activo; sin micrófono si no hay soporte (MicButton.test.tsx) | Baja |
| `RF-PLT-03` | Imágenes IA (desactivadas por defecto) | US11 | PLT | `AddExplorer.tsx` (avatar IA) | `POST /children/{id}/avatar/generate` | 409 al generar avatar con imagen inactiva (test_avatar_ai.py) | Baja |
| `RF-PLT-04` | Conectar dispositivo (QR/LAN) | US11 | PLT | `ConnectDevice.tsx` | — (`window.location.origin`) | URL de LAN + QR mostrados (ConnectDevice.test.tsx) | Baja |
| `RF-PLT-05` | Multilenguaje es/en | US11 | PLT | Contexto i18n | — (cliente) | Detección de idioma y cambio manual; voz en idioma activo (I18nContext.test.tsx) | Media |
| `RF-SEG-01` | Quiz nunca revela la respuesta | US4 | SEG | `LessonScreen.tsx` | `GET /lessons/{id}`, `POST /lessons/{id}/answer` | `LessonRead` sin `quiz_correct_index`/`quiz_explanation` (test_security.py) | Alta |
| `RF-SEG-02` | Aislamiento + JWT tipado | US1/US9/US5-6 | SEG | Transversal | Endpoints `/family/*` y `/me/*`, `/lessons/*` | 401 por token cruzado; 404 por acceso cruzado (test_security.py) | Alta |
| `RF-SEG-03` | Moderación con fallback seguro | US2 | SEG | `Spark.tsx` / `LessonScreen.tsx` | `POST /lessons`, `POST /lessons/{id}/ask` | Entrada inapropiada → 422 con mensaje seguro (test_moderation.py) | Alta |
| `RF-SEG-04` | Salir de la sesión del niño con contraseña | US5/US6 | SEG | `ExitChildSession.tsx`, `ChildHeader` | `POST /auth/verify-password` | Contraseña correcta cierra solo la sesión del niño; incorrecta → 401 y no cierra (test_password.py, ExitChildSession.test.tsx) | Media |

---

> **Nota final:** este documento es una **propuesta previa a la implementación**. Los criterios GWT y las pruebas previstas guiarán la construcción en las Entregas 2–3 y su verificación se documentará en [casos-aceptacion.md](../03-testing/casos-aceptacion.md).
