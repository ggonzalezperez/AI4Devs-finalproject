# Contratos de la API a implementar — Chispa

> Entrega 1 · Diseño técnico (previo a la implementación) · Máster LIDR–AI4Devs
> Contratos previstos de los endpoints (routers) y esquemas (Pydantic) que se implementarán.
> **Documentación viva:** la API generará documentación OpenAPI automática (Swagger) mediante FastAPI, disponible en **`/docs`** (interactivo). Este documento es el resumen de diseño curado; una vez implementada, `/docs` será la referencia interactiva definitiva.

## 1. Convenciones generales

- **Autenticación:** JWT vía cabecera `Authorization: Bearer <token>`. Los endpoints públicos se indican como *(sin auth)*.
- **Roles / distinción de token:** el JWT incluirá un claim `type` que distinguirá entre token de **familia** (`[FAMILIA]`) y token de **niño** (`[NIÑO]`). Cada endpoint exigirá el tipo correspondiente.
- **Errores:** se devolverán con el `status code` HTTP y un cuerpo `{"detail": "..."}` estándar de FastAPI.
- **Ficheros estáticos:** las imágenes generadas se servirán bajo `/media`.
- **Salud:** `GET /health` → `{"status": "ok"}` *(sin auth)*.

Leyenda de columna **Auth**: *(sin auth)* = público · `[FAMILIA]` = token de familia · `[NIÑO]` = token de niño.

## 2. Autenticación — prefijo `/auth`

Router `auth` · esquemas `auth`

| Método | Ruta | Auth | Request | Response | Códigos |
| --- | --- | --- | --- | --- | --- |
| POST | `/auth/register` | *(sin auth)* | `RegisterRequest` `{name, email:EmailStr, password}` | `RegisterResult` `{access_token, token_type, recovery_code}` | `201` · `409` email duplicado |
| POST | `/auth/login` | *(sin auth)* | `LoginRequest` `{email:EmailStr, password}` | `Token` `{access_token, token_type}` | `200` · `401` |
| POST | `/auth/change-password` | `[FAMILIA]` | `ChangePasswordRequest` `{current_password, new_password:min8}` | `{"status": "ok"}` | `200` · `400` contraseña actual incorrecta |
| POST | `/auth/reset-password` | *(sin auth)* | `ResetPasswordRequest` `{email:EmailStr, recovery_code, new_password:min8}` | `RecoveryResult` `{recovery_code}` (nuevo) | `200` · `400` |

Notas:

- El registro devolverá directamente un `access_token` (autologin) y un **código de recuperación** de un solo uso que sustituirá al email para recuperar la cuenta.
- `reset-password` consumirá el `recovery_code` anterior y **emitirá uno nuevo** en la respuesta.

## 3. Niños — prefijo `/children`

Router `children` · esquemas `child`

| Método | Ruta | Auth | Request | Response | Códigos |
| --- | --- | --- | --- | --- | --- |
| POST | `/children` | `[FAMILIA]` | `ChildCreate` `{name, birthdate, pin:4-8, avatar="fox"}` | `ChildRead` | `201` |
| GET | `/children` | `[FAMILIA]` | — | `list[ChildRead]` | `200` |
| POST | `/children/{id}/login` | `[FAMILIA]` | `ChildPinLogin` `{pin}` | `Token` (type=child) | `200` · `401` |
| POST | `/children/{id}/avatar/generate` | `[FAMILIA]` | `AvatarGenerate` `{description:2-120}` | `ChildRead` | `200` · `404` · `409` imágenes desactivadas |

El login del niño lo iniciará la familia (que ya está autenticada) introduciendo el PIN; devolverá un token de niño con `type=child`.

## 4. Lecciones — prefijo `/lessons`

Router `lessons` · esquemas `lesson`

