# Informe — e3-cierre

- Fecha: 2026-09-27
- Rama: `main`
- HU / RF cubiertos: US10, US11 · `RF-IA-06` (validación del proveedor de imagen), `RF-PLT-03`
  (`image_enabled` gobierna las imágenes)
- Brief: [`task-e3-cierre-brief.md`](../briefs/task-e3-cierre-brief.md)

## Qué se verificó

Tres correcciones del mismo patrón —el **fallo silencioso**— y una anotación errónea del libro mayor:

1. `image_provider` no se validaba contra el catálogo: un id inventado se guardaba con **200** y
   `build_image_generator` caía al stub sin decir nada. `RF-IA-06` declaraba la lista cerrada.
2. El panel no avisaba si había proveedor de imagen elegido con las imágenes desactivadas.
   Detectado el 15-09, invisible desde entonces.
3. `OpenAIImageGenerator`: el libro mayor pedía añadir `response_format=b64_json`. **La anotación era
   incorrecta** y aplicarla habría roto el adaptador. Se cierra al contrario, con centinela.

## Comandos ejecutados

- `./.venv/Scripts/python.exe -m pytest tests/test_ai_config_api.py -q`
- `./.venv/Scripts/python.exe -m pytest tests/test_images.py -q`
- `./.venv/Scripts/python.exe -m pytest -q`
- `./.venv/Scripts/python.exe -m ruff check .`
- `npx vitest run src/screens/AIConfigPanel.test.tsx`
- `npx vitest run`
- `npx tsc --noEmit` · `npm run lint`
- `DATABASE_URL="sqlite:///./verif_e3.db" ./.venv/Scripts/python.exe -m alembic upgrade head`
- `uvicorn app.main:app --host 127.0.0.1 --port 8000` + `npm run dev` (5173)
- `node verif-e3.mjs` (Playwright sobre el Chrome del sistema)

## Resultado de tests

| | Antes | Después |
|---|---|---|
| Dirigidos `test_ai_config_api.py` | 7 passed | **9 passed**, 0 failed |
| Dirigidos `test_images.py` | 14 passed | **16 passed**, 0 failed |
| Dirigidos `AIConfigPanel.test.tsx` | 2 passed | **4 passed**, 0 failed |
| **Suite backend** | 182 passed | **186 passed**, 0 failed · ruff: **limpio** |
| **Suite frontend** | 74 passed (32 ficheros) | **76 passed** (32 ficheros) · tsc: **limpio** |

Duración: backend 39,89 s · frontend 6,12 s.

Los cuatro tests nuevos del backend y los dos del frontend se escribieron **antes** que la
implementación, uno por ciclo (TDD Guard rechazó el primer intento de añadir dos a la vez). Rojos
reales observados: `assert 200 == 422` en la validación del proveedor, y `KeyError: 'b64_json'` en el
adaptador de OpenAI.

## Estado de base de datos

- **Sin migración**: los tres cambios son de validación, presentación y lectura defensiva. Ninguna
  entidad ni columna nueva.
- Se creó una base limpia para la verificación (`verif_e3.db`) y se aplicaron las migraciones
  existentes de cero: revisión final **`ad23d09d1b34` (head)**, 11 migraciones sin error.
- No se ejecutó `downgrade`: no hay revisión nueva que revertir.
- **Estado restaurado:** sí. `verif_e3.db` era un fichero desechable, borrado al terminar; la
  `chispa.db` de desarrollo no se tocó (se apuntó `DATABASE_URL` a la otra).

## Endpoints probados (curl)

Contra el servidor real en `127.0.0.1:8000`, con token de familia obtenido por `POST /auth/register`.

| Método y ruta | Caso | Esperado | Obtenido |
|---|---|---|---|
| `PUT /family/ai-config` | camino feliz, `image_provider=pollinations` | 200 | **200** ✅ |
| `PUT /family/ai-config` | `image_provider=midjourney` (no existe) | 422 | **422** `{"detail":"Proveedor de imagen no disponible"}` ✅ |
| `GET /family/ai-config` | estado tras el rechazo | sigue en `pollinations`/`true` | **sigue en `pollinations`/`true`** ✅ |
| `PUT /family/ai-config` | sin token | 401 | **401** ✅ |

