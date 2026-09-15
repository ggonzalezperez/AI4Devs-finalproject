# Estándares de backend — Chispa ✨

> Cuelga de [estándares base](base.md). Stack real: **Python 3.12 · FastAPI · SQLAlchemy 2 ·
> Alembic · Pydantic v2 · pytest · ruff**. SQLite en desarrollo y tests, PostgreSQL 16 en Docker.

---

## 1. Arquitectura por capas

Cuatro capas, con una dirección de dependencia única. Nunca al revés.

```
routers/      HTTP: rutas, códigos de estado, dependencias de auth. Sin lógica de negocio.
   ↓
services/     Reglas de negocio, orquestación, moderación, fallback de IA. Sin SQL crudo.
   ↓
repositories/ Acceso a datos. Es el único sitio donde se consulta la sesión de SQLAlchemy.
   ↓
models/       Entidades SQLAlchemy. Solo estructura.

schemas/      Contratos Pydantic de entrada y salida. Transversal, no es una capa.
```

**Qué va en cada sitio**, con el ejemplo canónico del proyecto:

- `routers/lessons.py` — resuelve el token, llama al servicio, traduce excepciones a códigos HTTP.
  Un *router* que supera las 15 líneas por endpoint casi siempre está haciendo trabajo del servicio.
- `services/lesson_service.py` — modera la entrada, construye el generador según la configuración de
  la familia, aplica el *fallback* al stub, persiste y asegura la isla de conocimiento.
- `repositories/lesson.py` — `create`, `list_thread`, `get_for_child`. Nada más.
- `models/lesson.py` — columnas y relaciones.

**Prohibido:** que un *router* importe un repositorio saltándose el servicio, o que un servicio
construya consultas SQLAlchemy directamente.

## 2. Contratos y esquemas

- Entrada y salida **siempre** con esquemas Pydantic explícitos. Nunca devolver un modelo ORM.
- Un esquema de lectura no expone jamás: `password_hash`, `pin_hash`, `family_id`,
  `recovery_code_hash`, `api_key_encrypted`, `image_api_key_encrypted`, `quiz_correct_index`,
  `quiz_explanation`.
- Los campos derivados van como `@computed_field` sobre `@property`, no como columna. Ejemplo:
  `ChildRead.age` se calcula de `birthdate`; la edad no se almacena porque cambia sola.
- Validar en el borde: `Field(min_length=…, max_length=…)`, `EmailStr`, rangos. La validación en
  cliente es cortesía para la persona usuaria, **no** sustituye a la del servidor.

> **Deuda conocida.** `ChildCreate.pin` acepta hoy `min_length=4, max_length=8` sin comprobar que
> sean dígitos, mientras `RF-ONB-03` exige `^\d{4}$` y solo el frontend lo aplica. Es un ejemplo
> real de la deriva que la [revisión adversaria](verificacion.md) debe cazar.

## 3. Autenticación: JWT tipado

Dos tipos de sesión conviven en el mismo dispositivo y **no son intercambiables**:

| Token | Claim `type` | Dependencia | Alcance |
|---|---|---|---|
| Familia | `family` | `get_current_family_user` | `/children/*`, `/family/*`, `/auth/change-password` |
| Niño | `child` | `get_current_child` | `/lessons/*`, `/me/*` |

- Un token `child` en un endpoint de familia devuelve **401**, y al revés también.
- Un recurso de otra familia u otro niño devuelve **404**, nunca 403.
- La sesión del niño la abre siempre un adulto: `POST /children/{id}/login` exige token `family`.

## 4. Base de datos y migraciones

- **Migraciones aditivas.** En `upgrade()` solo `create_table`, `add_column`, `create_index`. Los
  `drop_*` viven exclusivamente en `downgrade()`.
- **Cadena lineal.** Un único HEAD. `down_revision` apunta siempre a la migración anterior.
- Toda migración debe aplicar sin errores en **SQLite y PostgreSQL**. El `docker-entrypoint.sh`
  ejecuta `alembic upgrade head` antes de arrancar uvicorn, así que una migración rota tumba el
  contenedor.
- Índice explícito en toda columna de aislamiento: `child_id`, `family_id`.
- `created_at` siempre con zona horaria (UTC-aware).

Verificación mínima de una migración nueva:

```bash
alembic upgrade head && alembic downgrade -1 && alembic upgrade head
```

## 5. Costuras de IA (*seams*)

Todo proveedor externo entra por una **costura**: un `Protocol` con una implementación stub
determinista por defecto.

```
LessonGenerator (Protocol)
├── StubLessonGenerator      ← determinista, sin red, sin coste. El defecto.
├── ClaudeLessonGenerator
└── OllamaLessonGenerator

ImageGenerator (Protocol)
├── HuggingFace / SDXL local / OpenAI / Gemini / Pollinations
└── (ninguno)                ← el defecto: imagen desactivada
```

Reglas:

- La fábrica (`build_generator`, `build_image_generator`) elige según la configuración **de la
  familia**, no global.
- Toda llamada al proveedor va envuelta: si lanza, se cae al stub. El niño nunca ve el error.
- El stub debe ser **reproducible**: mismo input, mismo output. Es lo que hace testeable el resto.
- El contrato pedagógico (materia acotada, quiz de exactamente 3 opciones, índice en 0..2) lo
  impone **el sistema**, no el prompt. Un modelo que devuelva 4 opciones es un fallo del sistema.
- Las claves se cifran con Fernet antes de persistir y nunca vuelven en una respuesta: el esquema
  solo expone `has_api_key` / `has_image_api_key`.

## 6. Tests

- `pytest`, con los *fixtures* de `tests/conftest.py`: SQLite en memoria con `StaticPool` y
  `dependency_overrides` para inyectar la sesión. Cada test arranca con esquema limpio.
- Un fichero de test por área funcional, con el nombre del módulo que prueba
  (`test_lessons_api.py`, `test_moderation.py`).
- Nombres de test en inglés y descriptivos del comportamiento, no de la implementación:
  `test_create_lesson_blocked_by_moderation`, no `test_create_lesson_2`.
- **Cobertura por riesgo, no por porcentaje.** Todo lo que toque las cuatro reglas de seguridad del
  menor ([base §3](base.md#3-seguridad-del-menor-reglas-que-no-se-negocian)) lleva test de caso
  negativo obligatorio: token cruzado, acceso ajeno, entrada bloqueada, fuga de la respuesta del quiz.
- Los tests no salen a la red. Los proveedores se prueban con dobles.

## 7. Estilo

- `ruff check .` limpio antes de cualquier commit. Sin excepciones ni `# noqa` sin justificación
  escrita al lado.
- Comentarios en español y solo donde expliquen **por qué**, no qué. El ejemplo bueno del
  repositorio: `# Fallback seguro: el niño nunca ve un fallo del proveedor.`
- Funciones privadas del módulo con prefijo `_`.
- Sin `print`. Sin código muerto. Sin ficheros "por si acaso".
