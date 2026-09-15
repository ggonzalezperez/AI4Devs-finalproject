# Chispa ✨ — Entrega 1 · Producto

**Documento:** Problema y usuarios
**Proyecto:** Chispa (aprendizaje por curiosidad para niños)
**Alumno:** Germán González Pérez · **Máster:** LIDR – AI4Devs
**Repositorio:** github.com/ggonzalezperez/chispa (privado) · **Entrega 1:** 22 de julio de 2026

> Documentos relacionados: [PRD](prd.md) · [Alcance](alcance.md) · [Historias de usuario](historias-usuario.md)

---

## 1. Resumen ejecutivo

**Chispa** será una aplicación web responsive (móvil / tablet / PC) que convertirá la **curiosidad espontánea de un niño** en **micro-aprendizaje adaptado a su edad**, dentro de un espacio seguro y supervisado por la familia. El niño "encenderá una chispa" (formulará una pregunta, escrita o dictada), recibirá una **mini-lección** ajustada a su banda de edad, opcionalmente resolverá un **reto (quiz)**, y cada tema explorado se convertirá en una **isla** de su **grafo de conocimiento** ("archipiélago"), que podrá reabrir para seguir profundizando en una conversación tipo chat.

La aplicación se diseña para ser **autoalojable** y **gratuita en modo demo**: sin ningún proveedor de IA configurado, todo funcionará con contenido determinista de demostración, sin coste ni errores para el niño. Cuando la familia lo desee, podrá enchufar un proveedor de IA (texto e imagen) con su propia clave, que se guardará **cifrada**.

---

## 2. El problema

La curiosidad infantil es el motor natural del aprendizaje, pero hoy choca con tres barreras:

1. **Pantallas pasivas.** La mayor parte del consumo digital infantil es pasivo (vídeo en bucle, scroll), no dialógico. La pregunta del niño —"¿por qué el cielo es azul?"— rara vez encuentra una respuesta a su medida en el momento en que surge.
2. **Contenido no adaptado a la edad.** Los buscadores y asistentes generalistas devuelven respuestas pensadas para adultos: demasiado densas, con vocabulario inaccesible o, peor, con material inadecuado para un menor.
3. **Falta de supervisión y visibilidad parental.** Los padres no tienen un espacio donde ver qué está explorando su hijo, moderar la entrada, ni aprobar el contenido que consume o crea.

### Impacto del problema

| Consecuencia | Descripción |
|---|---|
| Oportunidades de aprendizaje perdidas | La pregunta se queda sin respuesta útil en el instante de máxima motivación (la curiosidad se enfría). |
| Exposición a contenido inadecuado | Sin filtro por edad ni moderación, el menor puede toparse con material inapropiado. |
| Falta de visibilidad de los padres | No hay panel que muestre intereses, progreso o alertas; la familia queda fuera del bucle. |
| Aprendizaje no acumulativo | Lo explorado no se estructura ni se puede retomar; no hay memoria del recorrido. |

### Por qué ahora

La combinación de **LLMs asequibles**, **APIs de voz nativas del navegador** (dictado y lectura, sin servidor) y **modelos de imagen gratuitos o locales** hace por primera vez viable —y a coste cero en modo demo— un tutor de curiosidad seguro, adaptado por edad y controlable por la familia, sin depender de una gran plataforma comercial.

---

## 3. Propuesta de valor

> **Transformar cualquier pregunta espontánea de un niño en aprendizaje seguro, personalizado por edad y visible para la familia.**

Chispa se diferencia por cuatro pilares:

1. **Bucle de curiosidad, no catálogo cerrado.** El contenido nace de la pregunta del niño (o de sugerencias), no de un temario fijo: curiosidad → lección → reto → isla.
2. **Adaptación real por edad.** Tres bandas (3–5 / 6–8 / 9–12) modulan longitud, vocabulario, analogías y follow-ups. Edad foco de diseño: **6–8 años**.
3. **Control parental de verdad.** Moderación de la entrada del niño, aprobación parental de los cuentos, aislamiento estricto de datos entre familias y panel de supervisión.
4. **IA opcional, privada y con degradación elegante.** Multiproveedor por familia, claves cifradas (Fernet), y **fallback al stub**: el niño nunca ve un fallo del proveedor y la app funciona gratis sin configurar nada.

