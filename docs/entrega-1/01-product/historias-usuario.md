# Chispa ✨ — Entrega 1 · Producto

**Documento:** Historias de usuario y criterios de aceptación
**Proyecto:** Chispa (aprendizaje por curiosidad para niños)
**Alumno:** Germán González Pérez · **Máster:** LIDR – AI4Devs
**Repositorio:** github.com/ggonzalezperez/chispa (privado) · **Entrega 1:** 22 de julio de 2026

> Documentos relacionados: [Problema y usuarios](problema-y-usuarios.md) · [PRD](prd.md) · [Alcance](alcance.md) · [Modelo de datos](../02-technical-design/modelo-datos.md) · [Contratos de la API](../02-technical-design/contratos-api.md)

---

## Cómo leer este documento

Este documento recoge el **diseño de las 11 historias de usuario (US1–US11) antes de escribir código**. Todo está redactado en clave de propuesta (futuro): describe lo que el sistema **deberá** hacer y lo que **se implementará** en las Entregas 2–3, no lo que ya existe.

Cada historia sigue una **plantilla única (Definition of Ready)** de **6 bloques**, pensada para que la HU quede "lista para desarrollo":

1. **Contexto** — problema, usuario beneficiado y quién solicita/valida.
2. **Alcance** — qué entra, qué no entra y MVP.
3. **Funcional** — reglas de negocio, datos/campos/estados, integraciones y casuística.
4. **Validación** — criterios de aceptación en **Gherkin**, datos de prueba y evidencia esperada.
5. **Operativa** — prioridad, dependencias e impacto.
6. **Trazabilidad IA** — cómo se asiste con IA y quién revisa.

Convenciones importantes:

- Los **criterios de aceptación** van siempre en bloques `gherkin`, incluidos los escenarios de error.
- Todavía **no hay personas físicas asignadas**. Los **stakeholders y validadores se expresan como ROLES** (Product Owner, Responsable de producto/negocio, QA / Validador funcional, Tech Lead), con la coletilla "(rol; persona por asignar)". Al ser un proyecto académico en solitario, el alumno asume varios de esos sombreros.
- El **usuario beneficiado** sí es real: **Familia/Adulto** o **Explorador/Niño** según la historia.

### Índice de épicas

