# Chispa — Sistema de diseño ("Archipiélago")

> Extraído del diseño elegido por el usuario en claude.ai/design
> (proyecto "Chispa: Vision Global y Diseño Atomizado", archivo `Chispa - Archipielago.dc.html`).
> Dirección visual: **Archipiélago / explorador**. Edad foco: **6–8 años**.
> Metáfora central: cada concepto aprendido = una **isla**; el niño construye su **archipiélago**.

## Tipografías (Google Fonts)

- **Fredoka** — títulos y CTAs (playful). Pesos 400–700.
- **Mulish** — cuerpo en pantallas de niño. 400–800.
- **Nunito** — sans general / panel adulto. 400–800.
- **Space Grotesk** — etiquetas tipo "mono" (overlines en mayúsculas). 500–700.
- (También cargadas: Baloo 2, Quicksand.)

## Paleta

| Rol | Hex |
|-----|-----|
| Fondo página (papel cálido) | `#e8e6e1` |
| Océano/teal primario | `#0e837b` |
| Teal oscuro (texto principal) | `#08433e` |
| Teal medio / sidebar | `#0e5b56` |
| Teal claro / gradientes | `#4cc0b6`, `#7fd0c7`, `#aeeae3`, `#b6ebe4` |
| **Coral (CTA / activo)** | `#ff7a59` |
| Oro/ámbar (islas, highlights) | `#ffc24d`, `#f4a93c`, `#ffd76a` |
| Crema (tarjetas/superficies) | `#fbf3e0`, `#fbf7ee`, `#fff` |
| Verde "dominado" (mastery fuerte) | `#2aa06a` / fondo `#e6f7ee` |
| Ámbar "emergente" | `#e0892f` / fondo `#fff1d6` |
| Grises de apoyo | `#6b6760`, `#8a8780`, `#7aa6a0`, `#6f9690` |

## Convenciones de UI

- **Marco móvil:** tarjetas de pantalla `320×700`, `border-radius: 36px`, sombra suave grande.
- **Panel adulto (desktop):** `760` de ancho, `border-radius: 24px`, sidebar teal `#0e5b56`.
- Esquinas muy redondeadas (16–22px en tarjetas internas), sombras suaves, **gradientes de océano** en fondos de niño.
- **Botón principal:** coral `#ff7a59`, texto blanco, Fredoka, radio 16–18px, sombra coral.
- **Avatares:** emoji (🦊🐢🦉) en círculo blanco; selección con anillo coral.
- **PIN:** 4 puntos; rellenos en coral. Teclado numérico 3×4 (tecla 0 en coral, ⌫).
- Moneda/recompensa: **conchas** "🐚 24".
- Overline: Space Grotesk, 11–12px, mayúsculas, `letter-spacing ~.05em`, color gris/teal.

## Inventario de pantallas (orden del flujo E2E)

**① Onboarding (adulto)**
1. Crear cuenta familiar (nombre, email, contraseña → "Crear cuenta"). Nota: "Sin datos del menor".
2. Añadir explorador (avatar, alias, **fecha de nacimiento → badge "7 años"**, **PIN** de 4).
3. ¿Quién va a explorar? (lista de la "tripulación": avatar, alias, "7 años · 12 islas", + añadir).

**② Mundo del niño**
1. Acceso del niño (avatar grande, "¡Hola, Leo!", 4 puntos PIN, teclado numérico, "¿No eres Leo? Cambiar").
2. **Encender la chispa** (saludo + conchas; "¿Qué quieres descubrir hoy?"; input con 🧭 + **🎤 voz**; "Islas para empezar…" sugerencias; tarjeta "Volver a tu travesía" con progreso).
3. **Mini-lección** (header materia+edad; ilustración; título; párrafo corto; "💡 Dato sorprendente"; **reproductor de audio**; CTA "¡A jugar! →").
4. **Reto rápido (quiz)** (progreso 2/3 con barras; pregunta; opciones A/B/C; estado correcto resaltado; feedback "🎉 ¡Muy bien!"; "Siguiente →").
5. **Mis conocimientos** ("El archipiélago de Leo 🗺️"; **mapa SVG de islas** conectadas por rutas punteadas; tamaño de isla = dominio; tarjeta de detalle de isla con "Explorar →").

**③ Panel adulto (desktop)**
- Sidebar: Resumen · Historial · Ficha del niño · Seguridad · **Cuentos (badge)**; selector de niño abajo.
- Resumen: "Esta semana con Leo"; selector Leo/Mía; 3 stats (Curiosidades, Conceptos nuevos, Quizzes %).
- Historial reciente (curiosidad · materia · fecha · aciertos).
- **Ficha de conocimiento** (FUERTES / EMERGENTES como chips de colores).
- **Cuento pendiente** con acciones **Aprobar / Revisar** (aprobación parental, D17).

**④ Estados y casos especiales**
- Fallback seguro ("Esta la vemos con un adulto" — 🛟) cuando la pregunta no es apropiada.
- Pista en el reto.
- Detalle de una isla.
- Revisión de un cuento por el adulto.

## Mapeo diseño → spec/arquitectura

- "Tripulación" = familia · "explorador" = niño · "isla" = nodo del grafo de conocimiento.
- "Encender la chispa" = US2 (curiosidad) · "Mini-lección" = US3 · "Reto" = US4 (quiz).
- "Mis conocimientos / archipiélago" = US7 (vista del grafo del niño).
- "Panel de familia" = US5/US6 (ficha, seguridad, **aprobación de cuentos**).
- Fallback seguro = moderación de entrada (D6).