| Método | Ruta | Auth | Request | Response | Códigos |
| --- | --- | --- | --- | --- | --- |
| POST | `/lessons` | `[NIÑO]` | `LessonCreate` `{curiosity:2-300, subject?}` | `LessonRead` | `201` · `422` moderación bloqueada |
| GET | `/lessons/{id}` | `[NIÑO]` | — | `LessonRead` | `200` · `404` |
| POST | `/lessons/{id}/ask` | `[NIÑO]` | `LessonCreate` `{curiosity:2-300, subject?}` | `LessonRead` (nuevo turno) | `201` · `404` · `422` |
| GET | `/lessons/{id}/thread` | `[NIÑO]` | — | `list[LessonRead]` (orden, raíz primero) | `200` · `404` |
| POST | `/lessons/{id}/answer` | `[NIÑO]` | `AnswerRequest` `{choice_index}` | `AnswerResult` `{correct, explanation, concept}` | `200` · `404` |

- `/ask` creará un **nuevo turno** en el hilo conversacional (nueva fila `Lesson` con `parent_id` / `root_id`).
- `/thread` devolverá todos los turnos del hilo ordenados, con la raíz en primer lugar.
- La moderación de entrada podrá bloquear una curiosidad inapropiada devolviendo `422`.

## 5. Espacio del niño — prefijo `/me`

Router `me`

| Método | Ruta | Auth | Request | Response | Códigos |
| --- | --- | --- | --- | --- | --- |
| GET | `/me/knowledge` | `[NIÑO]` | — | `list[KnowledgeNodeRead]` | `200` |
| GET | `/me/suggestions` | `[NIÑO]` | — | `list[Suggestion]` `{curiosity, emoji}` (5 fijas) | `200` |
| GET | `/me/profile` | `[NIÑO]` | — | `ChildProfile` `{name, age, islands, avatar, avatar_image_url}` | `200` |

`islands` = número de nodos de conocimiento (`knowledge_nodes`) del niño (campo derivado en la respuesta).

## 6. Historias

Router `stories` · esquemas `story`

| Método | Ruta | Auth | Request | Response | Códigos |
| --- | --- | --- | --- | --- | --- |
| POST | `/me/stories` | `[NIÑO]` | datos de la historia | `StoryRead` (`pending`) | `201` |
| GET | `/me/stories` | `[NIÑO]` | — | `list[StoryRead]` (solo `approved`) | `200` |
| GET | `/me/stories/{id}` | `[NIÑO]` | — | `StoryRead` | `200` · `404` |
| GET | `/family/stories` | `[FAMILIA]` | query `status_filter?` | `list[StoryRead]` | `200` |
| PUT | `/family/stories/{id}` | `[FAMILIA]` | `{action: approve\|reject, title?, body?}` | `StoryRead` | `200` · `404` |

- El niño solo podrá listar sus historias **aprobadas**; las recién creadas quedarán en `pending`.
- La familia listará todas (opcionalmente filtrando por estado) y aprobará/rechazará, pudiendo además editar `title`/`body` al aprobar.

## 7. Configuración de IA — prefijo `/family/ai-config`

Router `ai_config` · esquemas `ai_config`

| Método | Ruta | Auth | Request | Response | Códigos |
| --- | --- | --- | --- | --- | --- |
| GET | `/family/ai-config/catalog` | `[FAMILIA]` | — | `{providers, ollama_models, default_local_model, image_providers}` | `200` |
| POST | `/family/ai-config/recommend` | `[FAMILIA]` | `HardwareQuery` `{vram_gb≥0, ram_gb≥0}` | `Recommendation` `{can_run_local, fits, recommended, note}` | `200` |
| GET | `/family/ai-config` | `[FAMILIA]` | — | `AIConfigRead` | `200` |
| PUT | `/family/ai-config` | `[FAMILIA]` | `AIConfigUpdate` | `AIConfigRead` | `200` · `422` tier/provider inválido · `400` falta `AI_CONFIG_KEY` |