| Épica | Historias | Prioridad |
|---|---|---|
| [E1 · Onboarding y perfiles](#e1--onboarding-y-perfiles) | US1 | Núcleo |
| [E2 · Bucle de aprendizaje](#e2--bucle-de-aprendizaje) | US2, US3, US4 | Núcleo |
| [E3 · Conocimiento vivo](#e3--conocimiento-vivo) | US7, US8 | Núcleo |
| [E4 · Cuentos](#e4--cuentos) | US9 | Núcleo |
| [E5 · IA configurable](#e5--ia-configurable) | US10 | Alta |
| [E6 · Plataforma y accesibilidad](#e6--plataforma-y-accesibilidad) | US5/US6, US11 | Media |

---

## E1 · Onboarding y perfiles

### US1 — Cuenta familiar y perfiles de niño  ·  `[Onboarding] Crear cuenta familiar y dar de alta exploradores`

> **Como** adulto responsable de una familia, **quiero** crear una cuenta y dar de alta a mis hijos como "exploradores" con su PIN y avatar, **para** darles un acceso propio y seguro y poder recuperar mi cuenta si olvido la contraseña.

**Épica:** E1 · Onboarding y perfiles  ·  **Prioridad:** Alta

#### Bloque 1 — Contexto

- **Problema:** Chispa quiere ser un **espacio personal de descubrimiento** donde cada niño explora su curiosidad de forma segura, no una app de deberes ni una enciclopedia con IA. Para eso, cada explorador necesita una identidad propia bajo el paraguas de su familia: sin cuenta familiar ni perfiles de niño separados no hay dónde anclar de forma segura su curiosidad ni su **Ficha de Conocimiento**, y sin recuperación de acceso la familia podría perder todo ese rastro personalizado.
- **Usuario beneficiado:** Familia/Adulto (rol).
- **Stakeholder solicitante:** Product Owner (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 2) Seguridad infantil por diseño · 7) Padres con control, niño con agencia.
- **RF relacionados:** RF-ONB-01, RF-ONB-02, RF-ONB-03, RF-ONB-04, RF-ONB-05, RF-SEG-02 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Alta de cuenta familiar (nombre, email, contraseña ≥ 8 con confirmación) con autologin y token de tipo `family`.
  - Entrega única de un **código de recuperación** `XXXX-XXXX` (mostrado una sola vez).
  - Alta de exploradores (avatar, alias, fecha de nacimiento, PIN de 4 dígitos confirmado) con edad calculada.
  - Acceso del niño con PIN (iniciado por la familia autenticada) que emite token de tipo `child`.
  - Separación estricta de sesiones familia/niño.
  - Recuperación de contraseña por código, sin email.
- **Excluido explícitamente (qué NO entra):**
  - Verificación de email o envío de correos.
  - Avatar generado por IA (se cubre en US11).
  - Recuperación por SMS o proveedores de identidad externos (OAuth).
  - Roles intermedios (tutores, múltiples adultos con permisos diferenciados).
- **MVP:** Un adulto puede registrarse, crear un explorador con PIN y abrirle sesión; la familia recibe un código de recuperación que le permite restablecer la contraseña sin email.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - La contraseña debe tener **≥ 8 caracteres**; la confirmación debe coincidir (validación en cliente antes de llamar a la API).
  - El **PIN** debe cumplir `^\d{4}$` y coincidir con su confirmación; si no, no se crea el perfil.
  - **Aislamiento de sesiones (seguridad del menor):** un token `child` en endpoint de familia devuelve `401`, y un token `family` en endpoint de niño devuelve `401`.
  - El **login del niño lo autoriza el adulto:** `POST /children/{id}/login` exige un token de familia válido.
  - El **código de recuperación se muestra una sola vez** y se almacena hasheado (`recovery_code_hash`); `reset-password` consume el anterior y emite uno nuevo.
  - Nunca se serializan `password_hash`, `pin_hash` ni `family_id` en las respuestas de perfil.
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `families.name` | Formulario de alta | `families` | Nombre de la familia |
  | `users.email` | Formulario de alta | `users` | `unique=True`, `index=True` |
  | `users.password_hash` | Contraseña ≥ 8 | `users` | Solo hash, nunca en claro |
  | `users.recovery_code_hash` | Código `XXXX-XXXX` generado | `users` | Hash; código mostrado una sola vez |
  | `children.name` / `birthdate` | Alta de explorador | `children` | `birthdate` es base de la edad |
  | `children.pin_hash` | PIN 4 dígitos | `children` | Hasheado con bcrypt |
  | `children.avatar` | Selección de avatar | `children` | `def="fox"` |
  | `children.age` | Derivado de `birthdate` | `children` (calculado) | `@property`, no columna |
  | Claim `type` del JWT | Emisión de token | Servicio de auth | `family` \| `child` |
- **Integraciones implicadas:** Ninguna externa. Cifrado/hashing internos (bcrypt para PIN, hash de contraseña y de código de recuperación).
- **Casuística (happy + límites + errores):**
  - Happy path: la familia se registra, recibe su código de recuperación, da de alta a un niño con PIN y le abre sesión.
  - Caso límite 1: PIN correcto pero confirmación distinta → se rechaza sin crear perfil.
  - Caso límite 2: la familia olvida la contraseña y usa el código de recuperación para restablecerla (y recibe uno nuevo).
  - Error esperado: email ya registrado → `409`; credenciales inválidas en login → `401`; token de tipo incorrecto → `401`.

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Cuenta familiar y perfiles de niño

  Scenario: Crear una cuenta familiar
    Given estoy en la pantalla de crear cuenta familiar
    When introduzco nombre, email y una contraseña de al menos 8 caracteres con su confirmación
    And ambas contraseñas coinciden
    Then se crea la cuenta y recibo un token de tipo "family"
    And se me muestra UNA sola vez un código de recuperación con formato XXXX-XXXX

  Scenario: Las contraseñas no coinciden (validación en cliente)
    Given estoy en la pantalla de crear cuenta familiar
    When la contraseña y su confirmación no coinciden
    Then se muestra un error antes de llamar a la API

  Scenario: Añadir un explorador (niño)
    Given estoy autenticado como familia
    When añado un explorador con avatar, alias, fecha de nacimiento y un PIN de 4 dígitos (^\d{4}$) confirmado
    Then se crea el perfil con la edad calculada a partir de la fecha de nacimiento

  Scenario: PIN inválido
    Given estoy añadiendo un explorador
    When el PIN no tiene exactamente 4 dígitos o no coincide con su confirmación
    Then se rechaza y no se crea el perfil

  Scenario: Acceso del niño con PIN correcto
    Given existe un explorador con PIN
    And la familia está autenticada en el dispositivo (el alta del niño la autoriza el adulto)
    When el niño introduce el PIN correcto en su pantalla de acceso
    Then recibe un token de tipo "child"
    # Nota: POST /children/{id}/login exige un token de familia válido; el adulto abre la sesión del niño.

  Scenario: Separación de sesiones (regla de seguridad)
    Given tengo un token de tipo "child"
    When llamo a un endpoint de familia
    Then la respuesta es 401
    And con un token de tipo "family" en un endpoint de niño la respuesta también es 401

  Scenario: Recuperar contraseña por código (sin email)
    Given olvidé mi contraseña y tengo mi código de recuperación XXXX-XXXX
    When lo introduzco junto a una nueva contraseña válida
    Then mi contraseña se restablece y puedo iniciar sesión
```
- **Datos de prueba:** familia demo "Los Gómez" (email `demo@chispa.test`, contraseña `Chispa2026`); explorador "Nora", 7 años (`birthdate` 2019-04-10), avatar `fox`, PIN `1234`; código de recuperación de ejemplo `AB12-CD34`.
- **Evidencia esperada:** vídeo del flujo de registro → alta de niño → acceso con PIN; captura del código de recuperación mostrado una sola vez; registro de pruebas de aislamiento de sesión (401) y de recuperación de contraseña.

#### Bloque 5 — Operativa

- **Prioridad:** Alta.
- **Justificación de la prioridad:** Es la puerta de entrada de todo el producto: sin cuenta, perfiles y separación de sesiones no hay aprendizaje ni supervisión posibles; además concentra reglas de seguridad del menor.
- **Fecha objetivo:** — (Fase de núcleo, Entrega 2).
- **Dependencias:** FE: `CreateFamily.tsx`, `AddExplorer.tsx`, `WhoExplores.tsx`, `ChildAccess.tsx`, `ChangePassword.tsx`, `ResetPassword.tsx` · BE: `POST /auth/register`, `POST /auth/login`, `POST /auth/change-password`, `POST /auth/reset-password`, `POST /children`, `GET /children`, `POST /children/{id}/login` · Data: `families`, `users`, `children` · UX: pantallas de onboarding y del sistema de diseño.
- **Impacto estimado:** Alto — habilita todo el resto de historias y fija el modelo de identidad y seguridad.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

## E2 · Bucle de aprendizaje

### US2 — Encender la chispa (curiosidad → lección)  ·  `[Aprendizaje] Convertir una curiosidad en una mini-lección`

> **Como** niño explorador, **quiero** escribir o dictar una pregunta (o elegir una sugerencia), **para** recibir al instante una mini-lección sobre eso que me da curiosidad.

**Épica:** E2 · Bucle de aprendizaje  ·  **Prioridad:** Alta

#### Bloque 1 — Contexto

- **Problema:** La curiosidad de un niño se apaga si no encuentra respuesta en el momento. Chispa nace precisamente para **proteger y ampliar esa curiosidad**: un espacio personal de descubrimiento donde lo que intriga al niño manda, no un temario impuesto. Hoy no hay un camino directo entre "esto me intriga" y una explicación breve y recordable a su medida, y sin sugerencias de arranque el niño que no sabe qué preguntar se queda fuera. Cada chispa encendida sembrará además una nueva isla en su Ficha de Conocimiento.
- **Usuario beneficiado:** Explorador/Niño (rol).
- **Stakeholder solicitante:** Responsable de producto/negocio (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 1) Curiosidad primero, currículo después · 6) Aprendizaje corto y recordable.
- **RF relacionados:** RF-APR-01, RF-APR-02, RF-SEG-03 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Crear una lección a partir de una curiosidad escrita (`POST /lessons`) y navegar a ella.
  - Lanzar una lección desde una sugerencia de "Islas para empezar" (`GET /me/suggestions`, muestra rotatoria).
  - Generación **determinista** de la lección en modo demo (proveedor `stub`).
- **Excluido explícitamente (qué NO entra):**
  - Dictado por voz de la curiosidad (se cubre en US11).
  - Adaptación por edad y lectura en voz alta (se cubre en US3).
  - Resolución del quiz y maestría (se cubre en US4).
  - Generación con proveedores de IA reales (se configura en US10).
- **MVP:** Un niño envía una curiosidad y obtiene, al instante, una mini-lección con materia, cuerpo y un quiz de 3 opciones.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - En **modo demo** (sin proveedor configurado) la lección es **determinista**: `subject` ∈ {ciencia, matematicas, lenguaje, arte, cultura}, el quiz tiene **exactamente 3 opciones** y el índice correcto está entre 0 y 2.
  - La curiosidad debe tener entre **2 y 300 caracteres**; la moderación de entrada puede bloquear una curiosidad inapropiada con `422`.
  - El endpoint exige token de tipo `child`.
  - La respuesta **nunca** incluye `quiz_correct_index` ni `quiz_explanation` (ver US4).
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `lessons.curiosity` | Texto del niño o sugerencia | `lessons` | 2–300 caracteres |
  | `lessons.subject` | Generador de lección | `lessons` | Conjunto cerrado de 5 materias |
  | `lessons.concept` / `title` / `body` / `fun_fact` | Generador de lección | `lessons` | Contenido educativo |
  | `lessons.quiz_question` / `quiz_options` | Generador de lección | `lessons` | 3 opciones en modo demo |
  | `lessons.quiz_correct_index` | Generador de lección | `lessons` | Nunca se serializa |
  | Sugerencias | `GET /me/suggestions` | Servicio `me` | 5 de un repertorio de 25 `{curiosity, emoji}` |
- **Integraciones implicadas:** Proveedor de IA de texto (opcional; en este incremento se usa el `stub` determinista). La conmutación a proveedores reales es best-effort y se configura en US10.
- **Casuística (happy + límites + errores):**
  - Happy path: el niño escribe "¿por qué el cielo es azul?" y recibe una lección con quiz.
  - Caso límite 1: el niño no sabe qué preguntar y pincha una sugerencia → se crea y abre una lección para ese tema.
  - Caso límite 2: modo demo sin proveedor → lección determinista reproducible.
  - Error esperado: curiosidad inapropiada bloqueada por moderación → `422`.

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Encender la chispa

  Scenario: Crear una lección desde una curiosidad
    Given estoy autenticado como niño en la pantalla de encender la chispa
    When envío una curiosidad
    Then se crea una lección (POST /lessons) y la app navega a la lección

  Scenario: Lanzar una lección desde una sugerencia
    Given veo "Islas para empezar" con sugerencias (GET /me/suggestions)
    When pincho una sugerencia
    Then se crea y se abre una lección para ese tema

  Scenario: La lección stub es determinista
    Given no hay proveedor de IA configurado (modo demo)
    When se genera una lección
    Then su subject está en {ciencia, matematicas, lenguaje, arte, cultura}
    And el quiz tiene exactamente 3 opciones
    And el índice de la opción correcta está entre 0 y 2
```
- **Datos de prueba:** niño demo "Nora" (7 años, token `child`); curiosidad de ejemplo "¿por qué el cielo es azul?"; sugerencia de ejemplo "¿Cómo vuelan los aviones? ✈️".
- **Evidencia esperada:** captura de la pantalla de encender la chispa con la lección resultante; registro de que la lección `stub` es determinista (mismo input → mismo output) con quiz de 3 opciones.

#### Bloque 5 — Operativa

- **Prioridad:** Alta.
- **Justificación de la prioridad:** Es el corazón de la propuesta de valor (curiosidad → lección); sin ella el producto no cumple su promesa central.
- **Fecha objetivo:** — (Fase de núcleo, Entrega 2).
- **Dependencias:** FE: `Spark.tsx` · BE: `POST /lessons`, `GET /me/suggestions` · Data: `lessons`, `knowledge_nodes` (isla creada al vuelo, ver US8) · UX: pantalla "Encender la chispa" e "Islas para empezar".
- **Impacto estimado:** Alto — es la acción principal y desencadena la creación de islas y el hilo conversacional.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

### US3 — Mini-lección adaptada por edad + lectura en voz alta  ·  `[Aprendizaje] Adaptar la lección por edad y leerla en voz alta`

> **Como** niño explorador, **quiero** que la lección esté escrita a mi medida y que me la puedan leer en voz alta, **para** entenderla fácilmente aunque aún no lea bien.

**Épica:** E2 · Bucle de aprendizaje  ·  **Prioridad:** Alta

#### Bloque 1 — Contexto

- **Problema:** Para que un espacio de descubrimiento sea realmente del niño, la explicación tiene que hablar su idioma: una misma respuesta no sirve para un niño de 4 años y para uno de 11, ni en vocabulario ni en longitud. Chispa apuesta por un aprendizaje corto y recordable —una sola idea con su analogía— y no por una enciclopedia que abruma. Además, quien todavía no lee con fluidez se queda fuera si el contenido es solo texto, por lo que la lectura en voz alta amplía la curiosidad de los prelectores.
- **Usuario beneficiado:** Explorador/Niño (rol).
- **Stakeholder solicitante:** Responsable de producto/negocio (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 1) Curiosidad primero, currículo después · 4) Texto canónico · 6) Aprendizaje corto y recordable.
- **RF relacionados:** RF-APR-03, RF-APR-04 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Adaptación del contenido a la **banda de edad** del explorador (3–5, 6–8, 9–12).
  - Estructura pedagógica: una sola idea con analogía, dato sorprendente y 2–3 follow-ups.
  - **Lectura en voz alta** de la lección con Web Speech Synthesis (botón 🔊), en el idioma activo.
- **Excluido explícitamente (qué NO entra):**
  - Dictado por voz de la pregunta (US11).
  - Selección manual de voz/velocidad de lectura.
  - Traducción del contenido entre idiomas.
- **MVP:** La lección se genera acorde a la banda de edad del niño y puede leerse en voz alta cuando el navegador soporta síntesis de voz.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - El contenido debe corresponder a la **banda de edad** derivada de `children.age` (3–5, 6–8, 9–12).
  - Cada lección presenta **una sola idea**, con analogía, un dato sorprendente y **2 o 3 follow-ups**.
  - La **lectura en voz alta** es best-effort: solo se ofrece si el navegador soporta síntesis de voz; usa el idioma activo.
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `children.age` | Derivado de `birthdate` | `children` (calculado) | Determina la banda de edad |
  | `lessons.body` | Generador de lección | `lessons` | Adaptado a la banda |
  | `lessons.fun_fact` | Generador de lección | `lessons` | Dato sorprendente |
  | `lessons.follow_ups` | Generador de lección | `lessons` | 2–3 sugerencias (`nullable`) |
  | Idioma activo | Contexto i18n (FE) | Cliente | Guía la voz de lectura |
- **Integraciones implicadas:** **Web Speech API (SpeechSynthesis)** — opcional/best-effort, solo en navegadores compatibles. Proveedor de IA de texto para la adaptación por edad (opcional; `stub` en modo demo).
- **Casuística (happy + límites + errores):**
  - Happy path: un niño de 7 años abre una lección de banda 6–8 y pulsa 🔊 para escucharla.
  - Caso límite 1: navegador sin síntesis de voz → el botón 🔊 no ofrece lectura, pero la lección se lee en pantalla.
  - Caso límite 2: idioma activo distinto del navegador por defecto → la lectura usa el idioma activo.
  - Error esperado: la síntesis de voz falla en el dispositivo → se degrada sin romper la lección.

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Mini-lección adaptada por edad

  Scenario: Adaptación a la banda de edad
    Given soy un explorador con una edad concreta
    When abro una lección
    Then su contenido corresponde a mi banda de edad (3-5, 6-8 o 9-12)
    And presenta una sola idea con una analogía, un dato sorprendente y 2 o 3 follow-ups

  Scenario: Lectura en voz alta
    Given estoy en una lección y el navegador soporta síntesis de voz
    When pulso el botón 🔊
    Then la lección se lee con Web Speech Synthesis en el idioma activo
```
- **Datos de prueba:** exploradores de prueba de 4, 7 y 10 años para cubrir las tres bandas; una misma curiosidad ("¿por qué llueve?") comparada entre bandas; navegador con y sin `speechSynthesis`.
- **Evidencia esperada:** capturas comparando el cuerpo de la lección entre bandas de edad; vídeo con el botón 🔊 leyendo la lección en el idioma activo.

#### Bloque 5 — Operativa

- **Prioridad:** Alta.
- **Justificación de la prioridad:** La adaptación por edad y la lectura en voz alta son las que hacen la lección realmente comprensible para prelectores; sin ellas el valor educativo cae mucho.
- **Fecha objetivo:** — (Fase de núcleo, Entrega 2).
- **Dependencias:** FE: `LessonScreen.tsx`, componente `SpeakButton` · BE: `POST /lessons`, `GET /lessons/{id}/thread` · Data: `lessons` (`body`, `fun_fact`, `follow_ups`), `children.age` · UX: diseño de la lección y del botón de lectura.
- **Impacto estimado:** Medio-alto — mejora sustancialmente la accesibilidad y comprensión del contenido central.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

### US4 — Reto (quiz) que sube la maestría  ·  `[Aprendizaje] Resolver el reto y subir la maestría de la isla`

> **Como** niño explorador, **quiero** poner a prueba lo aprendido con un reto rápido, **para** afianzar el concepto y ver crecer mi dominio de esa isla, sin castigo si me equivoco.

**Épica:** E2 · Bucle de aprendizaje  ·  **Prioridad:** Alta

#### Bloque 1 — Contexto

- **Problema:** Leer una lección no garantiza que el concepto se asiente. En un espacio personal de descubrimiento con **memoria pedagógica**, hace falta un cierre activo y breve que consolide lo aprendido y actualice la Ficha de Conocimiento del niño, subiendo la maestría de esa isla (`knowledge_nodes`). Ese progreso debe sentirse honesto: sin castigo al equivocarse ni mecánicas que manipulen, porque la señal de dominio es lo que después guía la experiencia, no un simple marcador de deberes.
- **Usuario beneficiado:** Explorador/Niño (rol).
- **Stakeholder solicitante:** Responsable de producto/negocio (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 3) La ficha manda · 5) Progreso sin manipulación · 6) Aprendizaje corto y recordable.
- **RF relacionados:** RF-APR-05, RF-SEG-01 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Resolver el reto de una lección (`POST /lessons/{id}/answer`) y recibir si es correcto, la explicación y el concepto.
  - **Subir la maestría** del `KnowledgeNode` asociado al acertar.
  - **Sin penalización** al fallar.
  - Garantía de que el backend nunca revela la respuesta correcta antes de responder.
- **Excluido explícitamente (qué NO entra):**
  - Reintentos con penalización o límite de intentos.
  - Sistema de puntos, insignias o rankings.
  - Descenso de maestría (no existe penalización).
- **MVP:** El niño responde el reto; si acierta, sube la maestría de la isla; si falla, no pasa nada; la respuesta correcta nunca viaja al cliente antes de responder.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - **Secreto del quiz (seguridad):** `LessonRead` **nunca** expone `quiz_correct_index` ni `quiz_explanation`; la corrección se calcula **solo en el servidor** y la explicación solo se devuelve en la respuesta de `answer`. Garantía en tres capas (esquema `QuizPublic`, serialización `to_read_dict`, validación `answer_lesson`).
  - Al **acertar**, el servicio hace *upsert* del nodo (`concept` + `subject`) e incrementa `mastery`; se marca `lessons.answered = true`.
  - Al **fallar**, `correct=false` y la maestría **no** cambia (sin penalización).
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `lessons.quiz_correct_index` | Generador de lección | `lessons` | Solo en servidor, nunca serializado |
  | `lessons.quiz_explanation` | Generador de lección | `lessons` | Solo tras responder |
  | `lessons.answered` | Servicio de respuesta | `lessons` | `def=False` → `True` al acertar |
  | `knowledge_nodes.mastery` | *Upsert* al acertar | `knowledge_nodes` | `def=1`, sube al acertar |
  | `knowledge_nodes.concept` / `subject` | Lección acertada | `knowledge_nodes` | Clave del *upsert* |
- **Integraciones implicadas:** Ninguna externa. Toda la lógica de corrección y maestría es interna del servidor.
- **Casuística (happy + límites + errores):**
  - Happy path: el niño responde correctamente → `correct=true` y sube la maestría de la isla.
  - Caso límite 1: el niño falla → `correct=false`, sin penalización.
  - Caso límite 2: inspección del tráfico de red de `GET /lessons/{id}` → no aparece la opción correcta ni la explicación.
  - Error esperado: responder una lección inexistente o ajena → `404`.

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Reto que sube la maestría

  Scenario: Respuesta correcta
    Given estoy resolviendo el reto de una lección
    When respondo correctamente (POST /lessons/{id}/answer)
    Then la respuesta indica correct=true
    And sube la maestría del KnowledgeNode asociado

  Scenario: Respuesta incorrecta (sin penalización)
    Given estoy resolviendo el reto de una lección
    When respondo de forma incorrecta
    Then la respuesta indica correct=false
    And no se penaliza mi maestría

  Scenario: El backend nunca revela la respuesta correcta (seguridad)
    Given recibo una lección con su reto
    When inspecciono la respuesta del backend
    Then no contiene el índice ni el texto de la opción correcta
```
- **Datos de prueba:** lección demo con quiz de 3 opciones e índice correcto conocido solo en servidor; niño "Nora" con una isla de mastery inicial 1; una respuesta correcta y una incorrecta.
- **Evidencia esperada:** registro del incremento de `mastery` tras acertar; captura del cuerpo de `LessonRead` mostrando que no contiene `quiz_correct_index` ni `quiz_explanation`; prueba de "sin penalización" al fallar.

#### Bloque 5 — Operativa

- **Prioridad:** Alta.
- **Justificación de la prioridad:** Cierra el bucle de aprendizaje (aprender → afianzar → progresar) y contiene una de las reglas de seguridad estrella del sistema (secreto del quiz).
- **Fecha objetivo:** — (Fase de núcleo, Entrega 2).
- **Dependencias:** FE: `LessonScreen.tsx` (bloque de reto/quiz) · BE: `POST /lessons/{id}/answer` · Data: `lessons`, `knowledge_nodes` · UX: diseño del reto y del feedback de acierto/fallo.
- **Impacto estimado:** Alto — sostiene la sensación de progreso y protege la integridad del quiz.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

## E3 · Conocimiento vivo

### US7 — Archipiélago y buscador  ·  `[Conocimiento] Ver y buscar las islas de conocimiento`

> **Como** niño explorador, **quiero** ver todas mis islas en un mapa y poder buscarlas, **para** reencontrar un tema y volver a explorarlo.

**Épica:** E3 · Conocimiento vivo  ·  **Prioridad:** Media

#### Bloque 1 — Contexto

- **Problema:** La memoria pedagógica de Chispa solo tiene valor si el niño puede verla y volver a ella. La Ficha de Conocimiento se materializa como un **archipiélago** de islas (`knowledge_nodes`): a medida que el niño explora acumula muchos temas y, sin un mapa visual ni una búsqueda tolerante, pierde de vista lo que ya descubrió y su curiosidad no encuentra por dónde continuar. El objetivo no es un índice de contenidos, sino un espacio propio que invita a reexplorar.
- **Usuario beneficiado:** Explorador/Niño (rol).
- **Stakeholder solicitante:** Responsable de producto/negocio (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 3) La ficha manda · 1) Curiosidad primero, currículo después.
- **RF relacionados:** RF-CON-01, RF-CON-02, RF-CON-03 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Mapa (archipiélago) con todas las islas del niño (`GET /me/knowledge`).
  - Buscador **insensible a acentos y mayúsculas**.
  - Mensaje de "sin resultados" solo cuando el niño tiene al menos una isla.
  - Abrir la conversación guardada de una isla (`root_lesson_id`).
- **Excluido explícitamente (qué NO entra):**
  - Filtros por materia o por nivel de maestría.
  - Ordenación configurable o vistas alternativas del mapa.
  - Edición o borrado de islas por el niño.
- **MVP:** El niño ve sus islas, las busca sin preocuparse por acentos o mayúsculas y abre la conversación guardada de la que elija.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - La búsqueda coincide de forma **insensible a acentos y a mayúsculas/minúsculas**.
  - El mensaje de **"sin resultados"** aparece solo si el niño tiene ≥ 1 isla; con 0 islas no se muestra.
  - Al pinchar una isla se abre su conversación guardada a partir de `knowledge_nodes.root_lesson_id`.
  - **Aislamiento:** un niño solo ve sus propias islas (`knowledge_nodes.child_id`).
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `knowledge_nodes.concept` | Lecciones del niño | `knowledge_nodes` | Nombre buscable de la isla |
  | `knowledge_nodes.subject` | Lecciones del niño | `knowledge_nodes` | Materia asociada |
  | `knowledge_nodes.mastery` | Retos acertados (US4) | `knowledge_nodes` | Nivel de dominio |
  | `knowledge_nodes.root_lesson_id` | Lección raíz del tema | `knowledge_nodes` | Enlace lógico a la conversación |
- **Integraciones implicadas:** Ninguna. Normalización de texto (para búsqueda sin acentos) resuelta en cliente.
- **Casuística (happy + límites + errores):**
  - Happy path: el niño escribe "leon" y encuentra la isla "León".
  - Caso límite 1: búsqueda sin coincidencias con islas existentes → "sin resultados".
  - Caso límite 2: niño sin ninguna isla → no se muestra el mensaje de "sin resultados".
  - Error esperado: intento de abrir una isla de otro niño → no accesible (aislamiento por `child_id`).

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Archipiélago y buscador

  Scenario: Buscar una isla sin distinción de acentos ni mayúsculas
    Given tengo varias islas en mi archipiélago
    When busco un texto (con o sin acentos, en mayúsculas o minúsculas)
    Then se muestran las islas cuyo nombre coincide de forma insensible a acentos y mayúsculas

  Scenario: Mensaje de "sin resultados" solo si hay islas
    Given tengo al menos una isla
    When mi búsqueda no coincide con ninguna
    Then se muestra "sin resultados"
    But si no tengo ninguna isla, no se muestra ese mensaje

  Scenario: Abrir la conversación guardada de una isla
    Given veo una isla en el mapa
    When la pincho
    Then se abre su conversación guardada (root_lesson_id)
```
- **Datos de prueba:** niño con islas "León", "Volcanes" y "Números"; búsquedas "leon", "LEÓN", "vol"; un niño recién creado sin islas.
- **Evidencia esperada:** capturas del archipiélago con resultados de búsqueda tolerante a acentos; vídeo de apertura de la conversación guardada al pinchar una isla; caso "sin islas" sin mensaje de vacío.

#### Bloque 5 — Operativa

- **Prioridad:** Media.
- **Justificación de la prioridad:** Da persistencia y sentido de progreso al conocimiento acumulado; es muy valiosa, pero depende de que exista contenido generado por el bucle de aprendizaje (E2).
- **Fecha objetivo:** — (Fase de núcleo, Entrega 2).
- **Dependencias:** FE: `MyKnowledge.tsx` · BE: `GET /me/knowledge` · Data: `knowledge_nodes`, `lessons` (por `root_lesson_id`) · UX: diseño del mapa de islas y del buscador.
- **Impacto estimado:** Medio — refuerza retención y reengagement, sin ser bloqueante del bucle principal.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

### US8 — Chat con contexto e islas automáticas  ·  `[Conocimiento] Repreguntar en el hilo y crear islas automáticas`

> **Como** niño explorador, **quiero** seguir preguntando en el mismo hilo y que cada tema se guarde solo como una isla, **para** profundizar sin perder el contexto de mi conversación.

**Épica:** E3 · Conocimiento vivo  ·  **Prioridad:** Media

#### Bloque 1 — Contexto

- **Problema:** La curiosidad genuina encadena preguntas ("¿y por qué…?"), y un espacio personal de descubrimiento debe acompañar esa cadena en lugar de cortarla. Si cada pregunta empieza de cero se pierde el contexto y el niño no puede profundizar; y si tuviera que guardar manualmente cada tema, la fricción apagaría su exploración. Por eso la memoria pedagógica trabaja sola: cada tema se sedimenta como una isla de la Ficha de Conocimiento (`knowledge_nodes`) sin que el niño tenga que pensar en ello.
- **Usuario beneficiado:** Explorador/Niño (rol).
- **Stakeholder solicitante:** Responsable de producto/negocio (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 1) Curiosidad primero, currículo después · 3) La ficha manda.
- **RF relacionados:** RF-CON-04, RF-CON-05, RF-CON-01 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Creación **automática** de una isla (`knowledge_node`) al crear la lección, sin necesidad de responder el quiz.
  - Repreguntar en el hilo (`POST /lessons/{id}/ask`) creando un nuevo turno con `parent_id` y `root_id`.
  - Recuperar el hilo ordenado (`GET /lessons/{id}/thread`), con la raíz primero.
  - Garantía de que repreguntar **no** sube la maestría.
- **Excluido explícitamente (qué NO entra):**
  - Ramificación explícita de hilos por parte del niño.
  - Edición o borrado de turnos de la conversación.
  - Fusión de islas duplicadas.
- **MVP:** El niño puede repreguntar manteniendo contexto y cada tema queda guardado como isla automáticamente, sin que repreguntar altere su maestría.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - Al crear una lección se crea **1 nodo (isla)** para ese tema, aunque no se responda el quiz.
  - `POST /lessons/{id}/ask` crea una **nueva fila `Lesson`** con `parent_id` (turno anterior) y `root_id` (primer turno del hilo); son enteros **lógicos**, resueltos por consulta en la aplicación.
  - `GET /lessons/{id}/thread` devuelve los turnos **en orden, con la raíz primero**.
  - **Repreguntar no sube la maestría:** solo el quiz respondido correctamente (US4) la incrementa.
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `lessons.parent_id` | Turno anterior del hilo | `lessons` | Entero lógico, sin FK |
  | `lessons.root_id` | Primer turno del hilo | `lessons` | Entero lógico, `index=True` |
  | `knowledge_nodes` (nodo) | Creación de la lección | `knowledge_nodes` | 1 isla por tema al crear |
  | `knowledge_nodes.root_lesson_id` | Lección raíz | `knowledge_nodes` | Enlace lógico a la conversación |
  | `knowledge_nodes.mastery` | Solo quiz acertado | `knowledge_nodes` | No cambia al repreguntar |
- **Integraciones implicadas:** Proveedor de IA de texto para generar los turnos de seguimiento (opcional; `stub` en modo demo).
- **Casuística (happy + límites + errores):**
  - Happy path: el niño enciende una chispa, repregunta dos veces y recupera el hilo ordenado con la raíz primero.
  - Caso límite 1: consulta `GET /me/knowledge` sin responder ningún quiz → ya aparece 1 isla para ese tema.
  - Caso límite 2: repregunta varias veces sin responder ningún quiz → la maestría no cambia.
  - Error esperado: repreguntar sobre una lección inexistente o ajena → `404`; curiosidad de seguimiento inapropiada → `422`.

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Chat con contexto e islas automáticas

  Scenario: Isla creada automáticamente al crear la lección
    Given enciendo una chispa y se crea una lección
    When consulto GET /me/knowledge sin haber respondido el quiz
    Then aparece 1 nodo (isla) para ese tema

  Scenario: Repreguntar en el hilo con contexto
    Given tengo una lección raíz
    When repregunto (POST /lessons/{root}/ask)
    Then se crea un turno con parent_id y root_id manteniendo el contexto

  Scenario: Hilo en orden
    Given tengo una conversación con varios turnos
    When consulto GET /lessons/{root}/thread
    Then los turnos se devuelven en orden, con la raíz primero

  Scenario: Repreguntar no sube la maestría
    Given estoy en una conversación
    When repregunto (sin responder ningún quiz correctamente)
    Then mi maestría no cambia
    And solo el quiz respondido correctamente la sube
```
- **Datos de prueba:** lección raíz sobre "volcanes"; dos repreguntas encadenadas ("¿y por qué explotan?", "¿dónde hay volcanes?"); comprobación de `mastery` antes y después de repreguntar.
- **Evidencia esperada:** registro del hilo devuelto en orden (raíz primero); captura de `GET /me/knowledge` mostrando la isla creada sin responder el quiz; verificación de que la maestría no varía al repreguntar.

#### Bloque 5 — Operativa

- **Prioridad:** Media.
- **Justificación de la prioridad:** Aporta profundidad y contexto al aprendizaje y automatiza el guardado de islas; es un multiplicador de valor sobre el bucle base (E2), no un prerrequisito de él.
- **Fecha objetivo:** — (Fase de núcleo, Entrega 2).
- **Dependencias:** FE: `LessonScreen.tsx`, `MyKnowledge.tsx` · BE: `POST /lessons/{id}/ask`, `GET /lessons/{id}/thread`, `GET /me/knowledge` · Data: `lessons` (`parent_id`, `root_id`), `knowledge_nodes` (`root_lesson_id`) · UX: diseño del hilo conversacional y la relación isla↔conversación.
- **Impacto estimado:** Medio-alto — sostiene la profundización sin fricción y la persistencia automática del conocimiento.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

## E4 · Cuentos

### US9 — Biblioteca de cuentos con aprobación parental  ·  `[Cuentos] Crear cuentos con aprobación parental`

> **Como** familia, **quiero** que los cuentos que crea mi hijo pasen por mi aprobación antes de que él pueda leerlos, **para** garantizar que el contenido es apropiado; **y como** niño, **quiero** crear mis propios cuentos.

**Épica:** E4 · Cuentos  ·  **Prioridad:** Media

#### Bloque 1 — Contexto

- **Problema:** Crear cuentos es una de las formas más ricas en que un niño expande su curiosidad, pero en un producto para menores ningún contenido generado puede mostrarse sin supervisión. El reto es sostener la agencia del niño (crear libremente) sin renunciar a la seguridad infantil: la familia decide qué se publica, y el texto que el niño ve es el texto canónico aprobado, no una versión que cambie a sus espaldas.
- **Usuario beneficiado:** Familia/Adulto (rol) y Explorador/Niño (rol).
- **Stakeholder solicitante:** Product Owner (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 2) Seguridad infantil por diseño · 7) Padres con control, niño con agencia · 4) Texto canónico.
- **RF relacionados:** RF-CUE-01, RF-CUE-02, RF-CUE-03, RF-SEG-02 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - El niño crea cuentos (`POST /me/stories`) que quedan en estado `pending`.
  - El niño solo ve sus cuentos `approved`.
  - La familia lista todos (con filtro opcional por estado), aprueba o rechaza (`PUT /family/stories/{id}`) y puede editar `title`/`body` al aprobar.
  - Al rechazar se conserva el texto original.
  - Aislamiento entre familias.
