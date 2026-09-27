# Brief — e3-cierre: fallo silencioso de imagen, adaptador de OpenAI, guía de pantallas y acceso de revisores

## Contexto

Cierre de la entrega. Tres deudas declaradas en
[`docs/entrega-2/estado-implementacion.md`](../../../docs/entrega-2/estado-implementacion.md) §4 y en
el libro mayor quedan abiertas, y la entrega necesita además que un revisor externo pueda **usar** la
aplicación publicada sin hablar con el autor.

Las tres deudas comparten un patrón que ya nos ha costado dos jornadas de diagnóstico: **el fallo
silencioso**. La familia configura algo, la aplicación no protesta, y el niño recibe contenido del
stub mientras el adulto cree estar usando la IA que eligió. Es el mismo patrón de los identificadores
de modelo caducados (§3, hallazgo 7) y de la clave mal pegada (que ya se mitigó con `check_key_shape`).

Motivación por requisito:

- **RF-IA-06** (Proveedores de imagen) declara como regla de negocio
  `image_provider ∈ {none, huggingface, local_sdxl, openai, gemini, pollinations}`. El código **no la
  comprueba**: `put_config` valida el proveedor de texto contra el catálogo y devuelve 422, pero
  asigna `cfg.image_provider = payload.image_provider` sin mirar. Un proveedor inexistente se guarda
  con 200 y `build_image_generator` cae al stub sin decir nada.
  → **Divergencia documento↔código. Se corrige el código:** la regla del requisito es la correcta.
- **RF-PLT-03** (Imágenes IA desactivadas por defecto) gobierna el 409 del avatar con
  `image_enabled`. El endpoint del avatar **sí** avisa (409); el panel de configuración **no**: se
  puede guardar proveedor y clave con la casilla desactivada y no ocurre nada, sin señal. Detectado
  el 15-09-2026, sin tocar desde entonces.
- **Adaptador de OpenAI:** el libro mayor arrastra `Minor open: OpenAIImageGenerator missing
  response_format=b64_json`. **Verificado contra la documentación del proveedor durante este brief:
  la anotación es incorrecta y añadir el parámetro rompería el adaptador.** Ver §Diseño.

## Alcance

**Entra:**

1. Backend — `put_config` valida `image_provider` contra `IMAGE_PROVIDERS` y devuelve 422 si no
   existe o está deshabilitado (simetría con el proveedor de texto).
2. Frontend — el panel de IA avisa cuando hay proveedor de imagen elegido y las imágenes están
   desactivadas. Aviso, **no** bloqueo.
3. Backend — cierre razonado del *minor open* de OpenAI: **no** se añade `response_format`, se
   documenta por qué y se blinda con un test centinela; y el adaptador deja de estallar si la
   respuesta no trae `b64_json`.
4. Documentación — guía de pantallas con las 16 capturas en `docs/manual-usuario.md`, y sección
   resumen nueva en `README.md` con 3–4 capturas y enlace al manual.
5. Documentación — `docs/entrega-3/` con el acceso de revisores: pasos de Cloudflare Access,
   credenciales de la familia de demostración y qué recorrido hacer.
6. Operación — familia de demostración poblada en la VM (2 exploradores, lecciones, islas y un cuento
   pendiente de aprobar) y alta del correo de revisión en la política de Access.
7. Documentación — guion de recuperación de `sudo` en la VM por consola VNC. **Lo ejecuta el
   propietario**, no esta sesión.

**No entra** (y alguien podría asumir razonablemente que sí):

- **Validar `image_model` contra el catálogo.** El `<select>` del panel ya limita al catálogo, y una
  lista cerrada en el servidor bloquearía cualquier modelo que el proveedor publique entre entregas
  —exactamente el problema que causó el hallazgo 7 al revés—. Se deja declarado.
- **Bloquear el guardado de proveedor con la casilla desactivada.** Preparar la configuración hoy y
  activarla mañana es un uso legítimo. La corrección es hacer visible el estado, no prohibirlo.
