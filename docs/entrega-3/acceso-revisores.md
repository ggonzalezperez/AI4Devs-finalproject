# Acceso de revisores a la demo publicada

> Para quien corrige la entrega. La aplicación está en **https://chispa.chispalearn.com** y corre en
> una máquina doméstica, publicada por un túnel de Cloudflare. No hay nada que instalar.

## Hay dos puertas, y son independientes

Es lo primero que hay que entender, porque si no parece que la aplicación esté rota:

| | Qué es | Qué pide |
|---|---|---|
| **1. Cloudflare Access** | El portero de fuera. Protege **todas** las rutas, incluida `/api` | Un código de 6 dígitos enviado por email |
| **2. Chispa** | La aplicación en sí | Email y contraseña de la familia |

Pasar la primera **no** te mete en la aplicación: te deja ver su pantalla de bienvenida. Es lo
esperado.

## Puerta 1 — Cloudflare Access

1. Abre **https://chispa.chispalearn.com**.
2. En el campo **Email**, escribe la dirección que se te ha facilitado y pulsa **Send login code**.
3. Abre ese buzón, copia el código de 6 dígitos y pégalo.

Detalles que ahorran un susto:

- El remitente es `noreply@notify.cloudflare.com`. **Mira la carpeta de spam** la primera vez.
- El código **caduca a los 10 minutos** y es de **un solo uso**. Si pides otro, el anterior deja de
  valer, así que usa siempre el más reciente.
- Si el código no llega, no insistas: avisa. Cloudflare solo lo envía a direcciones autorizadas de
  antemano, y la pantalla muestra el mismo mensaje tanto si lo manda como si no.

La sesión de Access dura lo que dure la sesión de la aplicación, así que **esto se hace una sola
vez**, no en cada visita.

## Puerta 2 — Entrar en Chispa

Con la familia de demostración ya creada y con datos dentro:

| Dato | Valor |
|---|---|
| Email | `chispausertest@gmail.com` |
| Contraseña | *(se facilita junto con el enlace de entrega)* |
| Exploradores y sus PIN | *(se facilitan junto con el enlace de entrega)* |

> **Por qué la contraseña no está escrita aquí:** este fichero vive en el repositorio, y lo que entra
> en git se queda en su historial para siempre. Las credenciales viajan por el canal de entrega.

### Si prefieres crear tu propia familia

Puedes, y se ve el alta completa. Hace falta el **código de invitación**, que se facilita aparte.

Conviene saber qué es ese código, porque no es lo que su nombre sugiere: **es un único secreto
compartido**, no una invitación personal. Sirve infinitas veces, no caduca y la única forma de
revocarlo es cambiarlo, lo que lo invalida para todos a la vez. Está declarado así en
[`docs/MANUAL.md`](../MANUAL.md) y su propósito es cerrar el registro público, no identificar a
nadie.

## Recorrido sugerido, unos 10 minutos

1. **Panel de familia** → verás la tripulación con sus exploradores.
2. **⚙️ Configurar IA** → el catálogo de proveedores, la recomendación por hardware y el aviso de
   imágenes desactivadas. Sin tocar nada: guardar cambia el comportamiento para todos.
3. **Elige un explorador** e introduce su PIN. Estás ahora en el mundo del niño, que es otro espacio.
4. **Pregunta algo** → mini-lección con ilustración, dato sorprendente y reto de tres opciones.
5. **🗺️ Tu archipiélago** → el mapa de lo aprendido; cada isla reabre su conversación.
6. **Sal de la sesión del niño** → observa que pide la contraseña del adulto. Tener el aparato en la
   mano no basta.
7. **📚 Cuentos para revisar** → la aprobación parental, con aprobar, editar y rechazar.

### Dos cosas que puede que quieras provocar a propósito

- **La moderación**: escribe como niño algo inapropiado y responderá *«Esta la vemos con un adulto»*
  🛟 en lugar de generar contenido.
- **El límite de intentos**: falla la contraseña seis veces seguidas y recibirás un **429** con
  `Retry-After`. Si te autobloqueas, **espera unos minutos**: no es permanente.

## Qué NO es un fallo

| Lo que ves | Por qué pasa |
|---|---|
| Las lecciones parecen genéricas | La demo puede estar en **modo demo** (`ADR-001`): funciona entera sin ninguna clave de IA, a propósito |
| Una lección sin ilustración | La imagen es *best-effort*: si el proveedor falla, la lección llega igual. El niño nunca ve el error |
| El micrófono avisa de que no puede escuchar | La Web Speech API exige contexto seguro. Por el dominio con https funciona; por IP directa, no |
| Te pide el código de Access otra vez | La sesión ha caducado. Repite la puerta 1 |

## Si algo se tuerce el día de la corrección

La aplicación tiene defensa propia —login, código de invitación y límite de intentos por IP y por
cuenta—, así que Access se puede **poner en Bypass** en un minuto sin dejar la demo desnuda:

**Zero Trust → Access controls → Policies → `Autorizados` → Configurar**, y cambiar la acción de
**Allow** a **Bypass**. Surte efecto al guardar, sin redespliegue. Se revierte igual de rápido.

Es el plan B, no el estado normal: mientras Access esté puesto, la aplicación no está expuesta a
internet abierto.