- **Excluido explícitamente (qué NO entra):**
  - Ilustración del cuento con imágenes IA (depende de US10/US11).
  - Publicación o compartición fuera de la familia.
  - Comentarios o valoraciones de cuentos.
- **MVP:** El niño crea un cuento que queda pendiente; la familia lo aprueba (opcionalmente editándolo) o lo rechaza; el niño solo ve los aprobados.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - **Aprobación parental obligatoria:** un cuento nace `pending` y **no aparece** en la lista ni en el detalle del niño (`404`) hasta ser `approved`.
  - Flujo de estado: `pending` → `approved` / `rejected` (decisión de la familia). Se registra `reviewed_at`.
  - Al **rechazar** (`action=reject`), el cuento queda `rejected` y **conserva su texto original**.
  - Al **aprobar** (`action=approve`), la familia puede editar `title`/`body`.
  - **Aislamiento entre familias:** un cuento de otra familia responde `404`.
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `stories.title` / `body` | Creación del niño / edición familiar | `stories` | Editables al aprobar |
  | `stories.status` | Creación / revisión | `stories` | `pending` → `approved` \| `rejected` |
  | `stories.reviewed_at` | Revisión familiar | `stories` | `nullable`; se fija al revisar |
  | `stories.child_id` | Niño autor | `stories` | Base del aislamiento por familia |