### Concepto: un espacio personal de descubrimiento

Chispa **no** se plantea como una app de fichas ni como una academia infantil, sino como un **espacio personal de descubrimiento**: un lugar donde cada niño construirá su propio **mapa de conocimiento** a partir de sus preguntas, de lecciones cortas, de retos, de recuerdos y de lo que cree. La tesis del producto es la **curiosidad guiada con memoria pedagógica**, no un catálogo de contenidos: lo que da valor no es "qué contenido servimos", sino "cómo acompañamos y recordamos el recorrido del niño". Todo lo que se propone en este documento —bandas de edad, control parental, archipiélago, ficha— existe para sostener esa idea.

### Línea roja de producto (lo que Chispa no debe ser)

Para preservar el concepto anterior, se fija de forma explícita lo que Chispa **no** debe llegar a ser, ni siquiera por acumulación de features:

- Una **app de deberes** o de tareas escolares.
- Un **chatbot libre** para niños (sin marco pedagógico ni moderación).
- Una **enciclopedia con IA** (respuestas frías, sin adaptación ni memoria).
- **Entretenimiento disfrazado de educativo** (enganche por encima del aprendizaje).
- Una herramienta de **vigilancia del menor** (el panel familiar da confianza, no control invasivo).
- Un producto **dependiente de prompts no testeables** (el comportamiento debe poder verificarse).
- Un **MVP de features sueltas** sin un flujo central sólido que las conecte.

### Metáfora de producto: "Archipiélago"

Cada concepto aprendido es una **isla**; el conjunto de islas conectadas forma el **archipiélago** del niño. La familia es la **tripulación** y el niño, el **explorador**. Esta metáfora náutica (coral `#ff7a59` + teal `#0e837b`, tipografías Fredoka/Mulish) da coherencia visual y hace tangible el progreso: el mapa crece a medida que el niño explora.

---

## 4. Usuarios y actores

Chispa contará con **dos actores** con sesiones y permisos separados (JWT tipado). Un token de un tipo deberá ser rechazado en los endpoints del otro (401).

### 4.1 Familia / Adulto ("tripulación")

- **Autenticación:** email + contraseña (registro/login), sesión JWT de tipo `family`.
- **Rol:** administra la cuenta, crea y gestiona los perfiles de los niños, supervisa la actividad, modera y **aprueba/edita/rechaza** los cuentos, y configura la IA de la familia (texto e imagen).
- **Motivaciones:** que su hijo aprenda de forma segura y adaptada; tener visibilidad sin fricción; mantener el control del contenido y de la privacidad (claves y datos del menor).
- **Frustraciones que resuelve:** no saber qué consume el niño; miedo a contenido inadecuado; complejidad técnica (Chispa es autoalojable pero funciona en modo demo sin configurar nada).
- **Lo que la familia necesita, en una frase:** como compradora y supervisora del producto, la familia necesita **confianza, control y claridad**: entender qué aprende el niño, qué explora, qué límites hay y qué se guarda. El objetivo de diseño es dárselo sin convertir la supervisión en vigilancia.

### 4.2 Explorador / Niño

- **Autenticación:** perfil con **PIN de 4 dígitos** dentro de la familia; sesión JWT de tipo `child`.
- **Rol:** formula curiosidades (escritas o dictadas), consume mini-lecciones, resuelve retos, explora su archipiélago, sigue preguntando en el chat y crea cuentos (que la familia debe aprobar).
- **Motivaciones:** satisfacer su curiosidad de inmediato; ver crecer su mapa de islas y coleccionar conchas 🐚; sentir autonomía dentro de un entorno seguro.
- **Necesidades de accesibilidad:** interfaz táctil y grande, voz (dictar la pregunta 🎤 y escuchar la lección 🔊), lenguaje a su medida, idioma es/en.
- **Postura de diseño (usuario principal):** el niño es el usuario central. No entra a "hacer deberes", entra a **descubrir**, y debe sentir que la app **le pertenece**: suyas son sus preguntas, sus mundos, sus descubrimientos, sus cuentos, sus imágenes y su mapa. Chispa busca darle **agencia real dentro de un entorno seguro**, no colocarlo ante una tarea impuesta.

### 4.3 Actor de soporte: Operador / Autoalojador

