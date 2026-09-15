# Chispa ✨ — Entrega 1 · Producto

**Documento:** Alcance
**Proyecto:** Chispa (aprendizaje por curiosidad para niños)
**Alumno:** Germán González Pérez · **Máster:** LIDR – AI4Devs
**Repositorio:** github.com/ggonzalezperez/chispa (privado) · **Entrega 1:** 22 de julio de 2026

> Documentos relacionados: [Problema y usuarios](problema-y-usuarios.md) · [PRD](prd.md) · [Historias de usuario](historias-usuario.md)

---

## 1. Objetivo del documento

Delimitar de forma explícita **qué entra** y **qué queda fuera** del producto Chispa para esta entrega, así como los **riesgos, supuestos** y la **estrategia de priorización/recorte** que garantizará que el núcleo de valor se entregue aunque haya que reducir alcance.

---

## 2. Dentro de alcance

> **Núcleo del producto.** El **flujo central** *curiosidad → lección → reto → ficha/grafo* es el eje que da sentido a todo lo demás, y se rige por el principio **"curiosidad primero, currículo después"**: la materia entra como soporte de la pregunta del niño, no como temario impuesto. La **Ficha del niño** —vista derivada del **archipiélago** (nodos de conocimiento con su maestría) y del perfil del niño, sin entidades nuevas— es el **centro de la personalización**. Todo lo que sigue en este alcance se prioriza por su contribución a ese núcleo (ver [PRD §1.2–1.4](prd.md#12-principios-de-producto-no-negociables)).

### 2.1 Familia, perfiles y seguridad de acceso (E1)

- Cuenta de familia (registro/login con JWT `family`).
- Perfiles de niño con **PIN de 4 dígitos**, alias, fecha de nacimiento → edad calculada, y **avatares** (SVG diseñados o generados por IA).
- Sesiones de familia y de niño **separadas y tipadas** (rechazo cruzado 401).
- **Cambio de contraseña** (autenticado) y **recuperación** mediante **código** `XXXX-XXXX`, **sin servicio de email**.

### 2.2 Bucle de aprendizaje adaptado por edad (E2)

- Encender la chispa: curiosidad (escrita o dictada) → **mini-lección**.
- Lección **adaptada a la banda de edad** (3–5 / 6–8 / 9–12): una idea, analogía, dato sorprendente, 2–3 follow-ups.
- **Reto (quiz)** de 3 opciones; acertar sube la **maestría** del nodo; fallar no penaliza.
- **Lectura en voz alta** de la lección (🔊, Web Speech Synthesis).

### 2.3 Conocimiento vivo: archipiélago y chat (E3)

- **Islas** creadas automáticamente al generar una lección.
- **Buscador** del archipiélago (insensible a acentos y mayúsculas).
- **Chat con contexto**: seguir preguntando en el mismo hilo; hilo ordenado (raíz primero); reabrir la conversación guardada de una isla.

### 2.4 Cuentos con aprobación parental (E4)

- El niño crea cuentos (quedan **pendientes**).
- La familia **aprueba/edita/rechaza**; el rechazo conserva el texto original; aislamiento entre familias.

### 2.5 IA multiproveedor por familia (E5)

- **Texto:** `stub` (demo), **Ollama** (local), **Claude** y **OpenAI** habilitados; Gemini/DeepSeek/Kimi **previstos pero no habilitados** en esta entrega.

  > **Corregido en implementación (15-09-2026):** OpenAI se habilitó al comprobar que su adaptador (`OpenAICompatGenerator`) ya existía y estaba cableado; solo un flag del catálogo lo ocultaba.
- **Imagen:** HuggingFace (FLUX.1-schnell), SDXL local (Automatic1111), OpenAI (gpt-image-1-mini), Gemini (gemini-3.1-flash-image), **Pollinations** (sin clave). Ollama no genera imágenes.
- Claves **cifradas (Fernet)**, nunca devueltas al cliente.
- **Recomendador de modelo local por hardware** (VRAM/RAM).

### 2.6 Plataforma y accesibilidad (E6)

- **Panel de familia**: actividad, historial, ficha (fuertes/emergentes), selector de niño, seguridad.
- **Voz**: dictado (🎤) y lectura (🔊) con APIs nativas del navegador (multiidioma; si no hay soporte, se ocultan).
- **Imágenes IA** en lecciones y avatares (**off por defecto**).
- **i18n es/en** (detecta el navegador, el usuario puede cambiar).
- **Responsive y táctil**; **acceso LAN + QR** ("Conectar móvil").
- **Docker** (Postgres + backend + frontend + Ollama), autoalojable.

---

## 3. En el límite (incluido pero condicionado)

| Elemento | Condición |
|---|---|
| Imágenes reales en lecciones/avatares | Previstas para **activarse** cuando el operador pegue un token (p. ej. HuggingFace gratis) o levante SDXL local. Por defecto: avatares SVG. |
| IA de texto real (Claude/Ollama) | Prevista; por defecto se usará el **stub** determinista sin coste. |
| Acceso LAN + QR | Requerirá que el operador configure `VITE_API_URL` y `CORS_ORIGINS` y que los dispositivos compartan red WiFi. |

---

## 4. Fuera de alcance / futuro

| Elemento | Motivo / estado |
|---|---|
| Activación de imágenes reales "llave en mano" | No se construirá: dependerá del **operador** (pegar token HuggingFace o levantar SDXL); no se distribuirán claves. |
| Efectos de **sonido/vídeo** generados por IA | No se construirá ahora; futuro: cuando exista un modelo de audio/vídeo integrable. |
| Proveedores de texto **Gemini / DeepSeek / Kimi** | **Previstos pero no habilitados** en esta entrega; no se construirán ahora. (OpenAI sí se habilitó, ver §3.) |
| **Servicio de email** (verificación, recuperación por correo) | No se construirá: la recuperación se resolverá **por código** `XXXX-XXXX`. |
| Tier comercial **"managed"** (cuota + facturación) | **Previsto pero no activo**; solo `free` con `stub`/BYOK. |
| App móvil nativa / tiendas | No aplica: Chispa será una web responsive autoalojable. |
| Analítica de uso / telemetría con usuarios reales | No aplica en una entrega documental sin despliegue público. |

---

## 5. Priorización y recortes

**Orden de construcción por valor:** el **núcleo E1–E4** (onboarding, bucle de aprendizaje, conocimiento vivo y cuentos) se priorizará porque entrega el bucle de valor completo. E5 (IA configurable) y E6 (plataforma/accesibilidad) se construirán después.

**Historias opcionales (según la guía §13.7).** Por decisión de alcance, las 11 historias se plantean como
principales; no obstante, se identifican formalmente **dos historias opcionales** de bajo riesgo que, de
faltar tiempo, podrían diferirse sin romper el núcleo:

- **OPT-01 — Imágenes IA** (lecciones/avatares): la app funcionará con avatares SVG y sin ilustraciones generadas.
- **OPT-02 — QR / acceso LAN**: útil pero prescindible; la app funcionará en un único dispositivo.

Diferir cualquiera de estas dos no rompería el bucle curiosidad → lección → reto → isla ni el control parental.

---

## 6. Riesgos y supuestos

| Riesgo / supuesto | Impacto | Mitigación |
|---|---|---|
| **Alucinaciones de la IA** | Contenido incorrecto o inadecuado para el niño | Validación de salida + **fallback al stub** determinista; moderación de entrada |
| **Alcance excesivo** para el tiempo disponible | No terminar el núcleo | **Épicas priorizadas** (E1–E4 primero); historias opcionales identificadas para recorte |
| **Dependencia de proveedores externos** (APIs de IA) | Fallos, latencia o coste | **Degradación elegante**: caída al stub; el niño nunca ve un error del proveedor |
| **Seguridad del menor** | Exposición a contenido inadecuado | Moderación de la entrada + **aislamiento de datos** + **aprobación parental** de cuentos + backend nunca revela la respuesta del quiz |
| **Falta de tiempo** | Entrega incompleta | Construir el **núcleo E1–E4** antes que E5/E6 |
| Soporte de **voz** dispar entre navegadores | Botones de voz sin efecto | Detección de soporte: si no existe, **se ocultan** los controles |
| Configuración de **red LAN/CORS** por el operador | Acceso desde móvil no funciona | Documentación en `docs/MANUAL.md` + pantalla QR con `window.location.origin` |
| Gestión de **claves de IA** | Fuga de credenciales | Cifrado **Fernet**; las claves **nunca** se devuelven al cliente |

---

## 7. Criterios de "terminado" para la entrega

Para dar la entrega por terminada, deberá cumplirse:

- Historias US1–US11 con sus criterios de aceptación cumplidos y su **trazabilidad prevista** (pantalla + endpoint + prueba) documentada en [historias de usuario](historias-usuario.md).
- Núcleo E1–E4 funcional de extremo a extremo.
- Degradación elegante verificable (app usable sin ninguna clave).
- Documentación de producto (este conjunto) coherente y enlazada.
