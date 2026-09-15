# Chispa ✨ — Entrega 1 · Producto

**Documento:** PRD (Product Requirements Document)
**Proyecto:** Chispa (aprendizaje por curiosidad para niños)
**Alumno:** Germán González Pérez · **Máster:** LIDR – AI4Devs
**Repositorio:** github.com/ggonzalezperez/chispa (privado) · **Entrega 1:** 22 de julio de 2026

> Documentos relacionados: [Problema y usuarios](problema-y-usuarios.md) · [Alcance](alcance.md) · [Historias de usuario](historias-usuario.md)

---

## 1. Visión del producto

> «Chispa ayuda a los niños a aprender desde su curiosidad, convirtiendo cada pregunta en una pequeña aventura de conocimiento adaptada a su edad, segura para la familia y acumulada en su propio mapa de aprendizaje.»

> Chispa convierte la curiosidad espontánea de un niño en micro-aprendizaje adaptado por edad, seguro y supervisado por su familia; cada tema explorado se vuelve una **isla** de un **archipiélago** de conocimiento que el niño construye visualmente. La app es autoalojable, funciona **gratis en modo demo** y admite IA multiproveedor por familia con **degradación elegante**.

El contexto completo del problema, los usuarios y los objetivos está en [Problema y usuarios](problema-y-usuarios.md). Este PRD define **qué** debe hacer el producto (funcional y no funcional) y con qué criterios se considera correcto.

### 1.1 Promesa diferencial: tres mundos que se necesitan

Chispa nace de combinar tres "mundos" que, por separado, fallan; el producto se diseña para que se sostengan mutuamente:

| Mundo | Qué aporta | Riesgo si va solo | Cómo lo resuelve Chispa |
|---|---|---|---|
| Curiosidad libre | Motivación intrínseca | Entretenimiento superficial | Cada curiosidad se conecta con una habilidad concreta |
| Progreso educativo | Estructura y mejora visible | Parecer "colegio disfrazado" | La materia entra como soporte de la pregunta, no como imposición |
| Memoria personalizada | Continuidad y adaptación | Vigilancia o perfilado excesivo | Ficha visible para padres, minimización de datos y control familiar |

### 1.2 Principios de producto no negociables

Estos principios acotan las decisiones de diseño y de implementación; cualquier requisito de este PRD debe ser compatible con ellos:

1. **Curiosidad primero, currículo después.** El punto de partida es la pregunta del niño; la materia entra como soporte, no como temario impuesto.
2. **Seguridad infantil por diseño.** Moderación de entrada, aprobación parental de cuentos y aislamiento de datos son parte del núcleo, no añadidos.
3. **La ficha manda.** Ninguna interacción importante depende **solo** del prompt momentáneo: el sistema **lee y escribe** en la ficha/grafo del niño para decidir y personalizar.
4. **Texto canónico.** Voz, imagen y cuentos son **capas enriquecidas**; la base de todo contenido queda siempre en texto (verificable y degradable al stub).
5. **Progreso sin manipulación.** Sin scroll infinito, sin recompensas adictivas, sin publicidad, sin presión de rachas ni *dark patterns*.
6. **Aprendizaje corto y recordable.** Lecciones breves, con una idea y un dato memorable, pensadas para volver a ellas.
7. **Padres con control, niño con agencia.** La familia supervisa y aprueba; el niño explora y crea con autonomía real.
8. **Diseño incremental.** Primero un **flujo E2E sólido** (curiosidad → lección → reto → ficha), después la expansión en features.

### 1.3 El motor pedagógico

> **«La IA puede redactar, pero el sistema decide el contrato pedagógico.»**

Como principio de diseño de producto, la generación de lenguaje (texto, y sobre él voz e imagen) es una capa **redactora**: la IA propone la forma. Las decisiones pedagógicas —qué concepto se trabaja, qué banda de edad aplica, qué estructura tiene la lección (idea + dato + follow-ups), qué cuenta como acierto en el reto y cómo evoluciona la maestría— las fija el **sistema**, no el prompt. Esto es lo que hace el comportamiento **verificable** y coherente con la degradación elegante: el stub determinista respeta el mismo contrato que un proveedor real.

### 1.4 La Ficha de Conocimiento del Niño

La **Ficha de Conocimiento del Niño** es el concepto central de personalización de Chispa: su **memoria pedagógica** y la fuente desde la que se adapta la experiencia. Es **visible para los padres** (conceptos fuertes / emergentes, actividad, recorrido) y **utilizable por la IA** como contexto, pero **sin exponer al niño** a análisis fríos de rendimiento ni a un lenguaje de evaluación.