- **Integraciones implicadas:** Ninguna obligatoria. La generación asistida del texto del cuento por IA es opcional/best-effort y depende de la config de US10.
- **Casuística (happy + límites + errores):**
  - Happy path: el niño crea un cuento; la familia lo aprueba editando el título; el niño ya lo ve.
  - Caso límite 1: la familia rechaza el cuento → queda `rejected` conservando el texto original.
  - Caso límite 2: el niño intenta ver un cuento aún `pending` → `404`.
  - Error esperado: acceso a un cuento de otra familia → `404` (aislamiento).

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Cuentos con aprobación parental

  Scenario: El niño crea un cuento (queda pendiente)
    Given estoy autenticado como niño
    When creo un cuento (POST /me/stories)
    Then queda en estado pending
    And no aparece en mi lista ni en mi detalle (404) hasta ser aprobado

  Scenario: La familia aprueba y edita
    Given hay un cuento pendiente
    When la familia lo aprueba (PUT /family/stories/{id}, action=approve) editando título o cuerpo
    Then el cuento pasa a aprobado y el niño ya lo ve

  Scenario: La familia rechaza (conserva el original)
    Given hay un cuento pendiente
    When la familia lo rechaza (action=reject)
    Then el cuento queda en estado rejected
    And conserva su texto original

  Scenario: Aislamiento entre familias
    Given un cuento pertenece a otra familia
    When intento acceder a él
    Then la respuesta es 404
