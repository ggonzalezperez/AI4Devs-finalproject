# Casos de Aceptación (BDD) — Chispa

> Entrega 1 (documental) · Máster LIDR–AI4Devs
> Rol: Agente de QA/Pruebas
>
> Este documento define los **criterios de aceptación** de cada historia de usuario (US1–US11)
> en formato **Gherkin**, redactados **antes de implementar**. Son el comportamiento que la
> implementación **deberá cumplir**, y la base de las pruebas que se escribirán bajo el ciclo
> TDD/SDD. Los IDs, títulos y alcance siguen **exactamente** el catálogo canónico de
> [`01-product/historias-usuario.md`](../01-product/historias-usuario.md). La estrategia global
> está en [`estrategia-pruebas.md`](estrategia-pruebas.md).
>
> La trazabilidad se expresa como el **tipo/área de prueba prevista** que validará cada escenario;
> los nombres de fichero de prueba que aparecen son **planificados**, no evidencia existente.

## Leyenda de trazabilidad

| Símbolo | Significado |
|---|---|
| **[AUTO]** | Se validará automáticamente en CI (pytest o vitest) |
| **[UAT]** | Se validará manualmente en navegador / con IA real |

---

## US1 — Cuenta familiar y perfiles de niño

*Como adulto responsable de una familia, quiero crear una cuenta y dar de alta a mis hijos como
"exploradores" con su PIN y avatar, para darles un acceso propio y seguro y poder recuperar mi
cuenta.*