En el diseño actual, la Ficha **no es una entidad nueva**: es una **vista/derivada** sobre el modelo de datos existente. Se materializa a partir del **grafo de conocimiento** del niño —el **"archipiélago"**, esto es, sus nodos de conocimiento (`knowledge_nodes`) con su maestría— combinado con el **perfil del niño** (banda de edad, idioma, actividad). El panel de familia expone esta Ficha sobre los endpoints `/me/*`; ninguna funcionalidad de este PRD introduce tablas o entidades adicionales para sostenerla.

---

## 2. Actores y sesiones

| Actor | Autenticación | Tipo de token JWT | Puede |
|---|---|---|---|
| **Familia / Adulto** ("tripulación") | email + contraseña | `family` | Gestionar cuenta y perfiles, supervisar, aprobar cuentos, configurar IA |
| **Explorador / Niño** | PIN de 4 dígitos (dentro de la familia) | `child` | Encender chispas, ver lecciones, resolver retos, explorar islas, chatear, crear cuentos |

**Regla de seguridad transversal:** un token `child` deberá ser rechazado (401) en los endpoints de familia y un token `family` deberá ser rechazado (401) en los endpoints de niño. Cada niño accederá únicamente a sus propios datos; el aislamiento entre familias deberá ser estricto (los accesos cruzados devolverán 404).

---

## 3. Épicas y alcance funcional

Las 11 historias principales (US1–US11) se agrupan en **6 épicas** priorizadas. El detalle con criterios de aceptación en Gherkin y trazabilidad está en [Historias de usuario](historias-usuario.md).

| Épica | Historias | Descripción |
|---|---|---|
| **E1 · Onboarding y perfiles** | US1 | Cuenta familiar, perfiles de niño con PIN y avatares, recuperación de contraseña por código |
| **E2 · Bucle de aprendizaje** | US2, US3, US4 | Encender la chispa, mini-lección adaptada por edad + lectura, reto/quiz que sube maestría |
| **E3 · Conocimiento vivo** | US7, US8 | Archipiélago + buscador, chat con contexto e islas automáticas |
| **E4 · Cuentos** | US9 | Biblioteca de cuentos con aprobación parental |
| **E5 · IA configurable** | US10 | IA multiproveedor (texto + imagen) por familia, clave cifrada, recomendador por hardware |
| **E6 · Plataforma y accesibilidad** | US5/US6, US11 | Panel de familia, voz, imágenes IA, QR/LAN, i18n es/en |

