# Chispa — Manual de uso

Chispa convierte las preguntas de tus hijos en lecciones con ilustración, un reto para
comprobar que lo han entendido, y un mapa de islas que crece con cada cosa nueva que descubren.

Este manual es para **la persona adulta que administra la familia**. El niño no necesita leer nada:
entra con su clave de cuatro dígitos y pregunta.

> **¿Prefieres leerlo con las pantallas delante?** Este mismo manual existe en PDF, con guía de
> pantallas y 17 capturas de la aplicación: **[Chispa-Manual-de-uso.pdf](Chispa-Manual-de-uso.pdf)**.
> Es el formato pensado para imprimir o enviar a otra persona de la familia.

> ¿Buscas cómo instalarlo en tu propio servidor? Eso está en
> [MANUAL.md](MANUAL.md). Aquí se explica **cómo se usa**.

---

## 1. Dos mundos separados

Chispa tiene dos espacios que no se mezclan, y conviene entenderlo antes de empezar porque explica
casi todas sus decisiones:

| | **Tú (adulto)** | **Tu hijo (explorador)** |
|---|---|---|
| Cómo entra | Email y contraseña | Un PIN de 4 dígitos |
| Qué ve | Configuración, panel de aprendizaje, cuentos por aprobar | Sus preguntas, sus lecciones, sus islas |
| Qué **no** puede hacer | — | Salir de su sesión, ver ajustes, tocar la configuración de IA |

Mientras el niño juega, tu sesión sigue abierta en el dispositivo, así que **salir de la sesión del
niño pide tu contraseña otra vez**. Tener el aparato en la mano no basta para volver a los ajustes.

---

## 2. Crear el espacio de tu familia

1. Abre Chispa y pulsa **Crear el espacio de mi familia**.
2. Rellena tu nombre, tu email y una contraseña de al menos 8 caracteres.
3. **Código de invitación**: solo aparece si quien te invitó te dio uno. En la demo pública hace
   falta; en una instalación propia, déjalo vacío.
4. Pulsa **Crear cuenta**.

### El código de recuperación

Justo después verás un código largo, con este aspecto:

```
A3F2-91BC-7D4E-02AA-9C11-55FF-1234-ABCD
```

**Cópialo y guárdalo donde guardes tus contraseñas.** Es lo único que te permite recuperar el acceso
si olvidas la contraseña: Chispa no envía emails de recuperación, porque una aplicación autoalojada
no debe depender de un servidor de correo. No se puede volver a ver.

---

## 3. Añadir un explorador

En el panel de familia, pulsa **➕ Añadir explorador**:

- **Alias**: el nombre con el que aparecerá. Puedes usar un apodo; no hace falta el nombre real.
- **Fecha de nacimiento**: Chispa la usa para **adaptar el lenguaje de las lecciones a su edad**. La
  misma pregunta se responde distinto a los 4 años que a los 10.
- **Clave de 4 dígitos (PIN)**: la que usará para entrar. Elígela con él.
- **Avatar**: uno de los dibujos disponibles, o uno generado con IA describiéndolo con palabras
  (necesita tener la IA configurada).

Puedes añadir tantos exploradores como quieras. Cada uno tiene su propio mapa y sus propias
lecciones: **un hermano no ve lo del otro**.

---

## 4. Elegir cómo se generan las lecciones

Panel de familia → **⚙️ Configurar IA**. Hay tres caminos:

| Opción | Qué hace | Coste |
|---|---|---|
| **Demo** (por defecto) | Lecciones de ejemplo, sin IA real | Ninguno |
| **Local (Ollama)** | Un modelo corriendo en tu propio equipo | Ninguno, pero pide un ordenador capaz |
| **Tu clave (BYOK)** | Usa tu cuenta de OpenAI, Claude, Gemini… | Lo que cobre tu proveedor |

Si no configuras nada, **Chispa funciona igual**: verás lecciones de demostración. Es a propósito,
para que puedas probarla sin pagar ni registrar nada.

### Sobre tu clave de IA

- Se guarda **cifrada** en la base de datos y **nunca se muestra de vuelta**, ni siquiera a ti. El
  panel solo indica si hay una guardada.
- Si pegas algo que no tiene forma de clave del proveedor, se rechaza al guardar. Es deliberado: una
  clave inválida aceptada haría que las lecciones volvieran al modo demo **sin que nadie se entere**.
- Para cambiarla, pega la nueva encima. Para quitarla, borra el campo y guarda.

### Ilustraciones

En el mismo panel, **🖼️ Imágenes en las lecciones**. La opción más fácil es **Pollinations**, que es
gratis y no pide clave. Con OpenAI o Gemini las ilustraciones son mejores, pero las pagas tú.

Si una ilustración falla o tarda demasiado, **la lección se muestra igual, sin imagen**. El niño
nunca ve un error del proveedor.

---

## 5. El día a día del niño

### Entrar

En **¿Quién va a explorar?**, toca su avatar y teclea su PIN. Ya está dentro.

### Preguntar

La pantalla principal pregunta *"¿Qué quieres descubrir hoy?"*. Puede:

- **Escribir** su curiosidad.
- **Hablar**: el botón del micrófono 🎤 transcribe lo que diga y **envía la pregunta al terminar**,
  sin tener que pulsar nada más. Pensado para quien aún no escribe con soltura.
- **Tocar una sugerencia**: cinco ideas distintas cada vez que abre la pantalla.

### La lección

Cada lección trae:

- Un texto adaptado a su edad, con un **dato sorprendente** al final.
- Una **ilustración** acorde a lo que está aprendiendo.
- Un botón para **escucharla en voz alta**, útil si aún no lee bien.
- **Preguntas de seguimiento** sugeridas, para seguir tirando del hilo.
- Un **reto** (🎯) de tres opciones. Acertarlo es lo que marca el tema como aprendido.

Puede seguir preguntando sobre la misma lección: cada respuesta se encadena a la anterior, formando
una conversación que se conserva.

### Sus islas

**🗺️ Tu archipiélago** reúne todo lo que ha descubierto. Cada isla es un tema; tocarla vuelve a esa
conversación. Hay un buscador para encontrar una isla concreta.

### Cuentos

**📚 Mis cuentos** genera un relato donde **el niño es el protagonista**, construido a partir de los
temas que ya ha explorado.

**Ningún cuento se publica sin tu aprobación.** Al crearlo, el niño ve *"¡Listo! Tus padres lo
revisarán pronto"*, y el cuento queda pendiente hasta que tú lo revises.

---

## 6. Lo que ves tú

### Panel de aprendizaje

Panel de familia → **📊 Ver el aprendizaje**. Por cada explorador:

- **Lo que ya domina**: temas cuyo reto ha acertado.
- **Lo que está descubriendo**: temas que ha explorado pero aún no ha afianzado.
- Cuántas islas lleva exploradas.

No es una nota ni un ranking: es un mapa de por dónde anda su curiosidad.

### Cuentos por revisar

Panel de familia → **📚 Cuentos para revisar**. Cada cuento pendiente puedes:

- **Aprobarlo** → aparece en la biblioteca del niño.
- **Editarlo** antes de aprobarlo, cambiando título o texto.
- **Rechazarlo** → no se publica.

### Conectar otro dispositivo

**📱 Conectar otro dispositivo** muestra la dirección de tu instalación y un **código QR**. Escanéalo con la tablet
o el móvil del niño y entra directo, sin teclear direcciones.

---

## 7. Seguridad y privacidad

Lo que Chispa hace por defecto, sin que tengas que configurar nada:

- **No pide datos del menor**: ni nombre real, ni foto, ni colegio. Un alias y una fecha de
  nacimiento, que solo sirve para ajustar el lenguaje.
- **Tus datos son tuyos**: viven en la base de datos de tu instalación, no en un servicio ajeno.
- **Las claves de IA se guardan cifradas** y nunca se devuelven.
- **Se modera lo que el niño escribe**: ante una entrada inapropiada, responde *"Esta la vemos con un
  adulto"* 🛟 en lugar de generar contenido dudoso.
- **El niño nunca ve un error técnico.** Si un proveedor falla, la lección llega igual por otro
  camino.
- **Límite de intentos**: tras varios fallos seguidos con la contraseña o el PIN, Chispa hace esperar
  unos minutos. Protege contra quien pruebe combinaciones a lo bruto, incluido un hermano con
  paciencia.

---

## 8. Cuando algo no va

| Lo que ves | Qué pasa | Qué hacer |
|---|---|---|
| **"Esta la vemos con un adulto" 🛟** | La moderación bloqueó la pregunta | Léela con él. Si era inocente, reformúlala: la lista de palabras puede equivocarse |
| **"Demasiados intentos. Espera un momento"** | Demasiados fallos seguidos de contraseña o PIN | Esperar unos minutos. No es un bloqueo permanente |
| **"Aquí no puedo escuchar"** al pulsar el micrófono | La voz necesita conexión segura (https), y estás entrando por una dirección `http` | Entra por el dominio con https, o escribe la pregunta |
| **La lección no trae ilustración** | El proveedor de imagen falló, está desactivado o no tiene clave | Revisa **⚙️ Configurar IA → Imágenes**. La lección funciona igual |
| **Las lecciones parecen genéricas** | Está en modo demo, sin IA real configurada | Configura un proveedor o una clave propia |
| **Olvidaste la contraseña** | — | **Entrar → ¿Olvidaste tu contraseña?** y usa el código de recuperación que guardaste al crear la cuenta |
| **Perdiste el código de recuperación y la contraseña** | No hay recuperación posible por diseño | Quien administre el servidor tendrá que intervenir en la base de datos |

---

## 9. Detalles útiles

- **Idioma**: español e inglés, con el selector 🌐 de cada pantalla. Cambia toda la interfaz al
  instante.
- **Sesión del adulto**: dura 30 días en ese dispositivo. La del niño se cierra al salir.
- **Cambiar tu contraseña**: panel de familia → **Cambiar contraseña**. Pide la actual.
- **Funciona en móvil, tablet y ordenador**, con el mismo diseño adaptado a cada pantalla.
