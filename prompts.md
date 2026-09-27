> Prompts principales utilizados durante la creación del proyecto **Chispa** ✨.
>
> ℹ️ **Contexto (Entrega 2 — código funcional).** La Entrega 1 fue documental y su *pipeline* de prompts
> (discovery → documentos) se conserva íntegro más abajo, porque sigue siendo la fase donde se decidió
> **qué** construir. Lo que añade esta entrega es cómo se usó la IA para **construirlo**.
>
> 🔑 **Lo que de verdad vale la pena leer está en
> [`docs/entrega-1/05-ai-log/decisiones.md`](docs/entrega-1/05-ai-log/decisiones.md): siete entradas
> AI-LOG con los errores del modelo que fueron detectados y corregidos.** Una bitácora donde la IA nunca
> se equivoca no demuestra que hubo validación; demuestra que no la hubo. Resumen en §0.
>
> 📚 **Playbook completo (fuente de estos prompts, con los 9 campos por prompt, esquemas por documento y
> checklists):** [`docs/entrega-1/05-ai-log/prompts.md`](docs/entrega-1/05-ai-log/prompts.md). Ahí están, sin
> resumir, todos los prompts (P-ANALISIS, P-MODELO, P-DOC + esquema por documento, validación y coherencia) y
> el **patrón de *brief* ejecutable** con el que se dirigirá la IA al **implementar** el código (Entregas 2–3).
>
> No se limita a 3 por sección: se incluyen los que realmente aplican a cada una. Las secciones de
> implementación (tickets, PRs) marcan honestamente que su prompt es de tipo *brief* y se ejecutará al escribir
> el código.

## 0. Cómo se usó la IA para escribir el código (Entrega 2)

El código no se pidió a golpe de prompt suelto. Se siguió un flujo **SDD** con artefactos versionados en
[`.superpowers/sdd/`](.superpowers/sdd/INDEX.md): **53 briefs** y **53 informes**, uno por tarea.

```
brief  →  implementación (TDD)  →  informe con evidencias  →  revisión adversaria  →  commit
```

Tres decisiones hacen que esto no sea una declaración de intenciones:

1. **El TDD lo aplica una herramienta, no la buena voluntad.** `tdd-guard` intercepta la escritura de
   ficheros y **bloquea** implementar sin un test que falle antes. Bloqueó al agente **tres veces**
   durante el desarrollo: al añadir tres tests de golpe, al extraer un helper sin test que lo exigiera y
   al crear un componente completo sin rojo previo. Los bloqueos se acataron.
2. **La revisión la hace un agente distinto del implementador**, con el mandato explícito de *intentar
   romper*, no de confirmar. Encontró un **bloqueante en el propio arreglo del día**: al pasar la
   moderación de subcadena a palabra completa se cerraron los falsos positivos («armadura», «armario»)
   pero se abrieron falsos negativos («matarte», «drogadicto»). Se corrigió con dos listas y se verificó
   en ambas direcciones.
3. **Cada verificación la ejecuta el agente**, nunca se delega en la persona: tests dirigidos, suite
   completa, linters, migración reversible, `curl` real contra la API y recorrido E2E en navegador con
   capturas. Las evidencias de la entrega son el subproducto de ese flujo, no una tarea final.

### Los prompts que más rindieron

Están en `.claude/skills/` como **skills propias**, adaptadas de `lidr-specboot` y `nizos/tdd-guard`:

| Skill | Para qué |
|---|---|
| `chispa-brief` | Convertir una HU/RF en brief ejecutable con alcance cerrado |
| `chispa-verificar` | La cadena de verificación obligatoria, con su plantilla de informe |
| `chispa-revision-adversaria` | Revisión hostil con lista específica de seguridad del menor |
| `chispa-auditoria` | Contrastar documentación contra código |
| `chispa-bitacora` | Registrar prompt, resultado real y corrección |
| `chispa-commit` | Commits enfocados, con la convención del proyecto |

### Lo que salió mal, que es lo que se aprende

- **Identificadores de modelo caducados.** El catálogo ofrecía la serie Imagen de Google, apagada el
  17-08-2026. Un id caducado **no da error visible**: la llamada falla, el `except` la absorbe y el niño
  recibe una lección del generador de demo mientras la familia cree estar pagando IA. Se verificaron
  todos contra la documentación de cada proveedor —no de memoria— y se añadieron tests centinela.