El tercer caso es el que importa además del código: el 422 **no deja escrito a medias**.

No aplica la comprobación de `quiz_correct_index` / `quiz_explanation`: ningún endpoint de esta tarea
devuelve una lección.

## E2E

Chrome del sistema conducido con Playwright. Login real de familia, no un estado inyectado.

- **Flujo recorrido:** `/login` → alta de sesión → `/familia` → `/familia/ia`.
- **El aviso aparece al ABRIR el panel**, sin tocar ningún control, con la configuración ya guardada
  como `image_provider=pollinations`, `image_enabled=false`. Texto literal leído del DOM:
  «⚠️ Has elegido un proveedor de imagen, pero las imágenes están desactivadas: las lecciones saldrán
  sin ilustración. Marca «Activar imágenes» y guarda.»
  Es el caso exacto que llevaba invisible desde el 15-09.
- **Reactivo sin guardar ni recargar:** marcar la casilla lo hace desaparecer; desmarcarla lo
  devuelve. Confirma que se deriva del render y no del guardado.
- **Ancho de móvil (390 px):** el aviso se lee entero, sin desbordar ni cortar.
- **422 desde el navegador**, a través del proxy de Vite: `422 {"detail":"Proveedor de imagen no
  disponible"}`.

Capturas en `docs/entrega-3/evidencias/`:

| Fichero | Qué muestra |
|---|---|
| `e3-01-aviso-imagen-desactivada.png` | El aviso al abrir el panel (escritorio, 1280 px) |
| `e3-02-aviso-desaparece-al-activar.png` | Desaparece al marcar «Activar imágenes» |
| `e3-03-aviso-movil.png` | El aviso a 390 px de ancho |

**Consola del navegador:** sin errores propios de la aplicación. El único `console.error` es el 401
—y después el 422— que **provoca el propio guion de verificación** al llamar al endpoint con un
proveedor inventado: el navegador registra toda respuesta HTTP fallida. Los avisos de *future flags*
de React Router siguen ahí, filtrados, y siguen siendo los mismos dos de la Entrega 2.

## Hallazgos colaterales

1. **El ejemplo de `curl` de la skill `chispa-verificar` está caducado.** Propone
   `demo@chispa.test`, y `email-validator` rechaza el TLD `.test` como *special-use*: el alta
   devuelve 422, no un token. Quien siga la skill al pie de la letra se atasca en el paso 4.
   Corregido en la skill a un dominio válido.
2. **El límite de intentos funciona, y me cortó a mí**: tras varios intentos fallidos de alta, el
   servidor devolvió `429 {"detail":"Demasiados intentos..."}`. Se resolvió reiniciando el proceso,
   que es exactamente la limitación declarada en ADR-008 (los contadores viven en memoria). Sirve de
   comprobación no planificada de las dos cosas.

## Documentación actualizada

- `.superpowers/sdd/briefs/task-e3-cierre-brief.md` — brief nuevo.
- `.superpowers/sdd/progress.md` — anotación de OpenAI corregida, con el motivo.
- `docs/entrega-2/estado-implementacion.md` — la deuda del panel pasa a resuelta y se documenta el
  segundo fallo silencioso encontrado al lado.
- `.claude/skills/chispa-verificar/SKILL.md` — ejemplo de `curl` corregido.

## Resultado

**PASA.** Cadena completa en verde: 186 backend + 76 frontend, ruff y tsc limpios, migraciones al
día, los cuatro casos de `curl` correctos —incluido que el rechazo no escribe a medias— y el aviso
verificado en un navegador real, en escritorio y en móvil, apareciendo **al abrir** el panel.

Pendiente, fuera del alcance de esta verificación: **redesplegar en la VM** para que la demo
publicada incorpore las tres correcciones.