- `monthly_quota` que se cuenta pero no se aplica, y el tier `managed`: siguen aplazados.
- Migración a `httpx2`, moderación como servicio real: sin cambios.
- Dejar Access en **Bypass** como estado permanente. Se documenta como plan B de un minuto, no se
  aplica.

**Mínimo entregable:** guardar un proveedor de imagen con la casilla desactivada muestra un aviso
claro y accesible en el panel; un `image_provider` inexistente recibe 422; el adaptador de OpenAI
tiene test centinela y no lanza `KeyError`; el manual tiene guía de pantallas y el README su resumen;
y un revisor entra a `https://chispa.chispalearn.com` con credenciales documentadas y encuentra datos.

## Diseño

### Backend

**`app/routers/ai_config.py` — validación del proveedor de imagen**

En `put_config`, antes de asignar, replicando el patrón que ya existe para el proveedor de texto:

```python
image_provider = next(
    (p for p in ai_catalog.IMAGE_PROVIDERS if p["id"] == payload.image_provider), None
)
if image_provider is None or not image_provider["enabled"]:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="Proveedor de imagen no disponible",
    )
```

Sin cambio de esquema, sin migración. Endpoint: `PUT /family/ai-config`, token **family**, entrada
`AIConfigUpdate`, salida `AIConfigRead`, códigos **200** / **422** (proveedor o nivel inválido, clave
con forma incorrecta) / **400** (sin `AI_CONFIG_KEY`) / **401** (sin token) / **403** (token de niño).

**`app/services/image_providers.py` — adaptador de OpenAI**

`response_format` **no se añade.** Verificado en la documentación de OpenAI y en informes
independientes: el parámetro existe solo para `dall-e-2` y `dall-e-3`; la familia `gpt-image-*`
—la única del catálogo— **siempre** devuelve `b64_json` y **rechaza** `response_format` con
«Unknown parameter». Enviarlo convertiría un adaptador que hoy funciona (ilustración real verificada
de punta a punta el 21-09) en un 400 que el *best-effort* del `lesson_service` absorbería en
silencio: precisamente el fallo que este brief viene a cerrar.

Se deja constancia de la decisión en dos sitios, porque un comentario solo no impide que otra sesión
«arregle» la anotación del libro mayor:

- Comentario en el adaptador con el motivo y el alcance (`gpt-image-*` sí, `dall-e-*` no).
- **Test centinela** que falla si el cuerpo de la petición incluye `response_format`.

Y se blinda la lectura de la respuesta, hoy la única del módulo que indexa a ciegas
(`resp.json()["data"][0]["b64_json"]`): pasa a `.get()` en cadena y devuelve `None` si falta, como ya
hacen `LocalSDXLImageGenerator` y `GeminiImageGenerator`. `None` es contrato válido de
`ImageGenerator`: la lección sale sin ilustración en vez de romper la petición.

### Frontend

**`src/screens/AIConfigPanel.tsx`** — estado derivado, sin petición nueva ni estado nuevo:

```tsx
const imageMisconfigured = imageProvider !== "none" && !imageEnabled;
```

Se pinta dentro de la tarjeta de imagen, tras la casilla, con `role="status"` (es información, no un
error del usuario: `role="alert"` está reservado en este panel a los fallos de guardado). Aparece
igual al **cargar** una configuración guardada así y al **cambiar** los controles, porque se deriva
del render y no del guardado — que es la razón por la que el fallo pasó inadvertido desde el 15-09.

Claves i18n nuevas, en español **e** inglés:

| Clave | es | en |
|---|---|---|
| `aiPanel.imgDisabledWarning` | «⚠️ Has elegido un proveedor de imagen, pero las imágenes están desactivadas: las lecciones saldrán sin ilustración. Marca «Activar imágenes» y guarda.» | "⚠️ You picked an image provider, but images are off: lessons will have no illustration. Tick “Enable images” and save." |