- `/catalog` y `/recommend` ayudarán a la familia a elegir proveedor y modelo según su hardware.
- **`AIConfigRead` nunca devolverá claves de API.** En su lugar expondrá los booleanos `has_api_key` y `has_image_api_key`.
- El `422` en `PUT` se producirá si `tier`/`provider` no pertenecen al conjunto válido; el `400` si falta la variable de entorno `AI_CONFIG_KEY` necesaria para cifrar con Fernet.

## 8. Patrón de seguridad estrella: el quiz nunca filtrará la respuesta

El contrato más importante de la API, como **regla de diseño**, es que **`LessonRead` nunca expondrá la respuesta correcta ni la explicación del quiz** antes de que el niño responda. Esta regla se garantizará en **tres capas independientes**:

1. **Esquema de salida (`LessonRead` / `QuizPublic`).** `LessonRead.quiz` será de tipo `QuizPublic`, que solo contendrá `{question, options}`. No existirá campo para `correct_index` ni `explanation`, de modo que aunque un objeto llevara esos datos, Pydantic no los serializaría.

   ```python
   class QuizPublic(BaseModel):
       question: str
       options: list[str]
   ```

2. **Serialización (`to_read_dict` en el servicio de lecciones).** El diccionario que alimentará `LessonRead` construirá `quiz` únicamente con `question` y `options`; `quiz_correct_index` y `quiz_explanation` no se copiarán.

   ```python
   "quiz": {"question": lesson.quiz_question, "options": lesson.quiz_options},
   ```

3. **Validación en servidor (`answer_lesson`).** La corrección se calculará **solo** en el servidor comparando el índice enviado con el almacenado, y la explicación se devolverá **solo** en la respuesta de `POST /lessons/{id}/answer`:

   ```python
   correct = choice_index == lesson.quiz_correct_index
   return {"correct": correct, "explanation": lesson.quiz_explanation, "concept": lesson.concept}
   ```

Resultado esperado: el cliente nunca recibirá `quiz_correct_index`, y `quiz_explanation` solo llegará tras responder. Un niño no podrá "adivinar" la respuesta inspeccionando el tráfico de red.

## 9. Esquemas clave

### `ChildRead`

```
{ id, name, birthdate, avatar, avatar_image_url, age }
```

No expondrá `pin_hash` ni `family_id`. `age` será un `computed_field` derivado de `birthdate`.

### `LessonRead`

```
{ id, curiosity, subject, concept, title, body, fun_fact,
  answered, quiz: QuizPublic{question, options}, follow_ups: list[str], image_url }
```

Sin `quiz_correct_index`, sin `quiz_explanation`, sin `parent_id`/`root_id`.

### `AIConfigRead`

```
{ tier, provider, model, base_url, has_api_key: bool,
  monthly_quota, used_count,
  image_provider, image_model, image_base_url, image_enabled, has_image_api_key: bool }
```

Nunca devolverá `api_key_encrypted` ni `image_api_key_encrypted`; solo los booleanos `has_api_key` / `has_image_api_key`.

### `AIConfigUpdate` (entrada del `PUT`)

```
{ tier, provider, model?, base_url?, api_key?,
  image_provider="none", image_model?, image_base_url?, image_api_key?, image_enabled=false }
```

Las claves (`api_key`, `image_api_key`) se recibirán en claro **solo** en la petición de escritura y se cifrarán con Fernet antes de persistirse.

### `Token` / `RegisterResult`

```
Token          -> { access_token, token_type="bearer" }
RegisterResult -> { access_token, token_type="bearer", recovery_code }
RecoveryResult -> { recovery_code }
```

## 10. Referencia interactiva

La especificación OpenAPI completa (con todos los esquemas, códigos y ejemplos) se generará automáticamente por FastAPI y estará disponible en:

- **Swagger UI:** `/docs`
- **OpenAPI JSON:** `/openapi.json`

Una vez implementada, esa documentación viva será la fuente autoritativa; el presente documento se mantiene como resumen de diseño previo para la Entrega 1.