- **Una auditoría tiene puntos ciegos.** El barrido automático contrastaba *requisitos contra código*, así
  que no vio que `monthly_quota` se incrementa pero nunca se comprueba: ningún requisito lo reclamaba.
  Apareció leyendo un documento de diseño escrito en otra sesión.
- **Una corrección amplia toca más de lo que crees.** Al arreglar el encadenado de excepciones, una
  expresión regular añadió `from None` a 16 `raise` en lugar de a los 5 que estaban dentro de un
  `except`. Se detectó **contando** lo aplicado frente a lo esperado, no confiando en que el linter
  quedara verde.

---

## 0.bis Entrega 3 — publicar, endurecer y cazar fallos silenciosos

El flujo no cambió: **brief → implementación con TDD → verificación con evidencias → revisión →
commit**. Lo que cambió fue el tipo de problema. Con la aplicación en internet aparecieron fallos que
**no se reproducen en local**, y una categoría concreta acaparó el trabajo: el **fallo silencioso**.

> Un fallo silencioso es el que no produce ningún error visible. La familia configura un proveedor de
> IA, la aplicación responde `200`, y el niño recibe contenido del generador de demo mientras el adulto
> cree estar pagando por IA. No hay traza, no hay alerta, no hay nada que mirar.

Se cerraron cuatro del mismo patrón en una jornada: un proveedor de imagen inválido que se guardaba
con `200` en lugar de `422`, un panel que no avisaba de una configuración inservible, un adaptador que
reventaba con `KeyError` ante una respuesta inesperada, y un cliente HTTP que **destruía el motivo
real** de los errores al llamar a `JSON.parse` antes de comprobar el código de estado.

### Los tres prompts que sostuvieron esta fase

| Prompt / skill | Qué produjo |
|---|---|
| `chispa-brief` sobre la lista de deuda pendiente | [`task-e3-cierre-brief.md`](.superpowers/sdd/briefs/task-e3-cierre-brief.md): alcance cerrado, **lo que NO entra** con su motivo, tabla de validación con el nombre de cada test y los riesgos con su mitigación |
| `superpowers:systematic-debugging` ante un alta fallida en la demo | Prohibió proponer arreglos antes de tener causa raíz. Llevó a leer el cliente HTTP y encontrar que el error real nunca llegaba a la pantalla |
| `chispa-verificar` | [`task-e3-cierre-report.md`](.superpowers/sdd/reports/task-e3-cierre-report.md): suites con números reales, migraciones, cuatro casos de `curl` contra el servidor y E2E en Chrome real, escritorio y móvil |

### Lo que salió mal en esta fase

Cuatro errores, y ninguno lo detectó el modelo por sí solo: los detectó **verificar contra una fuente
externa** en lugar de confiar en lo escrito.

- **Una anotación del propio libro mayor era falsa, y seguirla habría roto código que funcionaba.**
  Arrastraba desde semanas atrás un *«falta `response_format=b64_json`»* en el adaptador de OpenAI. Al
  contrastarlo con la documentación del proveedor resultó ser **al revés**: ese parámetro existe solo
  para `dall-e-2` y `dall-e-3`, mientras que la familia `gpt-image-*` —la única del catálogo— lo
  **rechaza** y ya devuelve *base64* de serie. Añadirlo habría convertido un adaptador operativo en un
  `400` que el *best-effort* se habría tragado en silencio. Se cerró **al contrario de como estaba
  escrito**, con un test centinela que se pone rojo si alguien vuelve a intentarlo, y se corrigió la
  anotación: dejarla induciría el error otra vez.
  **Lección: una tarea pendiente escrita por una sesión anterior no es evidencia, es una hipótesis.**
- **La documentación afirmaba un mecanismo de acceso que no existía.** El documento de despliegue decía
  que la demo usaba *One-time PIN* «sin proveedor de identidad». Era falso: el único método activo
  exigía **cuenta propia de Cloudflare**, así que un revisor externo no habría podido entrar jamás,
  tuviera su correo autorizado o no. Solo se ve probando **en una ventana de incógnito**: con la sesión
  del propietario abierta, todo parece funcionar.