Pantallas: `/familia/ia` (`AIConfigPanel`). Sin rutas nuevas, sin componentes nuevos.

### Datos

Ninguna entidad nueva, **ninguna migración**. Los tres cambios son de validación, presentación y
lectura defensiva.

### Documentación

- `docs/manual-usuario.md` — sección de guía de pantallas. Las 16 capturas de
  `docs/entrega-2/evidencias/` se referencian con rutas relativas y **texto alternativo descriptivo**
  (el manual lo leen familias, y el alt es lo que queda si la imagen no carga). Las capturas no se
  mueven ni se duplican: son la evidencia de la Entrega 2 y siguen sirviendo de evidencia.
- `README.md` — sección «Guía de pantallas» con 3–4 capturas y enlace al manual. **Sin duplicar
  texto** del manual: el README resume y enlaza.
- `docs/entrega-3/acceso-revisores.md` — ver §Reglas de negocio.
- `docs/entrega-3/recuperar-sudo-vm.md` — guion VNC, para el propietario.

## Reglas de negocio

Las que el implementador no puede deducir del código:

1. **El aviso avisa, no bloquea.** Guardar proveedor + clave con `image_enabled=false` sigue
   devolviendo 200. Preparar hoy y activar mañana es legítimo.
2. **`response_format` no se añade nunca al adaptador de OpenAI** mientras el catálogo solo ofrezca
   `gpt-image-*`. Si algún día entra un `dall-e-*`, entonces —y solo entonces— el parámetro es
   obligatorio y `output_format`/`output_compression`/`quality` dejan de valer. El test centinela es
   el recordatorio.
3. **Seguridad del menor — el aviso no filtra la clave.** El panel ya distingue «hay clave guardada»
   (`has_image_api_key`) de la clave misma, que el servidor nunca devuelve. El aviso nuevo se deriva
   de `image_provider` y `image_enabled`, dos valores no sensibles: **no** menciona ni pinta la clave.
4. **Seguridad del menor — la familia de demostración es una familia real de la base de datos
   publicada.** Por tanto: PIN de 4 dígitos como cualquier otra, ningún dato personal de menores
   reales (nombres inventados), y su contenido pasa la misma moderación. Las credenciales se
   documentan **solo** en el repositorio privado.
5. **Cloudflare Access — el correo de revisión debe estar en la política `Allow` para que el PIN
   llegue.** Verificado en la documentación de Cloudflare: *«Cloudflare only sends the email if the
   user is allowed by an Access policy»*. Un correo fuera de la lista no recibe nada y la pantalla
   muestra el mismo mensaje, así que un alta mal escrita se diagnostica como «no llega el correo».
   Ruta del panel: **Zero Trust → Access controls → Policies → Configure**; el cambio surte efecto al
   guardar, sin redespliegue. El PIN caduca a los **10 minutos**, es de **un solo uso**, y pedir uno
   nuevo invalida el anterior. Remitente a permitir en el buzón: `noreply@notify.cloudflare.com`.

## Validación

