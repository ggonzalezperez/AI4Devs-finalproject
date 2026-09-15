# Estado de implementación — Entrega 2 · Chispa ✨

> **Alumno:** Germán González Pérez · **Máster:** LIDR – AI4Devs
> **Fecha:** 14 de septiembre de 2026 · **Rama:** `entrega_2`
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
| Tests backend | 0 | **143** (32 ficheros) |
| Tests frontend | 0 | **60** (31 ficheros) |
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


## 4. Deuda conocida

Se declara en lugar de ocultarse.

| Asunto | Estado | Decisión |
|---|---|---|
| `monthly_quota` nunca se comprueba | `used_count` se incrementa pero el límite no actúa: el contador existe, la cuota no | Se aborda en la Entrega 3, donde la cuota es necesaria de verdad (ver [diseño de demo pública](../superpowers/specs/2026-09-14-despliegue-demo-publica-design.md)) |
| Tier `managed` sin implementar | El modelo lo contempla; no hay claves a nivel de servidor | Entrega 3 |
| Migración a `httpx2` | 1 aviso de deprecación en la suite | No se toca a dos días de la entrega: `httpx` lo usan los proveedores de IA |
| Moderación como *blocklist* | Es un marcador de posición declarado, no un servicio real | Suficiente para el MVP; la costura permite sustituirlo |
| El PIN acepta dígitos Unicode (`١٢٣٤`) | `\d` de Python es Unicode-aware | Sin impacto: el formulario solo produce `[0-9]` y el PIN se hashea igual |
| Sin despliegue público | La app corre en local y LAN | Entrega 3 |
| El panel no avisa si hay proveedor de imagen configurado pero desactivado | Se puede guardar proveedor y clave con `image_enabled=false` y no ocurre nada, sin señal | Detectado el 15-09; mismo patrón de fallo silencioso. Pendiente |
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