```
- **Datos de prueba:** cuento demo "El zorro y la luna" creado por "Nora" (queda `pending`); una segunda familia con su propio cuento para probar el aislamiento; edición de título al aprobar.
- **Evidencia esperada:** vídeo del ciclo crear → aprobar/editar → visible para el niño; captura de `404` cuando el cuento está `pending` o pertenece a otra familia; registro de que el rechazo conserva el texto original.

#### Bloque 5 — Operativa

- **Prioridad:** Media.
- **Justificación de la prioridad:** Aporta una vía creativa muy valorada y refuerza la confianza parental mediante moderación; no es parte del bucle núcleo de aprendizaje, por lo que va después de E2/E3.
- **Fecha objetivo:** — (Fase de cuentos, Entrega 2–3).
- **Dependencias:** FE: `StoryLibrary.tsx`, `FamilyStories.tsx` · BE: `POST /me/stories`, `GET /me/stories`, `GET /me/stories/{id}`, `GET /family/stories`, `PUT /family/stories/{id}` · Data: `stories` · UX: biblioteca del niño y bandeja de moderación de la familia.
- **Impacto estimado:** Medio — amplía el valor creativo y de confianza, aislado del bucle principal.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

## E5 · IA configurable

### US10 — IA multiproveedor por familia (texto + imagen)  ·  `[IA] Configurar proveedor de IA por familia con BYOK`

> **Como** familia, **quiero** elegir y configurar el proveedor de IA (o quedarme en modo demo) con mi propia clave guardada de forma segura, **para** controlar la calidad, el coste y la privacidad del contenido que consume mi hijo.

**Épica:** E5 · IA configurable  ·  **Prioridad:** Alta

#### Bloque 1 — Contexto

- **Problema:** La IA es la que da voz al espacio de descubrimiento, pero cada familia tiene una tolerancia distinta al coste, la calidad y la privacidad del contenido que consume su hijo. Sin una configuración propia, o se impone un proveedor único a todos o se exponen claves de API de forma insegura, algo inaceptable en un producto para menores. Chispa lo resuelve de forma incremental: arranca en un modo demo seguro sin claves y deja que la familia suba de nivel (BYOK) cuando quiera, con los secretos siempre protegidos.
- **Usuario beneficiado:** Familia/Adulto (rol).
- **Stakeholder solicitante:** Tech Lead (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 2) Seguridad infantil por diseño · 8) Diseño incremental.
- **RF relacionados:** RF-IA-01, RF-IA-02, RF-IA-03, RF-IA-04, RF-IA-05, RF-IA-06 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Configuración por defecto en **modo demo** (`tier=free`, `provider=stub`, `has_api_key=false`).
  - Guardar clave propia (**BYOK**) sin exponerla: la respuesta nunca devuelve la clave; se almacena cifrada con Fernet.
  - Validación de proveedor habilitado (`422` si no lo está).
  - Recomendador de modelo local por hardware (`POST /family/ai-config/recommend`).
  - Configuración paralela de proveedor de **imagen** (por defecto `none`, `image_enabled=false`).
- **Excluido explícitamente (qué NO entra):**
  - Facturación o medición de coste real por proveedor.
  - Descarga/instalación automática de modelos locales.
  - Rotación automática de claves o gestión de secretos externa (KMS).
- **MVP:** Una familia puede permanecer en modo demo o pasar a BYOK con su clave (guardada cifrada y nunca devuelta), viendo `has_api_key=true` sin exponer el secreto.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - **Las claves nunca se exponen (seguridad/privacidad):** `AIConfigRead` devuelve `has_api_key` / `has_image_api_key` (booleanos), nunca `api_key_encrypted` ni `image_api_key_encrypted`.
  - Las claves se reciben **en claro solo en la petición de escritura** y se **cifran con Fernet** antes de persistirse; requiere la variable de entorno `AI_CONFIG_KEY` (su ausencia da `400`).
  - `tier` ∈ {free, byok, managed} y `provider` ∈ {stub, ollama, claude, openai, gemini, deepseek, kimi}; valor fuera del conjunto → `422`.
  - `image_provider` ∈ {none, huggingface, local_sdxl, openai, gemini, pollinations}; la generación de imágenes está **desactivada por defecto**.
  - Relación **1:1** con la familia (`family_ai_config.family_id` único).
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `family_ai_config.tier` | `PUT /family/ai-config` | `family_ai_config` | `def=free` |
  | `family_ai_config.provider` | `PUT /family/ai-config` | `family_ai_config` | `def=stub` |
  | `family_ai_config.api_key_encrypted` | Clave en claro → Fernet | `family_ai_config` | Nunca serializada; expone `has_api_key` |
  | `family_ai_config.model` / `base_url` | `PUT /family/ai-config` | `family_ai_config` | `nullable` |
  | `family_ai_config.image_provider` | `PUT /family/ai-config` | `family_ai_config` | `def=none` |
  | `family_ai_config.image_api_key_encrypted` | Clave imagen → Fernet | `family_ai_config` | Nunca serializada; expone `has_image_api_key` |
  | `family_ai_config.image_enabled` | `PUT /family/ai-config` | `family_ai_config` | `def=False` |
- **Integraciones implicadas:** Proveedores de IA de **texto** (Ollama, Claude, OpenAI, Gemini, DeepSeek, Kimi — todos opcionales; `stub` por defecto) y de **imagen** (HuggingFace, local SDXL, OpenAI, Gemini, Pollinations — opcionales, desactivados por defecto). Cifrado **Fernet** interno para las claves.
- **Casuística (happy + límites + errores):**
  - Happy path: la familia guarda `provider=claude` con su `api_key`; `has_api_key` pasa a `true` y la respuesta no contiene la clave.
  - Caso límite 1: familia sin configurar → `tier=free`, `provider=stub`, `has_api_key=false`.
  - Caso límite 2: la familia consulta el recomendador con su VRAM/RAM y recibe un modelo local acorde.
  - Error esperado: proveedor no habilitado → `422`; falta `AI_CONFIG_KEY` al cifrar → `400`.

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: IA multiproveedor por familia

  Scenario: Configuración por defecto (modo demo)
    Given no he configurado nada
    When consulto la configuración de IA
    Then tier=free, provider=stub y has_api_key=false

  Scenario: Guardar clave propia (BYOK) sin exponerla
    Given quiero usar Claude
    When guardo provider=claude con mi api_key
    Then has_api_key pasa a true
    And la respuesta NO contiene la clave (se almacena cifrada con Fernet)

  Scenario: Proveedor deshabilitado
    Given intento configurar un proveedor no habilitado
    When guardo la configuración
    Then la respuesta es 422

  Scenario: Recomendador de modelo local por hardware
    Given quiero un modelo local
    When envío mi VRAM y RAM (POST /family/ai-config/recommend)
    Then recibo una recomendación de modelo acorde a mi hardware
```
- **Datos de prueba:** familia demo sin configurar (espera `free`/`stub`); `PUT` con `provider=claude` y `api_key=sk-demo-xxxx`; consulta de hardware `{vram_gb: 8, ram_gb: 16}`; intento con un `provider` no habilitado.
- **Evidencia esperada:** captura de `AIConfigRead` mostrando `has_api_key=true` sin la clave; registro del `422` por proveedor no habilitado y del `400` por falta de `AI_CONFIG_KEY`; salida del recomendador para un hardware de ejemplo.