| Caso | Dado / Cuando / Entonces | Test previsto |
|---|---|---|
| Camino feliz (backend) | **Dado** una familia autenticada **cuando** guarda cada uno de los seis proveedores del catálogo **entonces** 200 y `AIConfigRead` lo refleja | `test_put_acepta_los_proveedores_de_imagen_del_catalogo` |
| Error esperado (backend) | **Dado** una familia autenticada **cuando** envía `image_provider="inventado"` **entonces** 422 «Proveedor de imagen no disponible» y la configuración **no** cambia | `test_put_rechaza_proveedor_de_imagen_desconocido` |
| Centinela (backend) | **Dado** el adaptador de OpenAI **cuando** genera **entonces** el cuerpo enviado **no** contiene `response_format` y sí `output_format=webp` | `test_openai_no_envia_response_format` |
| Respuesta degenerada (backend) | **Dado** que OpenAI responde 200 sin `b64_json` (p. ej. `{"data":[{"url":"…"}]}`) **cuando** se genera **entonces** devuelve `None` y **no** lanza | `test_openai_sin_b64_json_devuelve_none` |
| Camino feliz (frontend) | **Dado** el panel con proveedor de imagen e imágenes **activadas** **entonces** no hay aviso | `AIConfigPanel > no avisa si las imágenes están activadas` |
| Fallo silencioso cerrado | **Dado** una configuración guardada con `image_provider="openai"`, `has_image_api_key=true` e `image_enabled=false` **cuando** se abre el panel **entonces** aparece el aviso con `role="status"` | `AIConfigPanel > avisa si hay proveedor de imagen con las imágenes desactivadas` |
| Sin proveedor | **Dado** `image_provider="none"` e `image_enabled=false` **entonces** no hay aviso (es el estado por defecto, no un error) | `AIConfigPanel > no avisa en el estado por defecto` |
| Acceso cruzado | **Dado** un token de **niño** **cuando** llama a `PUT /family/ai-config` **entonces** 403 y ninguna escritura | ya cubierto por la suite de `ai_config`; se comprueba que sigue en verde |
| Moderación | No aplica: ninguna entrada nueva del niño en esta tarea | — |

Además, y porque la Entrega 2 dejó anotado que *«la revisión la hizo la misma sesión que
implementó»*: la revisión adversaria de esta tarea la hace una **sesión distinta**
(`chispa-revision-adversaria`), y el recorrido del revisor se verifica **contra la demo publicada**,
no contra `localhost`.

## Trazabilidad

**HU:** US10 (IA configurable), US11 (imágenes) · **RF:** RF-IA-06 (validación del proveedor de
imagen), RF-PLT-03 (`image_enabled` gobierna las imágenes) · **Pantallas:** `/familia/ia`
(`AIConfigPanel`) · **Endpoints:** `PUT /family/ai-config` · **Ficheros:**
`backend/app/routers/ai_config.py`, `backend/app/services/image_providers.py`,
`frontend/src/screens/AIConfigPanel.tsx`, `frontend/src/i18n/translations.ts`,
`docs/manual-usuario.md`, `README.md`, `docs/entrega-3/` · **Tests:**
`backend/tests/test_ai_config_api.py`, `backend/tests/test_images.py`,
`frontend/src/screens/AIConfigPanel.test.tsx`

## Riesgos

| Riesgo | Mitigación |
|---|---|
| **El buzón compartido de revisión se bloquea el día de la corrección.** Un Gmail recién creado, con 2FA y accedido desde una IP y un país desconocidos, es el caso que Google desafía con verificación por teléfono. Si desafía, el revisor no recibe el PIN y **no hay plan B inmediato** | Crear el buzón con antelación y abrirlo una vez desde el navegador; **sin** 2FA; y documentar el **Bypass de Access** como plan B de un minuto, con la aplicación defendida por su propio login, `INVITE_CODE` y límite de intentos |
| Añadir `response_format` «arreglando» la anotación del libro mayor rompería el adaptador | Test centinela + comentario + esta entrada. Y se **corrige la anotación** del libro mayor, que es lo que induce el error |
| El 422 nuevo rompe un cliente que hoy guarda un proveedor de imagen vacío (`""`) | `""` no está en el catálogo, así que pasaría de 200 silencioso a 422. El panel siempre envía un id del catálogo; se comprueba con la suite del panel en verde |
| Las capturas son de la Entrega 2 y la interfaz ha cambiado desde entonces | Se revisan una a una antes de incrustarlas; la que no corresponda a la interfaz actual se repite contra la demo publicada |
| La familia de demostración se llena de contenido ajeno durante la corrección | Aceptado: es el objetivo. El volumen `pgdata` es independiente del portátil, así que no contamina nada propio |
| El límite de intentos deja fuera al revisor si falla el PIN del niño | Documentar en el recorrido el PIN correcto en primer lugar, y dejar anotado `RATE_LIMIT_ENABLED` como interruptor de urgencia |
