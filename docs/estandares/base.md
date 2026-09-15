# Estándares base — Chispa ✨

> **Fuente única de verdad** para cualquier agente de IA (Claude, Cursor, Codex, Gemini) y para
> cualquier persona que trabaje en este repositorio. Adaptado de `lidr-specboot`
> (`docs/base-standards.md`) al contexto real de Chispa.
>
> Los estándares específicos cuelgan de aquí:
> [backend](backend.md) · [frontend](frontend.md) · [documentación](documentacion.md) ·
> [verificación](verificacion.md)

---

## 1. Principios núcleo

- **Pasos pequeños, de uno en uno.** Nunca avanzar más de un paso. Si una tarea necesita tres
  ficheros nuevos y una migración, son varias tareas.
- **TDD.** Toda funcionalidad nueva empieza por un test que falla. Ver [verificación](verificacion.md);
  la regla la aplica `tdd-guard` con hooks, no la buena voluntad.
- **Tipado completo.** Python con anotaciones en toda firma pública; TypeScript en modo `strict`,
  sin `any` ni `@ts-ignore`.
- **Cambios incrementales.** Antes un diff de 60 líneas revisable que uno de 600.
- **Cuestionar los supuestos.** Si el brief dice algo que el código contradice, gana la realidad y
  se corrige el brief. La deriva entre documentación y código es un hallazgo de primera clase, no
  una nota al pie.
- **Detectar repetición.** Tres apariciones del mismo patrón piden una abstracción; dos, todavía no.

## 2. Idioma

**Chispa se escribe en español.** Esta regla invierte deliberadamente el *English Only* de
`lidr-specboot`, porque el proyecto es una entrega académica en español y sus usuarios finales son
familias hispanohablantes.

| Artefacto | Idioma |
|---|---|
| Documentación (`docs/`, `README`, ADRs, historias, requisitos) | Español |
| Comentarios de código | Español |
| Mensajes de commit | Español |
| Textos de interfaz | Español e inglés (catálogo i18n, ver [frontend](frontend.md)) |
| Mensajes de error de la API | Español |
| Identificadores de código (variables, funciones, clases, tablas, columnas) | **Inglés** |
| Nombres de tests | Inglés (`test_create_lesson_blocked_by_moderation`) |

El motivo de la frontera: el dominio se lee en español, pero el código habla el idioma de sus
librerías (FastAPI, SQLAlchemy, React). Mezclar `def crear_leccion(db: Session)` con
`Depends(get_current_child)` produce código peor que cualquiera de las dos opciones puras.

## 3. Seguridad del menor: reglas que no se negocian

Chispa la usan niños de 3 a 12 años. Estas cuatro reglas están por encima de cualquier otra
consideración de diseño, rendimiento o elegancia:

1. **El backend nunca envía la respuesta correcta del quiz.** Ni el índice ni la explicación salen
   en `LessonRead`. La corrección se calcula solo en servidor. Garantizado en tres capas
   independientes: el esquema `QuizPublic`, la serialización `to_read_dict` y la validación en
   `answer_lesson`.
2. **Toda entrada del niño pasa por moderación**, con *fallback* seguro: ante la duda, se bloquea
   con 422 y un mensaje amable orientado a la familia.
3. **Aislamiento estricto** por niño y por familia. Los accesos cruzados devuelven **404**, nunca
   403, para no confirmar que el recurso existe.
4. **El niño nunca ve un error técnico.** Si el proveedor de IA falla, se degrada al stub
   determinista. Un fallo de infraestructura no puede convertirse en una pantalla rota delante de
   un niño de cinco años.

Cualquier cambio que toque estas cuatro reglas exige revisión adversaria antes de fusionar
(ver [verificación](verificacion.md)).

## 4. Degradación elegante

Todo lo que dependa de un servicio externo o de una capacidad del navegador debe funcionar sin él:

| Capacidad | Sin ella |
|---|---|
| Proveedor de IA de texto | Stub determinista (modo demo, sin coste) |
| Proveedor de imagen | Sin imagen; la lección se lee igual |
| Síntesis de voz del navegador | El botón 🔊 no se muestra; el texto está en pantalla |
| Reconocimiento de voz | El micrófono no se muestra; se escribe |

La app entera debe ser plenamente usable sin configurar ni una sola clave.

## 5. Skills del proyecto

- Viven en `.claude/skills/`.
- Cuando una petición encaje con una skill, **cargarla y seguirla antes de continuar**.
- Cargar también los ficheros referenciados desde ella (`references/*.md`).

| Skill | Cuándo |
|---|---|
| `chispa-brief` | Antes de implementar: convierte una HU/RF en brief ejecutable |
| `chispa-verificar` | Después de implementar: cadena de verificación y evidencias |
| `chispa-revision-adversaria` | Antes de fusionar: revisión independiente que busca romper |
| `chispa-auditoria` | Barridos de deuda técnica y revisiones pre-entrega |
| `chispa-bitacora` | Registrar prompts, resultados y correcciones en la bitácora de IA |
| `chispa-commit` | Crear commits enfocados con la convención del proyecto |

## 6. Flujo de trabajo

Chispa usa un flujo SDD propio, rodado a lo largo de 56 briefs, con los artefactos en
`.superpowers/sdd/`:

```
brief  →  implementación (TDD)  →  report  →  verificación  →  revisión adversaria  →  commit
```

- `.superpowers/sdd/briefs/task-<id>-brief.md` — qué hay que construir y cómo se valida.
- `.superpowers/sdd/reports/task-<id>-report.md` — qué se construyó, con evidencias.
- `.superpowers/sdd/progress.md` — libro mayor: una línea por tarea, con commit y tests.

**Regla de oro heredada de OpenSpec:** si aparece un cambio de alcance a mitad de una tarea, se
actualiza **primero el brief** y después el código. La documentación es la fuente de verdad, no un
resumen que se escribe al final. No se aplican "arreglos rápidos" de solo código en esa ventana.

## 7. Trazabilidad

Todo cambio funcional debe poder seguirse en esta cadena, y ninguno de sus eslabones es opcional:

```
HU (US1–US11)  →  RF (requisitos.md)  →  endpoint / pantalla  →  test  →  evidencia
```

La matriz vive en [`docs/entrega-1/01-product/requisitos.md`](../entrega-1/01-product/requisitos.md),
Parte 3. Si un cambio añade capacidad, la matriz se actualiza en el mismo commit.

## 8. Qué NO hacer

- No commitear `.env` ni secretos. Nunca. (`.gitignore` los cubre; comprobarlo igualmente.)
- No añadir migraciones destructivas: solo operaciones aditivas en `upgrade()`; los `drop_*` viven
  exclusivamente en `downgrade()`.
- No serializar jamás `password_hash`, `pin_hash`, `family_id`, `api_key_encrypted` ni
  `quiz_correct_index`.
- No firmar commits con menciones a Claude ni *trailers* de co-autoría.
- No delegar en la persona usuaria la ejecución de tests o verificaciones que el agente puede
  ejecutar él mismo.