#### Bloque 5 — Operativa

- **Prioridad:** Alta.
- **Justificación de la prioridad:** Habilita calidad real de contenido y controla coste/privacidad; además concentra el manejo seguro de secretos (Fernet), crítico en un producto para menores.
- **Fecha objetivo:** — (Fase de IA configurable, Entrega 2–3).
- **Dependencias:** FE: `AIConfigPanel.tsx` · BE: `GET /family/ai-config`, `PUT /family/ai-config`, `GET /family/ai-config/catalog`, `POST /family/ai-config/recommend` · Data: `family_ai_config` · UX: panel de configuración de IA (texto + imagen) y recomendador.
- **Impacto estimado:** Alto — determina la calidad del contenido de todo el bucle y fija el modelo de seguridad de claves.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

## E6 · Plataforma y accesibilidad

### US5/US6 — Panel de familia (supervisión, ficha, seguridad)  ·  `[Plataforma] Supervisar actividad y ficha de conocimiento del niño`

> **Como** familia, **quiero** un panel donde ver la actividad y la ficha de conocimiento de cada niño, **para** supervisar su aprendizaje y su seguridad.

**Épica:** E6 · Plataforma y accesibilidad  ·  **Prioridad:** Media

#### Bloque 1 — Contexto

- **Problema:** Un espacio personal del niño no significa un espacio opaco para su familia. Para acompañar la curiosidad y velar por la seguridad, el adulto necesita ver qué descubre cada hijo y cómo progresa, leyendo directamente su Ficha de Conocimiento (el archipiélago de `knowledge_nodes` y su perfil): conceptos fuertes y emergentes. Sin este panel, la memoria pedagógica queda invisible para quien debe acompañar, y se pierde el equilibrio entre padres con control y niño con agencia.
- **Usuario beneficiado:** Familia/Adulto (rol).
- **Stakeholder solicitante:** Product Owner (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 3) La ficha manda · 7) Padres con control, niño con agencia · 5) Progreso sin manipulación.
- **RF relacionados:** RF-PLT-01, RF-SEG-02 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Panel con la actividad de cada niño: su archipiélago, que **es** su historial de temas explorados.
  - Ficha de conocimiento con conceptos fuertes y emergentes.
  - Selector de niño para conmutar entre hijos.

  > **Corregido en implementación (14-09-2026):** esta historia suponía servir el panel desde los
  > endpoints `/me/*`, pero esos exigen token `child` por diseño (JWT tipado, ADR-002). Dar acceso a
  > la familia habría roto una garantía de seguridad, así que se añadieron endpoints propios de
  > familia: `GET /children/{id}/profile` y `GET /children/{id}/knowledge`. El listado lección a
  > lección queda fuera de este incremento.
