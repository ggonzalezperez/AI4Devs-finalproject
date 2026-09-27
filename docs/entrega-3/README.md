# Entrega 3 — Versión final desplegada · Chispa ✨

> **Máster LIDR – AI4Devs · Proyecto Final** · Alumno: **Germán González Pérez**
> Fecha: **29 de septiembre de 2026** · Rama: `finalproject-GGP`

La Entrega 1 definía qué construir. La Entrega 2 lo construyó. Ésta lo **publica**: la aplicación está
en internet, con dominio propio, HTTPS y control de acceso, y el flujo completo funciona de punta a
punta.

## 🌐 https://chispa.chispalearn.com

Corre en una máquina doméstica y sale a internet por un **túnel de Cloudflare**. Cómo entrar,
credenciales y recorrido sugerido: **[acceso-revisores.md](acceso-revisores.md)**.

---

## Índice

| Documento | Qué contiene |
|---|---|
| [**acceso-revisores.md**](acceso-revisores.md) | Cómo entrar a la demo, las dos puertas, el recorrido sugerido y qué **no** es un fallo |
| [**herramientas-ia.md**](herramientas-ia.md) | Inventario de skills, agentes y automatismos usados para construir el producto |
| [**recuperar-sudo-vm.md**](recuperar-sudo-vm.md) | Guion de operación para recuperar `sudo` en la máquina de la demo |
| [**evidencias/**](evidencias/) | Capturas del trabajo de esta entrega |

Fuera de esta carpeta:

- [`docs/Chispa-Manual-de-uso.pdf`](../Chispa-Manual-de-uso.pdf) — **manual de uso en PDF**, 18
  páginas con guía de pantallas, para familias.
- [`docs/entrega-2/demo-publica.md`](../entrega-2/demo-publica.md) — la infraestructura que sostiene
  el dominio: túnel, Access, variables y límites conocidos.
- [`docs/entrega-2/estado-implementacion.md`](../entrega-2/estado-implementacion.md) — qué existe
  historia por historia, y la **tabla de deuda conocida**, que se declara en vez de ocultarse.
- [`.superpowers/sdd/`](../../.superpowers/sdd/) — briefs, informes de verificación y libro mayor,
  tarea a tarea. Es la mejor evidencia del proceso.

## Qué cambió en esta entrega

**Publicado.** Dominio `chispalearn.com` en Cloudflare, túnel como contenedor del propio
`docker-compose`, HTTPS y Access delante. La red doméstica está tras **doble NAT y CGNAT**, así que no
había puertos que abrir: el túnel establece una conexión saliente.

**Endurecido.** Publicar convirtió en reales dos riesgos aceptados: se añadió **código de invitación**
en el alta y **límite de intentos** por IP y por cuenta en los cinco endpoints de credenciales, con la
IP resuelta *fail-closed*. Access es defensa perimetral; estos dos controles viven **dentro** de la
aplicación, para que quitar Access no la deje desnuda.

**Corregido, tras la primera jornada de uso real.** Tres fallos que solo existían en la imagen de
producción —caché sirviendo el *bundle* anterior, `VITE_API_URL` horneada, y `??` donde debía ir
`||`— y cuatro **fallos silenciosos** en la última jornada: un proveedor de imagen inválido que se
guardaba con 200, un panel que no avisaba de una configuración inútil, un adaptador que reventaba ante
una respuesta inesperada y un cliente HTTP que destruía el motivo real de los errores.

**Aligerado.** Las ilustraciones pasaron de 2,5 MB a 74 KB pidiéndolas en WebP comprimido; el volumen
de medios bajó de 19 MB a 2 MB.

**Documentado.** Manual de uso en PDF con guía de pantallas, guía de acceso para revisores e
inventario de herramientas de IA.

## Estado

| | |
|---|---|
| Historias de usuario | 10 de 10 implementadas |
| Tests | **186 backend + 78 frontend = 264** |
| Linters | `ruff` y `tsc --noEmit` limpios |
| Despliegue | Público, con HTTPS y control de acceso |

## Una nota sobre el método

La deuda conocida se **declara**, no se esconde: hay una tabla con lo que no está resuelto, por qué y
cuándo se abordará. Incluye cosas incómodas, como que la verificación de la Entrega 2 la hiciera la
misma sesión que implementó, en contra del estándar propio del proyecto.

Un producto que dice dónde falla es más fiable que uno que solo enseña lo que funciona.