**Prioridad de construcción:** núcleo E1–E4 primero (bucle de valor completo), luego E5 y E6. Ver justificación en [alcance](alcance.md#5-priorización-y-recortes).

---

## 4. Requisitos funcionales

Los requisitos funcionales se especifican **uno a uno, en formato tabular** (ID, módulo, entradas, salidas, criterios de aceptación GWT, reglas de negocio, prioridad, dependencias y riesgos) y **trazados a su HU** en el documento [**Requisitos (RF/RNF) y trazabilidad**](requisitos.md). Los criterios de aceptación formales (Gherkin) viven en [Historias de usuario](historias-usuario.md).

Resumen por módulo:

| Módulo | Requisitos | Épica · HU |
|---|---|---|
| **ONB** — Onboarding y perfiles | RF-ONB-01 … RF-ONB-05 | E1 · US1 |
| **APR** — Bucle de aprendizaje | RF-APR-01 … RF-APR-05 | E2 · US2–US4 |
| **CON** — Conocimiento vivo | RF-CON-01 … RF-CON-05 | E3 · US7–US8 |
| **CUE** — Cuentos | RF-CUE-01 … RF-CUE-03 | E4 · US9 |
| **IA** — IA configurable | RF-IA-01 … RF-IA-06 | E5 · US10 |
| **PLT** — Plataforma y accesibilidad | RF-PLT-01 … RF-PLT-05 | E6 · US5/US6, US11 |
| **SEG** — Seguridad (transversal) | RF-SEG-01 … RF-SEG-03 | Transversal |

El detalle de cada RF y la **matriz de trazabilidad HU ↔ RF** (que sirve también como base para el diseño de pruebas funcionales) están en [requisitos.md](requisitos.md).

---

## 5. Requisitos no funcionales

Los RNF se especifican **en formato tabular con criterio de verificación** (RNF-01…RNF-10) en [requisitos.md](requisitos.md). Resumen:

| # | Categoría | En una frase |
|---|---|---|
| **RNF-01** | Seguridad del menor | Moderación + *fallback seguro* 🛟; el backend nunca envía la respuesta del quiz; aprobación parental. |
| **RNF-02** | Seguridad técnica | JWT tipado con rechazo cruzado (401), claves de IA cifradas (Fernet), SSRF mitigado, aislamiento por niño/familia (404). |
| **RNF-03** | Privacidad | Sin datos del menor en el alta; recuperación por código, **sin servicio de email**. |
| **RNF-04** | Fiabilidad / degradación elegante | Sin proveedor o ante fallo, caída al **stub** determinista; el niño nunca ve un error. |
| **RNF-05** | Accesibilidad | Táctil y grande; voz (dictado + lectura); contraste y tipografías legibles; *reduced-motion*. |
| **RNF-06** | Responsive / multidispositivo | Móvil, tablet y PC; acceso LAN con QR. |
| **RNF-07** | Rendimiento percibido | El stub responde inmediato y determinista, sin dependencia de red externa. |
| **RNF-08** | Portabilidad / despliegue | Autoalojable con Docker; SQLite en dev; migraciones Alembic siempre aditivas. |
| **RNF-09** | Calidad y mantenibilidad | Suite pytest / Vitest, lint (ruff / `tsc --noEmit`), CI en GitHub Actions. |
| **RNF-10** | Internacionalización | Interfaz es/en; lectura y dictado por voz en el idioma activo. |

---

## 6. Experiencia y dirección visual

Dirección **"Archipiélago"** (náutica): coral `#ff7a59` (CTA/activo) + teal `#0e837b` (océano), fondo papel cálido `#e8e6e1`, tipografías **Fredoka** (títulos/CTA) y **Mulish** (cuerpo del niño), **Nunito** en el panel adulto. Esquinas muy redondeadas, gradientes de océano en el mundo del niño, avatares emoji en círculo con anillo coral, PIN de 4 puntos y teclado numérico, recompensa en **conchas 🐚**. Edad foco de diseño: **6–8 años**. Detalle completo en `docs/design-system.md`.

Flujo principal de pantallas: Bienvenida → Crear cuenta familiar → Añadir explorador → ¿Quién explora? → Acceso del niño (PIN) → **Encender la chispa** → **Mini-lección** (🔊) → **Reto** → **Mis conocimientos** (archipiélago). Panel adulto (desktop): Resumen · Historial · Ficha del niño · Seguridad · Cuentos.

---

## 7. Supuestos y dependencias

- La **voz** depende del soporte del navegador (Web Speech API / Synthesis); si no existe, se degrada ocultando los controles.
- La **IA real** (texto/imagen) depende de que el operador aporte clave o levante modelos locales; por defecto todo funciona en demo.
- El **acceso LAN + QR** asume que los dispositivos están en la misma red WiFi y que el operador configura `VITE_API_URL`/`CORS_ORIGINS`.
- No hay servicio de email; la recuperación de contraseña se resuelve con el código `XXXX-XXXX`.

---

## 8. Métricas de éxito (cualitativas)

Al ser un proyecto académico sin datos de uso reales, el éxito se evaluará de forma **cualitativa** y por **cobertura de criterios de aceptación**. Se considerará logrado cuando:

- El **bucle completo** (curiosidad → lección → reto → isla) funcione de extremo a extremo y adaptado por edad.
- El **control parental** (moderación, aprobación de cuentos, aislamiento) se cumpla y quede cubierto por pruebas.
- La **degradación elegante** sea verificable: sin ninguna clave, la app deberá ser plenamente usable.
- La **accesibilidad** (voz, i18n, responsive, LAN+QR) esté presente y prevista su validación.
- Todas las historias US1–US11 cuenten con criterios de aceptación cumplidos y con su trazabilidad prevista a pantalla + endpoint + prueba (ver [historias de usuario](historias-usuario.md)).

> Nota: no se comprometen cifras cuantitativas de adopción o retención por tratarse de una entrega documental sin despliegue público con usuarios reales.

---

## 9. Fuera de alcance

Resumen (detalle en [alcance](alcance.md#4-fuera-de-alcance--futuro)) de lo que **no se construirá** en esta entrega: activación de imágenes reales por el operador, efectos de sonido/vídeo generados por IA, proveedores de texto Gemini/DeepSeek/Kimi (previstos pero no habilitados; OpenAI sí se habilitó en implementación), servicio de email, y el tier comercial "managed" (cuota + facturación).