No es un usuario de la interfaz de aprendizaje, pero es relevante para el alcance: quien desplegará Chispa (Docker) y, opcionalmente, **activará la IA real** pegando una clave (p. ej. token gratuito de HuggingFace) o levantando modelos locales (Ollama, SDXL). Sin su intervención, la app deberá permanecer plenamente funcional en **modo demo**.

### 4.4 Usuario futuro (fuera de alcance inicial): docente / aula

El **docente** y el uso en **aula** se reconocen como un usuario **futuro**, **no** como foco del MVP. Podría materializarse más adelante como un **"modo aula"**, pero se deja fuera de esta entrega de forma explícita para evitar la complejidad de la gestión escolar (grupos, matrículas, roles docentes, informes por clase). El diseño actual se centra en el binomio **niño ↔ familia**; cualquier capacidad de aula se abordaría como una extensión posterior sin comprometer el núcleo.

### 4.5 Mapa de vocabulario (diseño ↔ dominio)

| Término de producto/diseño | Concepto técnico |
|---|---|
| Tripulación | Familia (cuenta) |
| Explorador | Niño (perfil con PIN) |
| Isla | Nodo del grafo de conocimiento (`KnowledgeNode`) |
| Archipiélago | Grafo de conocimiento del niño |
| Encender la chispa | Crear una curiosidad → lección raíz (US2) |
| Conchas 🐚 | Moneda / recompensa visual |

---

## 5. Escenarios de uso (historias de contexto)

- **Leo (7 años), tarde de sábado.** Pregunta "¿por qué los volcanes echan fuego?". Chispa le da una mini-lección con una analogía y un dato sorprendente, se la lee en voz alta, y le propone un reto de 3 opciones. Al terminar, aparece una nueva isla "Volcanes" en su archipiélago. Sigue preguntando "¿y el más grande del mundo?" en el mismo hilo.
- **María (madre), esa misma noche.** Abre el panel de familia en el portátil: ve que Leo exploró volcanes y planetas esta semana, revisa su ficha (fuertes/emergentes) y aprueba un cuento que Leo escribió sobre un dragón, corrigiéndole una frase antes de publicarlo.
- **Familia sin configurar nada.** Instalan Chispa con Docker y la usan tal cual: las lecciones salen del stub determinista, sin coste ni claves. Más adelante pegan un token gratuito de HuggingFace y, a partir de ese momento, las lecciones y avatares salen con imágenes.

---

## 6. Objetivos del producto

| # | Objetivo | Cómo se materializa |
|---|---|---|
| O1 | Bucle curiosidad → lección → reto → isla, funcional y adaptado por edad | US2, US3, US4 (bandas 3–5 / 6–8 / 9–12) |
| O2 | Supervisión y control parental reales | US5/US6 (panel), US9 (aprobación de cuentos), moderación de entrada, aislamiento de datos |
| O3 | IA opcional multiproveedor con privacidad y degradación a demo | US10 (claves cifradas Fernet, fallback al stub, recomendador por hardware) |
| O4 | Accesibilidad e inclusión | US11 (voz, i18n es/en, responsive/táctil, LAN + QR) |

Estos objetivos se detallan y priorizan en el [PRD](prd.md) y se acotan en el documento de [alcance](alcance.md).

---

## 7. Principio transversal: degradación elegante

Todo el sistema se diseñará para que **la ausencia de configuración nunca produzca un error visible al niño**. Si no hay proveedor de IA configurado (o falla), el generador caerá al **stub** determinista; si la imagen está desactivada, se usarán avatares SVG diseñados; si la voz no está soportada por el navegador, los botones simplemente no se mostrarán. Este principio es la base de la propuesta "gratis y sin fricción" y condicionará buena parte de los criterios de aceptación (ver [historias de usuario](historias-usuario.md)).

---

## 8. Norte del proyecto

Toda decisión de producto se contrastará con una única frase que resume el resultado que Chispa persigue para el niño:

> «Que un niño pueda preguntar algo que le importa, entenderlo un poco mejor, recordarlo, conectarlo con otras ideas y sentir que su mundo de conocimiento ha crecido.»

Si una funcionalidad no contribuye a ese recorrido —preguntar, entender, recordar, conectar, crecer—, es candidata a quedar fuera del núcleo (ver [alcance](alcance.md)).