- **Excluido explícitamente (qué NO entra):**
  - Alertas o notificaciones proactivas a la familia.
  - Informes exportables (PDF/email).
  - Límites de tiempo o controles de uso configurables.
- **MVP:** La familia selecciona un niño y ve su actividad y su ficha de conocimiento (conceptos fuertes y emergentes).

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - La familia solo ve a **sus** niños; los datos se derivan de los endpoints del espacio del niño (`/me/*`).
  - La **ficha de conocimiento** distingue conceptos fuertes (mayor `mastery`) y emergentes.
  - `islands` es un campo **derivado** en la respuesta = número de `knowledge_nodes` del niño.
  - El selector de niño cambia el contexto de datos mostrado sin mezclar información entre hijos.
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `ChildProfile` `{name, age, islands, avatar, avatar_image_url}` | `GET /children/{id}/profile` | `children` (+ derivado) | `islands` derivado de `knowledge_nodes` |
  | `knowledge_nodes` (ficha) | `GET /children/{id}/knowledge` | `knowledge_nodes` | `mastery >= 2` fuerte · `mastery == 1` emergente |
- **Integraciones implicadas:** Ninguna. Solo agregación de datos internos del niño.
- **Casuística (happy + límites + errores):**
  - Happy path: la familia abre el panel, selecciona a un niño y ve su actividad y ficha.
  - Caso límite 1: familia con varios niños → el selector conmuta correctamente los datos.
  - Caso límite 2: niño recién creado sin actividad → panel con ficha vacía coherente (0 islas).
  - Error esperado: acceso con token de tipo incorrecto a datos del niño → `401` (aislamiento de sesiones, ver US1).

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Panel de familia

  Scenario: Ver actividad y ficha del niño
    Given estoy autenticado como familia con al menos un niño
    When abro el panel y selecciono un niño
    Then veo su actividad e historial
    And su ficha de conocimiento con conceptos fuertes y emergentes

  Scenario: Selector de niño
    Given tengo varios niños
    When cambio de niño en el selector
    Then el panel muestra los datos del niño seleccionado
