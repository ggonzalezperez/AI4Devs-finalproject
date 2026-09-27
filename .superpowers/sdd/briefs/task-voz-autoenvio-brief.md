# Brief — voz-autoenvio: enviar la pregunta al terminar el dictado

## Contexto

Hoy el dictado por voz (RF-PLT-02, US11) solo **rellena** el campo: el niño dicta y después
tiene que pulsar el botón de enviar (🧭 en Spark, 🔎 en la lección). Para un niño pequeño ese
segundo paso es fricción: ya ha "hablado con Chispa" y la app no reacciona.

Petición del propietario: al dejar de grabar, que se envíe directamente.

**Hallazgo doc↔código:** RF-PLT-02 declara como mitigación de riesgo *"precisión de
reconocimiento variable entre navegadores: mitigado permitiendo edición del texto
transcrito"*. El autoenvío **elimina** esa mitigación. Decisión tomada: se implementa el
autoenvío y se corrige el RF, porque la fricción del doble paso pesa más en el usuario real
(un niño de 4 años) que la transcripción imperfecta, que además puede reintentarse.

## Alcance

- **Entra:** autoenvío tras una transcripción con texto, en las dos pantallas que tienen
  micrófono (Spark → crear lección; LessonScreen → siguiente turno). Corrección de RF-PLT-02.
- **No entra:** cuenta atrás o botón de cancelar antes de enviar; edición por voz; cambios en
  la lectura en voz alta (RF-APR-04); autoenvío desde las sugerencias o los follow-ups.
- **Mínimo entregable:** el niño pulsa 🎤, habla, y al callarse su pregunta se envía sola sin
  tocar nada más.

## Diseño

- **Backend:** ninguno. No se toca ningún endpoint.
- **Frontend:**
  - `components/MicButton.tsx`: nueva prop opcional `onAutoSubmit?: (text: string) => void`.
    En `onresult`, tras `onText(text)`, si viene `onAutoSubmit` se llama **con el texto**, no
    leyendo el estado (el estado de React aún no se ha actualizado: usar `curiosity` daría el
    valor anterior).
  - `screens/Spark.tsx`: `onAutoSubmit={(texto) => void start(texto)}`.
  - `screens/LessonScreen.tsx`: `onAutoSubmit={(texto) => void ask(texto)}`.
  - Sin claves i18n nuevas.
- **Datos:** ninguno. Sin migración.

## Reglas de negocio

- Solo se envía si la transcripción trae texto no vacío; con texto vacío se comporta como hoy.
- El autoenvío **no** salta la moderación: `start()` y `ask()` siguen tratando el 422 con
  `spark.blocked`. La entrada dictada del niño se modera igual que la escrita.
- Si el componente está `disabled` (hay una petición en curso) el botón no es pulsable, así
  que no puede haber doble envío.
- El texto transcrito sigue quedando en el input (via `onText`), de modo que si el envío falla
  el niño lo ve y puede corregirlo.

## Validación

| Caso | Dado / Cuando / Entonces | Test previsto |
|---|---|---|
| Camino feliz | Dado el micrófono soportado, cuando la transcripción devuelve texto, entonces se llama a `onAutoSubmit` con ese texto | `envía la pregunta al terminar el dictado` |
| Texto vacío | Dada una transcripción vacía, entonces no se autoenvía | `no envía nada si la transcripción viene vacía` |
| Sin la prop | Dado un MicButton sin `onAutoSubmit`, entonces solo rellena el campo y no rompe | tests existentes siguen verdes |
| Contexto inseguro | Dado http por IP, entonces ni transcribe ni autoenvía | test ya existente de `isSecureContext` |

## Trazabilidad

HU: US11 · RF: RF-PLT-02 (corregido) · Pantallas: Spark, LessonScreen ·
Endpoints: ninguno nuevo (`POST /lessons`, `POST /lessons/{id}/ask` ya existentes) ·
Tests: `MicButton.test.tsx`

## Riesgos

- **Transcripción errónea enviada sin revisión.** Es el riesgo aceptado a cambio de quitar
  fricción. Mitigación parcial: el texto queda visible en el input y el niño puede volver a
  preguntar; la lección errónea es recuperable (crea una isla, no borra nada).
- **Envío accidental** si el niño pulsa el micro sin querer y hay ruido. Mitigación: la Web
  Speech API con `continuous = false` corta sola y una transcripción vacía no envía.