- **Una hipótesis plausible y falsa, descartada antes de tocar producción.** Se sospechó que un ajuste
  de caché del CDN estaba anulando la cabecera `no-store` del servidor. En lugar de cambiar la
  configuración por si acaso, se **midieron las cabeceras reales**: llegaban intactas. No se tocó nada.
- **El ejemplo de una skill propia estaba caducado.** `chispa-verificar` proponía dar de alta
  `demo@chispa.test`, y el validador de correo rechaza `.test` por ser un dominio reservado: quien
  siguiera la skill al pie de la letra se atascaba con un `422` en lugar de obtener un token.

---

## Pipeline de prompts (común a todas las secciones)

Todos los documentos se generan con la misma cadena. Estos dos prompts **preceden** a los de cada sección:

**P-ANALISIS — Analizar la conversación de discovery** (así se guió al asistente: *"no interpretes ni mejores
el producto; refleja lo dicho y marca ambigüedades"*).

```text
Eres analista de producto y arquitecto de software. Vas a leer la transcripción íntegra de una
conversación de discovery y producir un ACTA NORMALIZADA que servirá para redactar la documentación
de diseño (producto + técnico) de un proyecto, ANTES de escribir código.

CONTEXTO DEL PROYECTO: {{CONTEXTO_PROYECTO}}
TRANSCRIPCIÓN DEL DISCOVERY: {{DISCOVERY_COMPLETO}}

TAREA. Extrae y organiza SOLO lo que aparece en la transcripción (no inventes). Devuelve un acta con
estas secciones, cada afirmación con una cita textual breve: 1) PROBLEMA Y CONTEXTO; 2) USUARIOS Y
ACTORES; 3) PROPUESTA DE VALOR Y PRINCIPIOS; 4) ALCANCE (MVP/límite/fuera); 5) FUNCIONALIDAD (por
épica); 6) MODELO DE DATOS (entidades, campos, relaciones, estados); 7) DISEÑO TÉCNICO (stack, capas,
integraciones, seams/fallback); 8) SEGURIDAD Y PRIVACIDAD; 9) IA EN EL PRODUCTO; 10) DESPLIEGUE;
11) PRUEBAS Y CALIDAD; 12) IA EN EL PROCESO; 13) DECISIONES TOMADAS vs ABIERTAS; 14) TERMINOLOGÍA.
REGLAS: no interpretes; anota AMBIGÜEDADES; conserva números, nombres de entidades y tecnologías tal
cual; idioma español.
```

**P-MODELO — Modelo estructurado del discovery** → produce `{{INFORMACION_ESTRUCTURADA}}` (YAML), la **única
fuente de verdad** para redactar cada documento. Guía: *"rellena solo con datos del acta; para cualquier hueco
usa `null` y añádelo a `_faltantes`; no inventes"*. (Esquema YAML completo en el playbook §4.)

Cada sección siguiente usa la **plantilla base P-DOC** inyectándole el **esquema de apartados** del documento
correspondiente:

```text
Eres redactor técnico. Redacta el documento "{{ID_DOCUMENTO}}" de la Entrega 1 (documental, PREVIA a la
implementación) usando EXCLUSIVAMENTE los datos del MODELO ESTRUCTURADO. No inventes; para huecos usa el
marcador ⟦FALTA: … · pregunta: …⟧ y sigue con el resto.

CONTEXTO DEL PROYECTO: {{CONTEXTO_PROYECTO}}
MODELO ESTRUCTURADO (fuente de verdad): {{INFORMACION_ESTRUCTURADA}} {{RESPUESTAS_ADICIONALES}}
ESQUEMA OBLIGATORIO DEL DOCUMENTO (respeta TODOS los apartados, en orden; no agrupes ni elimines
ninguno; usa las cabeceras de tabla y los tipos de diagrama indicados): {{ESQUEMA_APARTADO}}

REGLAS DE FORMATO: H1 exacto + blockquote de metadatos; secciones numeradas; voz futura/propuesta
(prohibido "as-built"); tablas con cabeceras exactas; Mermaid solo donde el esquema lo pide; español;
enlaces relativos; IDs conforme a la gramática (US/E/RF/RNF/O/OPT/ADR). SALIDA: solo el Markdown del documento.
```

## Índice

1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Modelo de datos](#3-modelo-de-datos)
4. [Especificación de la API](#4-especificación-de-la-api)
5. [Historias de usuario](#5-historias-de-usuario)
6. [Tickets de trabajo](#6-tickets-de-trabajo)
7. [Pull requests](#7-pull-requests)

---

## 1. Descripción general del producto

*Documentos generados: `problema-y-usuarios.md`, `prd.md`, `alcance.md`. Prompts P-PROB, P-PRD, P-ALC (P-DOC +
esquema). Cómo se guió: fijar la voz de producto (curiosidad primero; líneas rojas de "lo que NO debe ser"),
mantener los 8 principios no negociables y no inflar el PRD con el detalle tabular (que vive en `requisitos.md`).*

**Prompt (P-PROB · esquema de `problema-y-usuarios.md`):**

```text
[P-DOC con ID_DOCUMENTO = problema-y-usuarios]
ESQUEMA:
# Chispa ✨ — Entrega 1 · Producto   (H1 + blockquote + "> Documentos relacionados")
## 1. Resumen ejecutivo
## 2. El problema  ### Impacto del problema (tabla: Consecuencia | Descripción)  ### Por qué ahora
## 3. Propuesta de valor (blockquote) ### Concepto ### Línea roja ### Metáfora "Archipiélago"
## 4. Usuarios y actores ### 4.1 Familia/Adulto ### 4.2 Explorador/Niño ### 4.3 Operador/Autoalojador
   ### 4.4 Usuario futuro (docente) ### 4.5 Mapa de vocabulario (tabla: Término | Concepto técnico)
## 5. Escenarios de uso  ## 6. Objetivos (tabla # | Objetivo | Cómo se materializa; O1–O4)
## 7. Degradación elegante  ## 8. Norte del proyecto (blockquote)
Validación: O1–On con "cómo se materializa"; línea roja y norte citados del modelo.
```

**Prompt (P-PRD · esquema de `prd.md`):**

```text
[P-DOC con ID_DOCUMENTO = prd]
ESQUEMA:
## 1. Visión (2 blockquotes) ### 1.1 Tres mundos (tabla: Mundo | Qué aporta | Riesgo | Cómo lo resuelve)
### 1.2 Principios no negociables (lista 1–8) ### 1.3 Motor pedagógico ### 1.4 Ficha de Conocimiento
## 2. Actores y sesiones (tabla: Actor | Autenticación | Token JWT | Puede)
## 3. Épicas (tabla: Épica | Historias | Descripción; E1–E6)
## 4. RF (RESUMEN por módulo + enlace a requisitos.md)  ## 5. RNF (RESUMEN RNF-01–10 + enlace)
## 6. Experiencia visual  ## 7. Supuestos  ## 8. Métricas (cualitativas)  ## 9. Fuera de alcance
Validación: §4/§5 son resúmenes con enlace (no duplican el detalle de requisitos.md).
```

**Prompt (P-ALC · esquema de `alcance.md`):**

```text
[P-DOC con ID_DOCUMENTO = alcance]
ESQUEMA:
## 1. Objetivo ## 2. Dentro de alcance (una subsección 2.1–2.6 por épica E1–E6)
## 3. En el límite (tabla: Elemento | Condición) ## 4. Fuera de alcance (tabla: Elemento | Motivo/estado)
## 5. Priorización y recortes (opcionales OPT-01/OPT-02, no bloqueantes)
## 6. Riesgos y supuestos (tabla: Riesgo | Impacto | Mitigación) ## 7. Criterios de "terminado"
```

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

*Documento generado: `arquitectura.md` (prompt P-ARQ). Guía: 5 diagramas Mermaid del tipo indicado, seams
puerto/adaptador con fallback al stub, y la secuencia de "encender la chispa" con moderación + fallback.*

```text
[P-DOC con ID_DOCUMENTO = arquitectura]
ESQUEMA:
# Arquitectura propuesta — Chispa (blockquote banner)
## 1. Visión general (mermaid flowchart LR)  ## 2. Contexto C4 nivel 1 (mermaid flowchart TB con subgraph)
## 3. Componentes: capas + dos seams (mermaid flowchart TB con subgraphs anidados)
   ### 3.1 Seam de texto — LessonGenerator ### 3.2 Seam de imagen — ImageGenerator ### 3.3 Catálogo IA
## 4. Frontend (SPA)
## 5. Secuencia "Encender la chispa" (mermaid sequenceDiagram con alt/else/Note: moderación + fallback)
## 6. Secuencia "Guardar config de IA (BYOK)" (mermaid sequenceDiagram con alt/else)
## 7. Persistencia y despliegue  ## 8. Registro de decisiones (tabla ADR | Decisión, enlaces a los 7 ADR)
Validación: puerto/adaptador/fábrica/fallback en 3.1 y 3.2; §8 enlaza los 7 ADR.
```

### **2.2. Descripción de componentes principales:**

*Se genera con la misma pasada P-ARQ (apartados §3–§4 del esquema anterior): capas backend routers/services/
repositories/models, los dos seams de IA y la SPA. Para regenerar un único apartado se usa el prompt de
apartado suelto del playbook (§8):*

```text
Regenera EXCLUSIVAMENTE el apartado "{{APARTADO}}" del documento {{DOCUMENTO_REFERENCIA}}, respetando su
{{ESQUEMA_APARTADO}} (subtítulos, columnas de tabla y tipo de diagrama). Usa solo datos de
{{INFORMACION_ESTRUCTURADA}}; voz pre-implementación; no toques el resto del documento.
```

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

*Cubierto por P-ARQ (§3–§4) y por `decisiones-tecnologicas.md` (prompt P-TEC), que justifica el stack y la
estructura por capas + puerto/adaptador.*

```text
[P-DOC con ID_DOCUMENTO = decisiones-tecnologicas]
Objetivo: stack y justificación (backend FastAPI/SQLAlchemy/Alembic; frontend React+TS+Vite; datos
Postgres/SQLite; IA httpx sin SDKs). Tabla por decisión: Tecnología | Versión | Por qué. Voz futura.
```

### **2.4. Infraestructura y despliegue**

*Documento generado: `despliegue.md` (prompt P-DESP). Guía: topología Docker Compose (4 servicios), diagrama
Mermaid, tabla de variables de entorno con "obligatoria fuera de dev", y CI sin CD (self-hosted).*

```text
[P-DOC con ID_DOCUMENTO = despliegue]
ESQUEMA:
## 1. Topología (mermaid flowchart TB: frontend/backend/postgres/ollama; Ollama en 127.0.0.1) + mapa de puertos
## 2. Variables de entorno (tabla: Variable | Por defecto | Propósito | ¿Obligatoria fuera de dev?)
## 3. Modelos de despliegue (autoalojado Docker / dev sin Docker / LAN+QR)  ## 4. Datos y migraciones (Alembic aditivas)
## 5. Niveles de IA (stub / Ollama local / BYOK Claude; imagen)  ## 6. Hardening  ## 7. CI/CD (jobs backend/frontend; sin CD)
Bloques ```bash solo donde el esquema lo pide (generación de clave Fernet, comandos locales).
```

### **2.5. Seguridad**

*Documento generado: `seguridad.md` (prompt P-SEG). Guía: modelo de amenazas centrado en el menor; un control
por categoría OWASP con el componente de diseño concreto; matriz amenaza→control→componente; riesgos residuales
honestos.*

```text
[P-DOC con ID_DOCUMENTO = seguridad]
ESQUEMA:
# Seguridad (perspectiva OWASP) — Chispa (metadatos en negrita, separadores ---)
## 1. Modelo de amenazas ### 1.1 Activos (tabla) ### 1.2 Actores (tabla) ### 1.3 Superficies
## 2. Controles OWASP: A01 (JWT tipado + aislamiento 404) · A02 (Fernet + bcrypt) · A03 (ORM + Pydantic)
   · A04 (moderación + secreto del quiz) · A05 (fail-closed) · A07 (anti-enumeración) · A10 (SSRF)
## 3. Privacidad del menor (tabla: Principio | Cómo se aplicará)
## 4. Matriz Amenaza→Control→Componente  ## 5. Riesgos residuales  ## 6. Conclusión
Validación: cada control nombra su función/componente; riesgos residuales declarados con honestidad.
```

### **2.6. Tests**

*Documento generado: `estrategia-pruebas.md` (prompt P-EST). Guía: TDD dirigido por specs (SDD), pirámide de
pruebas (diagrama `graph TD`), cobertura por riesgo y degradación como categoría destacada; los generadores de
IA se prueban siempre con mocks.*

```text
[P-DOC con ID_DOCUMENTO = estrategia-pruebas]
ESQUEMA:
## 1. Filosofía (1.1 TDD/SDD · 1.2 Pruebas por riesgo: tabla Riesgo | Por qué | Dónde)
## 2. Pirámide (mermaid graph TD: Unitarias→Integración→E2E)  ## 3. Tipos de prueba (tabla)
## 4. Áreas cubiertas (4.1 backend pytest · 4.2 frontend Vitest)  ## 5. Degradación (tabla escenario|comportamiento|prueba)
## 6. Validación con IA real  ## 7. CI/CD (jobs; ```bash comandos locales)  ## 8. Riesgos de cobertura
```

---

## 3. Modelo de Datos

*Documento generado: `modelo-datos.md` (prompt P-DATOS). Guía: exactamente **7 entidades** (sin introducir
tablas de otra visión), diagrama `erDiagram` con cardinalidades, detalle campo a campo (tabla de 5 columnas) y
11 migraciones aditivas y lineales; `parent_id`/`root_id`/`root_lesson_id` como enteros **lógicos** sin FK.*

```text
[P-DOC con ID_DOCUMENTO = modelo-datos]
ESQUEMA:
# Modelo de datos propuesto — Chispa (blockquote banner)
## 1. Visión general (decisiones de diseño en viñetas: sin enums nativos; UTC-aware; enlaces lógicos; Fernet)
## 2. Diagrama ER (mermaid erDiagram con las 7 entidades: Family, User, Child, Lesson, KnowledgeNode, Story,
   FamilyAIConfig; cardinalidades ||--o{, ||--||, ||..o{) + tabla Relación | Cardinalidad | Implementación
## 3. Detalle campo a campo (3.1 families … 3.7 family_ai_config; tabla: Campo | Tipo SQLAlchemy | Nulo | Por defecto | Notas)
## 4. Estrategia de migración Alembic (tabla # | Paso | Cambio principal; 11 filas aditivas y lineales)
Validación: 7 entidades en ER y en §3.x; sin FK donde el modelo dice lógicas; migraciones no destructivas.
```

---

## 4. Especificación de la API

*Documento generado: `contratos-api.md` (prompt P-API). Guía: una tabla de endpoints por prefijo con 6 columnas
y marcadores de auth `[FAMILIA]`/`[NIÑO]`/`(sin auth)`; la regla estrella "el quiz nunca filtra la respuesta"
en 3 capas con bloques `python`; esquemas clave que nunca exponen secretos.*

```text
[P-DOC con ID_DOCUMENTO = contratos-api]
ESQUEMA:
# Contratos de la API a implementar — Chispa (blockquote banner, cita /docs)
## 1. Convenciones (auth Bearer; claim type family/child; errores {detail}; /health)
## 2. /auth  ## 3. /children  ## 4. /lessons  ## 5. /me  ## 6. Historias  ## 7. /family/ai-config
   (cada uno: tabla Método | Ruta | Auth | Request | Response | Códigos)
## 8. Patrón estrella: el quiz nunca filtra la respuesta (3 bloques ```python: QuizPublic, to_read_dict, answer_lesson)
## 9. Esquemas clave (ChildRead, LessonRead, AIConfigRead, AIConfigUpdate, Token/RegisterResult)  ## 10. Referencia interactiva (/docs)
Validación: tablas con las 6 columnas; ningún endpoint expone quiz_correct_index/explanation.
```

---

## 5. Historias de Usuario

*Documento generado: `historias-usuario.md` (prompt P-HU) y `casos-aceptacion.md` (P-CASOS). Guía: las 11
historias con la **plantilla DoR de 6 bloques**, Gherkin en el Bloque 4 (incluyendo escenarios de error),
numeración no contigua correcta (US1–4, US7–10, US5/US6, US11) y stakeholders como **roles** (no personas).*

```text
[P-DOC con ID_DOCUMENTO = historias-usuario]
ESQUEMA (por cada US, 6 bloques):
> blockquote "Como <rol> quiero <capacidad> para <beneficio>"  + **Épica** · **Prioridad** + tag [Modulo]
#### Bloque 1 — Contexto (beneficiario, solicitante, validador UAT como ROLES; Principios; RF relacionados)
#### Bloque 2 — Alcance (dentro / fuera / MVP)
#### Bloque 3 — Funcional (reglas de negocio; tabla Datos: Campo/entidad | Origen | Sistema maestro | Notas; casos feliz/borde/error)
#### Bloque 4 — Validación (```gherkin Feature + Scenarios Given/When/Then, incluye errores)
#### Bloque 5 — Operativa (Dependencias FE/BE/Data/UX; prioridad justificada)
#### Bloque 6 — Trazabilidad IA (SDD, brief, modelo Claude, revisor PO)
+ Índice de épicas (tabla con anclas) y Matriz de realización (Historia | Épica | Pantalla | Endpoint | Prueba).
Validación: 6 bloques por US; Gherkin con escenarios de error; roles, no personas físicas.
```

*Requisitos y trazabilidad (`requisitos.md`, prompt P-REQ): cada RF/RNF es una tabla de 2 columnas de etiqueta
fija; GWT **inline** (no fenced); matriz HU→RF sin huérfanos y RF→prueba funcional.*

---

## 6. Tickets de Trabajo

> **Fase de implementación (Entregas 2–3).** En Chispa el "prompt" de cada ticket **no será texto libre**: será
> un ***brief* ejecutable** (spec tan detallada que un subagente la ejecuta sin ambigüedad), con **TDD** (el
> test se escribe **antes** que el código). Aún no se han ejecutado; la anatomía de 7 partes y la plantilla
> ilustrativa están en [`docs/entrega-1/05-ai-log/prompts.md`](docs/entrega-1/05-ai-log/prompts.md) §2.4.

**Patrón de *brief* por ticket (previsto):**

```text
Encabezado (reglas duras): "Usa el código EXACTO. TDD. Backend backend/, venv ./.venv/Scripts/python.exe.
Rama feature-<bloque>. SIN deps nuevas. SIN push."
Files: qué crear / modificar con ruta completa.
Step 1 — Test primero: el/los test(s) escritos ANTES de implementar.
Step 2 — Ver fallar (red): comando pytest que debe fallar.
Step 3 — Código exacto: la implementación literal.
Step 4 — Ver pasar (green): el mismo comando, ahora en verde.
Steps 5–7: tests/código de las piezas de soporte + commit local (mensaje exacto, sin git push).
```

*Ejemplo ilustrativo (núcleo del generador de lecciones):* test `test_stub_is_deterministic_and_well_formed`
(el stub genera el mismo `subject` para el mismo input, quiz de **exactamente 3 opciones**,
`0 ≤ quiz_correct_index < 3`) → ver fallar → definir `GeneratedLesson`, el `Protocol` `LessonGenerator` y
`StubLessonGenerator` como costura hacia un LLM real → ver pasar → commit
`feat(backend): LessonGenerator interface + deterministic stub + moderation stub`.

---

## 7. Pull Requests

> **Fase de implementación (Entregas 2–3).** Cada PR se cerrará con **revisión de código en dos capas** (un
> agente distinto del implementador): conformidad con el *brief* + calidad. Skills "superpowers" empleadas en
> el ciclo: `requesting-code-review`, `receiving-code-review`, `verification-before-completion`,
> `finishing-a-development-branch`.

**Prompt de revisión de PR (previsto):**

```text
Revisa este PR en dos capas y NO lo apruebes si falla alguna:
1) Conformidad con el brief: ¿se crearon/modificaron exactamente los archivos indicados? ¿los tests del brief
   están y pasan? ¿se respetó "sin deps nuevas / sin push"?
2) Calidad: correctitud, seguridad (¿se filtra algún secreto o la respuesta del quiz?), aislamiento por
   propietario (404), degradación (fallback al stub), estilo (ruff / tsc). Devuelve hallazgos priorizados
   (bloqueante/alto/medio) con archivo:línea y una propuesta de corrección por cada uno.
```

> El resultado de cada brief/revisión (tests que pasan, commit, hallazgos y correcciones) se registrará en la
> bitácora [`docs/entrega-1/05-ai-log/decisiones.md`](docs/entrega-1/05-ai-log/decisiones.md).