```
- **Datos de prueba:** familia con dos niños ("Nora", 7 años, con islas; "Leo", 4 años, sin actividad); ficha con conceptos de distinta `mastery`.
- **Evidencia esperada:** capturas del panel con actividad y ficha; vídeo del selector de niño conmutando datos entre hermanos; caso del niño sin actividad con ficha vacía coherente.

#### Bloque 5 — Operativa

- **Prioridad:** Media.
- **Justificación de la prioridad:** Refuerza la confianza y el acompañamiento parental; es muy valiosa para la familia, pero se apoya en datos que generan E2/E3, por lo que va después de ellas.
- **Fecha objetivo:** — (Fase de plataforma, Entrega 2–3).
- **Dependencias:** FE: `FamilyPanel.tsx` · BE: `GET /children/{id}/profile`, `GET /children/{id}/knowledge` · Data: `children`, `knowledge_nodes` · UX: diseño del panel de supervisión y del selector de niño.
- **Impacto estimado:** Medio — clave para la confianza parental; se apoyará en los datos que el niño vaya generando (lecciones e islas de `knowledge_nodes`), sin capturar información adicional.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

### US11 — Voz, imágenes IA, QR/LAN e i18n  ·  `[Plataforma] Habilitar voz, imágenes, QR/LAN e idioma`

> **Como** niño y como familia, **quiero** dictar preguntas, ver imágenes cuando estén activas, conectar el móvil por QR y usar la app en mi idioma, **para** que la experiencia sea accesible en cualquier dispositivo.

**Épica:** E6 · Plataforma y accesibilidad  ·  **Prioridad:** Media

#### Bloque 1 — Contexto

- **Problema:** La accesibilidad decide a cuántos niños llega este espacio de descubrimiento: un prelector necesita dictar y escuchar, una familia quiere usar el móvil junto al ordenador, y el idioma del entorno debe respetarse para que la curiosidad se exprese con naturalidad. Sin estas capacidades, la experiencia queda limitada a teclado, un solo dispositivo y un solo idioma. Son mejoras transversales que se añaden de forma incremental sobre un texto canónico ya sólido, sin alterar el contenido que el niño consume.
- **Usuario beneficiado:** Explorador/Niño (rol) y Familia/Adulto (rol).
- **Stakeholder solicitante:** Responsable de producto/negocio (rol; persona por asignar).
- **Validador funcional (UAT):** QA / Validador funcional (rol; persona por asignar).
- **Principios aplicables:** 4) Texto canónico · 8) Diseño incremental · 2) Seguridad infantil por diseño.
- **RF relacionados:** RF-PLT-02, RF-PLT-03, RF-PLT-04, RF-PLT-05 (ver [Requisitos](requisitos.md))

#### Bloque 2 — Alcance

- **En este incremento (qué entra):**
  - Dictado de la pregunta por voz (Web Speech API), en el idioma activo.
  - Ocultar el micrófono si el navegador no soporta reconocimiento de voz.
  - Generación de avatar por IA respetando el interruptor de imágenes (`409` si está desactivada).
  - Conexión del móvil por **QR/LAN** basada en `window.location.origin`.
  - **i18n**: detección del idioma del navegador (es/en) y cambio manual.
- **Excluido explícitamente (qué NO entra):**
  - Idiomas más allá de es/en.
  - Emparejamiento seguro del dispositivo móvil (autenticación por QR).
  - Edición avanzada del avatar generado.
- **MVP:** El niño puede dictar su curiosidad cuando el navegador lo soporta, la app respeta el idioma del entorno y se puede conectar el móvil por QR; las imágenes IA solo funcionan si la familia las activó.

#### Bloque 3 — Funcional

- **Reglas de negocio críticas:**
  - El **dictado por voz** es best-effort: solo se ofrece si el navegador soporta la Web Speech API; en caso contrario, el botón de micrófono **no se muestra**.
  - La **generación de imágenes está desactivada por defecto** (`image_enabled=false`, ver US10); generar un avatar con la imagen desactivada devuelve `409`.
  - La **conexión por QR** usa `window.location.origin` (URL de la LAN) y muestra su código QR.
  - **i18n:** el idioma se detecta del navegador (es/en) y puede cambiarse manualmente; guía también la voz de dictado y de lectura (US3).
- **Datos / campos / estados afectados:**
  | Campo / entidad | Origen | Sistema maestro | Notas |
  |---|---|---|---|
  | `children.avatar_image_url` | `POST /children/{id}/avatar/generate` | `children` | `nullable`; requiere imagen activada |
  | `family_ai_config.image_enabled` | Config de imagen (US10) | `family_ai_config` | Gobierna el `409` |
  | Idioma activo (es/en) | Navegador + selección | Contexto i18n (cliente) | Detectado y cambiable |
  | URL/QR de conexión | `window.location.origin` | Cliente | Basado en la LAN |
- **Integraciones implicadas:** **Web Speech API (reconocimiento de voz)** — opcional/best-effort. **Generación de imágenes IA** — opcional, desactivada por defecto (proveedor según US10). **QR** — generación local del código a partir de la URL de la LAN.
- **Casuística (happy + límites + errores):**
  - Happy path: el niño pulsa 🎤, habla y su voz se transcribe como curiosidad en el idioma activo.
  - Caso límite 1: navegador sin reconocimiento de voz → el botón de micrófono no aparece.
  - Caso límite 2: la familia abre la app en un navegador en inglés → la interfaz arranca en `en` y puede cambiarse a `es`.
  - Error esperado: generar avatar con imágenes desactivadas → `409`.

#### Bloque 4 — Validación

- **Criterios de aceptación (Gherkin):**
```gherkin
Feature: Voz, imágenes, QR/LAN e i18n

  Scenario: Dictar la pregunta por voz
    Given el navegador soporta la Web Speech API
    When pulso el micrófono 🎤 y hablo
    Then mi voz se transcribe en el idioma activo como texto de la curiosidad

  Scenario: Sin soporte de voz
    Given el navegador no soporta reconocimiento de voz
    Then el botón de micrófono no se muestra

  Scenario: Generar avatar con imagen desactivada
    Given la generación de imágenes está desactivada (por defecto)
    When intento generar un avatar por IA
    Then la respuesta es 409

  Scenario: Conectar el móvil por QR / LAN
    Given estoy en la pantalla "Conectar móvil"
    Then veo la URL basada en window.location.origin y su código QR

  Scenario: Idioma detectado y cambiable
    Given abro la app
    Then el idioma se detecta del navegador (es/en)
    And puedo cambiarlo manualmente
```
- **Datos de prueba:** navegador con y sin `SpeechRecognition`; familia con `image_enabled=false` (espera `409` al generar avatar); descripción de avatar "un zorro astronauta"; navegador en `en` y en `es`; URL de LAN de ejemplo `http://192.168.1.20:5173`.
- **Evidencia esperada:** vídeo del dictado por voz transcribiendo la curiosidad; captura del micrófono ausente en navegador incompatible; registro del `409` con imágenes desactivadas; captura de la URL + QR de conexión y del cambio de idioma.

#### Bloque 5 — Operativa

- **Prioridad:** Media.
- **Justificación de la prioridad:** Amplía notablemente la accesibilidad y el alcance multidispositivo/multilingüe; son mejoras transversales sobre un bucle que ya aporta valor sin ellas, de ahí que vayan tras el núcleo.
- **Fecha objetivo:** — (Fase de plataforma, Entrega 2–3).
- **Dependencias:** FE: `Spark.tsx` (micrófono), `ConnectDevice.tsx`, `AddExplorer.tsx` (avatar IA), contexto i18n · BE: `POST /children/{id}/avatar/generate` (409 si imagen off) y endpoints de imagen · Data: `children.avatar_image_url`, `family_ai_config.image_enabled` · UX: micrófono, pantalla "Conectar móvil" y selector de idioma.
- **Impacto estimado:** Medio — accesibilidad y alcance amplios, sin ser bloqueante del bucle núcleo.

#### Bloque 6 — Trazabilidad IA

- **¿Generada o asistida con IA?:** Sí — redacción y futura implementación asistidas con IA (flujo SDD).
- **Plantilla / prompt previsto:** brief SDD ejecutable (ver [`05-ai-log/prompts.md`](../05-ai-log/prompts.md)).
- **Modelo previsto:** Claude (Claude Code + skills "superpowers").
- **Revisor humano (obligatorio):** Product Owner (rol; persona por asignar) — revisión de spec + calidad por agentes distintos del implementador.
- **Cambios manuales sobre el output IA:** se registrará durante la implementación (Entregas 2–3).

---

## Matriz de realización prevista (resumen)

> Plan de realización: cada historia se implementará en la(s) pantalla(s) y endpoint(s) indicados y se validará con las pruebas previstas. Es un mapa de diseño anterior a la construcción, no un registro de cobertura ya alcanzada.

| Historia | Épica | Pantalla(s) prevista(s) | Endpoint(s) previsto(s) | Prueba(s) prevista(s) |
|---|---|---|---|---|
| US1 | E1 | CreateFamily, AddExplorer, ChildAccess, ResetPassword | `/auth/*`, `/children*` | test_auth.py, test_children.py, test_password.py |
| US2 | E2 | Spark | `POST /lessons`, `/me/suggestions` | test_lessons_api.py, Spark.test.tsx |
| US3 | E2 | LessonScreen, SpeakButton | `/lessons/{id}/thread` | test_lesson_generator.py, SpeakButton.test.tsx |
| US4 | E2 | LessonScreen | `POST /lessons/{id}/answer` | test_answer_api.py, test_security.py |
| US7 | E3 | MyKnowledge | `GET /me/knowledge` | test_knowledge_root_lesson_id.py, MyKnowledge.test.tsx |
| US8 | E3 | LessonScreen, MyKnowledge | `/lessons/{id}/ask`, `/thread` | test_conversation.py |
| US9 | E4 | StoryLibrary, FamilyStories | `/me/stories`, `/family/stories` | test_story_api.py, FamilyStories.test.tsx |
| US10 | E5 | AIConfigPanel | `/family/ai-config*` | test_ai_config_api.py, test_crypto.py |
| US5/US6 | E6 | Panel de familia, ChildHeader | `/me/*` | test_me_api.py, test_me_profile.py |
| US11 | E6 | Spark, ConnectDevice, i18n | `/children/{id}/avatar/generate` | test_avatar_ai.py, MicButton.test.tsx, I18nContext.test.tsx |