```gherkin
Feature: Cuenta familiar y perfiles de niño

  Scenario: Crear una cuenta familiar
    Given estoy en la pantalla de crear cuenta familiar
    When introduzco nombre, email y una contraseña válida con su confirmación coincidente
    Then se crea la cuenta y recibo un token de tipo "family"
    And se me muestra una sola vez un código de recuperación con formato XXXX-XXXX

  Scenario: Las contraseñas no coinciden (validación en cliente)
    Given estoy en la pantalla de crear cuenta familiar
    When la contraseña y su confirmación no coinciden
    Then se muestra un error antes de llamar a la API

  Scenario: Añadir un explorador con PIN
    Given estoy autenticado como familia
    When añado un explorador con avatar, alias, fecha de nacimiento y un PIN de 4 dígitos confirmado
    Then se crea el perfil con la edad calculada a partir de la fecha de nacimiento

  Scenario: Acceso del niño con PIN correcto
    Given existe un explorador con PIN
    When el niño introduce el PIN correcto
    Then recibe un token de tipo "child"

  Scenario: Separación de sesiones (regla de seguridad)
    Given tengo un token de tipo "child"
    When llamo a un endpoint de familia
    Then la respuesta es 401 (y a la inversa, un token "family" en un endpoint de niño también da 401)

  Scenario: Recuperar contraseña por código (sin email)
    Given olvidé mi contraseña y tengo mi código de recuperación XXXX-XXXX
    When lo introduzco junto a una nueva contraseña válida
    Then mi contraseña se restablece y puedo iniciar sesión
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Registro/login, token family, hash de contraseña | Pruebas de auth y de contraseñas | [AUTO] |
| PIN, alta y listado de exploradores | Pruebas de la API de niños | [AUTO] |
| Separación de sesiones family/child | Pruebas de seguridad y de dependencias de acceso | [AUTO] |
| Alta de familia / explorador (UI) | Pruebas de componente de las pantallas de alta y acceso | [AUTO] |
| Cambio y recuperación de contraseña (UI) | Pruebas de componente de cambio/recuperación de contraseña | [AUTO] |
| Recorrido completo en navegador | Recorrido manual (UAT) | [UAT] |

---

## US2 — Encender la chispa (curiosidad → lección)

*Como niño explorador, quiero escribir o dictar una pregunta (o elegir una sugerencia), para
recibir al instante una mini-lección sobre eso que me da curiosidad.*

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

  Scenario: La lección stub es determinista (modo demo)
    Given no hay proveedor de IA configurado
    When se genera una lección
    Then su subject está en {ciencia, matematicas, lenguaje, arte, cultura}
    And el quiz tiene exactamente 3 opciones con el índice correcto entre 0 y 2

  Scenario: El contenido que llega al niño está moderado (seguridad del bucle)
    Given un texto candidato generado por IA
    When pasa por la capa de moderación
    Then el contenido inapropiado se bloquea o se marca y solo contenido apto llega al niño
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Endpoint de lecciones y stub determinista | Pruebas de la API de lecciones y del generador | [AUTO] |
| Sugerencias de arranque | Pruebas de los endpoints `/me/*` | [AUTO] |
| Moderación del contenido del bucle | Pruebas de moderación | [AUTO] |
| Pantalla de encender la chispa | Pruebas de componente de la pantalla de la chispa | [AUTO] |
| Generación con proveedor real (lección real) | Validación manual con IA real | [UAT] |

---

## US3 — Mini-lección adaptada por edad + lectura en voz alta

*Como niño explorador, quiero que la lección esté escrita a mi medida y que me la puedan leer en
voz alta, para entenderla fácilmente aunque aún no lea bien.*

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

  Scenario: Navegador sin síntesis de voz (degradación)
    Given el navegador no soporta síntesis de voz
    Then el botón 🔊 (SpeakButton) no se muestra (renderiza null) y la lección sigue siendo usable
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Adaptación por banda de edad y estructura (analogía, dato, follow-ups) | Pruebas del generador de lecciones y de la API de lecciones | [AUTO] |
| Pantalla de lección | Pruebas de componente de la pantalla de lección | [AUTO] |
| Botón de lectura y degradación sin voz | Pruebas del componente de lectura de voz | [AUTO] |

---

## US4 — Reto (quiz) que sube la maestría

*Como niño explorador, quiero poner a prueba lo aprendido con un reto rápido, para afianzar el
concepto y ver crecer mi dominio de esa isla, sin castigo si me equivoco.*

```gherkin
Feature: Reto que sube la maestría

  Scenario: Respuesta correcta
    Given estoy resolviendo el reto de una lección
    When respondo correctamente (POST /lessons/{id}/answer)
    Then la respuesta indica correct=true y sube la maestría del KnowledgeNode asociado

  Scenario: Respuesta incorrecta (sin penalización)
    Given estoy resolviendo el reto de una lección
    When respondo de forma incorrecta
    Then la respuesta indica correct=false y no se penaliza mi maestría

  Scenario: El backend nunca revela la respuesta correcta (seguridad)
    Given recibo una lección con su reto
    When inspecciono la respuesta del backend
    Then no contiene el índice ni el texto de la opción correcta
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Evaluación de respuestas y maestría | Pruebas de la API de respuestas | [AUTO] |
| Secreto de la solución en el contrato | Pruebas de seguridad y de la API de lecciones | [AUTO] |
| Bloque de reto (UI) | Pruebas de componente de la pantalla de lección | [AUTO] |

---

## US5/US6 — Panel de familia (supervisión, ficha, seguridad)

*Como familia, quiero un panel donde ver la actividad y la ficha de conocimiento de cada niño,
para supervisar su aprendizaje y su seguridad.*

```gherkin
Feature: Panel de familia

  Scenario: Ver la ficha de conocimiento del niño
    Given estoy autenticado como familia con al menos un niño
    When consulto el perfil del niño (GET /me/profile)
    Then recibo sus datos (nombre, edad, islas) con conceptos fuertes y emergentes
    And nunca datos de otra familia

  Scenario: Consultar actividad e historial sobre /me/*
    Given un niño de mi familia
    When abro su panel
    Then veo su conocimiento (GET /me/knowledge) y sus sugerencias (GET /me/suggestions)

  Scenario: Acceso sin token (seguridad)
    Given no envío un token válido
    When consulto un endpoint /me/*
    Then la respuesta es 401
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Perfil (GET /me/profile: name/age/islands, fuertes/emergentes) | Pruebas del endpoint de perfil | [AUTO] |
| Conocimiento y sugerencias sobre /me/*, aislamiento y 401 | Pruebas de los endpoints `/me/*` | [AUTO] |
| Cabecera del niño en el panel (UI) | Pruebas de componente de la cabecera del niño | [AUTO] |

> Nota de diseño: los endpoints `/me/*` (knowledge, suggestions, profile) serán de **solo lectura**
> (GET). No se contempla un endpoint de actualización de perfil, por lo que no se documenta ningún
> criterio de "editar/persistir perfil".

---

## US7 — Archipiélago y buscador

*Como niño explorador, quiero ver todas mis islas en un mapa y poder buscarlas, para reencontrar
un tema y volver a explorarlo.*

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
    Then se abre su conversación guardada mediante su root_lesson_id
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Búsqueda insensible a acentos/mayúsculas + "sin resultados" (UI) | Pruebas de componente del archipiélago | [AUTO] |
| Enlace por `root_lesson_id` (backend) | Pruebas del vínculo `root_lesson_id` y de los endpoints `/me/*` | [AUTO] |

---

## US8 — Chat con contexto e islas automáticas

*Como niño explorador, quiero seguir preguntando en el mismo hilo y que cada tema se guarde solo
como una isla, para profundizar sin perder el contexto de mi conversación.*

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
    When repregunto sin responder ningún quiz correctamente
    Then mi maestría no cambia; solo el quiz respondido correctamente la sube
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Isla automática, hilo ordenado, contexto, repregunta no sube maestría | Pruebas de conversación | [AUTO] |
| Vínculo `root_lesson_id` | Pruebas del vínculo `root_lesson_id` | [AUTO] |
| Hilo/repregunta (UI) | Pruebas de componente de la lección y del archipiélago | [AUTO] |

---

## US9 — Biblioteca de cuentos con aprobación parental

*Como familia, quiero que los cuentos que crea mi hijo pasen por mi aprobación antes de que él
pueda leerlos; y como niño, quiero crear mis propios cuentos.*

```gherkin
Feature: Cuentos con aprobación parental

  Scenario: El niño crea un cuento (queda pendiente)
    Given estoy autenticado como niño
    When creo un cuento (POST /me/stories)
    Then queda en estado pending y no aparece en mi lista ni detalle (404) hasta ser aprobado

  Scenario: La familia aprueba y edita
    Given hay un cuento pendiente
    When la familia lo aprueba (PUT /family/stories/{id}, action=approve) editando título o cuerpo
    Then el cuento pasa a aprobado y el niño ya lo ve

  Scenario: La familia rechaza (conserva el original)
    Given hay un cuento pendiente
    When la familia lo rechaza (action=reject)
    Then el cuento queda en estado rejected y conserva su texto original

  Scenario: Aislamiento entre familias
    Given un cuento pertenece a otra familia
    When intento acceder a él
    Then la respuesta es 404
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Pending oculto, aprobar, rechazar conserva original, aislamiento 404 | Pruebas de la API de cuentos | [AUTO] |
| Modelo de cuento | Pruebas del modelo de cuento | [AUTO] |
| Biblioteca y cuentos de familia (UI) | Pruebas de componente de biblioteca y cuentos de familia | [AUTO] |

---

## US10 — IA multiproveedor por familia (texto + imagen)

*Como familia, quiero elegir y configurar el proveedor de IA (o quedarme en modo demo) con mi
propia clave guardada de forma segura, para controlar calidad, coste y privacidad.*

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

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Default free/stub, BYOK sin devolver clave, deshabilitado 422, recomendador | Pruebas de la API de configuración de IA | [AUTO] |
| CRUD, modelo y cifrado de clave | Pruebas de CRUD/modelo de config y de cifrado | [AUTO] |
| Catálogo, proveedores y wiring | Pruebas de catálogo, de proveedores y de wiring proveedor↔lección | [AUTO] |
| Panel de configuración (UI) | Pruebas de componente del panel y del cliente de configuración | [AUTO] |

---

## US11 — Voz, imágenes IA, QR/LAN e i18n

*Como niño y como familia, quiero dictar preguntas, ver imágenes cuando estén activas, conectar
el móvil por QR y usar la app en mi idioma, para que la experiencia sea accesible en cualquier
dispositivo.*

```gherkin
Feature: Voz, imágenes, QR/LAN e i18n

  Scenario: Dictar la pregunta por voz
    Given el navegador soporta la Web Speech API
    When pulso el micrófono 🎤 y hablo
    Then mi voz se transcribe en el idioma activo como texto de la curiosidad

  Scenario: Sin soporte de voz (degradación)
    Given el navegador no soporta reconocimiento de voz
    Then el botón de micrófono (MicButton) no se muestra (renderiza null)

  Scenario: Generar avatar con imagen desactivada
    Given la generación de imágenes está desactivada (por defecto)
    When intento generar un avatar por IA
    Then la respuesta es 409

  Scenario: Generación de imagen segura (anti-SSRF)
    Given una URL de imagen que apunta a un destino no permitido
    When el backend intenta procesarla
    Then la petición se rechaza por la validación anti-SSRF

  Scenario: Conectar el móvil por QR / LAN
    Given estoy en la pantalla "Conectar móvil"
    Then veo la URL basada en window.location.origin y su código QR

  Scenario: Idioma detectado y cambiable
    Given abro la app
    Then el idioma se detecta del navegador (es/en) y puedo cambiarlo manualmente
```

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| Avatar IA (409 si imagen off) | Pruebas de generación de avatar | [AUTO] |
| Matriz de proveedores + validación SSRF | Pruebas de imágenes (proveedores + anti-SSRF) | [AUTO] |
| Dictado por voz y degradación sin voz (UI) | Pruebas del componente de micrófono y de la pantalla de la chispa | [AUTO] |
| Conectar móvil por QR/LAN (UI) | Pruebas de componente de conectar dispositivo | [AUTO] |
| Detección y cambio de idioma | Pruebas del contexto i18n | [AUTO] |
| Imagen real de extremo a extremo | Validación manual con IA real | [UAT] |

---

## Escenarios transversales (plataforma y seguridad)

Reforzarán varias historias a la vez y se validarán automáticamente:

| Escenario | Se validará mediante (previsto) | Modo |
|---|---|---|
| CORS y health check | Pruebas de CORS y de health | [AUTO] |
| Configuración de la app | Pruebas de configuración | [AUTO] |
| Modelos de datos base | Pruebas de modelos y de la base de datos | [AUTO] |
| Sesión y rutas protegidas (UI) | Pruebas del contexto de sesión y de rutas protegidas | [AUTO] |
| Arranque de la app (UI) | Pruebas de arranque de la app y de la landing | [AUTO] |
| Cliente y núcleo de API (UI) | Pruebas del cliente HTTP y del núcleo de dominio | [AUTO] |

---

## Matriz de trazabilidad resumida

| Historia | Épica | Pantalla(s) | Endpoint(s) clave | Área de prueba prevista | Modo |
|---|---|---|---|---|---|
| US1 | E1 | CreateFamily, AddExplorer, ChildAccess, ResetPassword | `/auth/*`, `/children*` | Auth, niños, contraseñas | [AUTO]+[UAT] |
| US2 | E2 | Spark | `POST /lessons`, `/me/suggestions` | Lecciones, moderación, pantalla de la chispa | [AUTO]+[UAT] |
| US3 | E2 | LessonScreen, SpeakButton | `POST /lessons`, `/lessons/{id}/thread` | Generador de lecciones, componente de lectura | [AUTO] |
| US4 | E2 | LessonScreen | `POST /lessons/{id}/answer` | API de respuestas, seguridad | [AUTO] |
| US5/US6 | E6 | Panel de familia, ChildHeader | `/me/profile`, `/me/knowledge`, `/me/suggestions` | Endpoints `/me/*` (solo lectura) | [AUTO] |
| US7 | E3 | MyKnowledge | `GET /me/knowledge` | Vínculo `root_lesson_id`, archipiélago | [AUTO] |
| US8 | E3 | LessonScreen, MyKnowledge | `/lessons/{id}/ask`, `/thread` | Conversación | [AUTO] |
| US9 | E4 | StoryLibrary, FamilyStories | `/me/stories`, `/family/stories` | API de cuentos | [AUTO] |
| US10 | E5 | AIConfigPanel | `/family/ai-config*` | Configuración de IA, cifrado | [AUTO] |
| US11 | E6 | Spark, ConnectDevice, i18n | `/children/{id}/avatar/generate`, endpoints de imagen | Avatar, imágenes/SSRF, voz, i18n | [AUTO]+[UAT] |

---

## Resumen automático vs manual

- **Automático [AUTO]:** la mayoría de escenarios de US1–US11 y todos los transversales se
  validarán en CI (pytest + vitest) en cada push y PR. Los generadores de IA se cubrirán con
  mocks/monkeypatch, sin llamadas HTTP reales.
- **Manual / UAT [UAT]:** la validación con **IA real** (lección e imagen generadas por
  proveedores reales) y los **recorridos completos en navegador** (registro→acceso→chispa,
  aprobación de cuentos, conexión de móvil por QR) se verificarán manualmente y se registrarán en
  el diario de progreso.
