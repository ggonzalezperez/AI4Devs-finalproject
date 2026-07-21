# Chispa ✨ — Resumen del proyecto · Entrega 1

> **Máster LIDR – AI4Devs · Proyecto Final · Entrega 1 (Producto y diseño técnico)**
> Fecha de entrega: **22 de julio de 2026**. Documento de identificación y resumen ejecutivo.
>
> Esta entrega es **documental y previa a la implementación**: define **qué se va a construir, cómo y con qué
> papel de la IA**, como paso anterior a escribir el código. No incluye código; describe el producto y el diseño.

---

## 1. Identificación

| Campo | Valor |
|---|---|
| **Alumno** | Germán González Pérez |
| **Correo** | gerx97@gmail.com |
| **Proyecto** | **Chispa** — aprendizaje por curiosidad para niños, con IA |
| **Repositorio** | `github.com/ggonzalezperez/chispa` (privado; acceso al TA a solicitud) |
| **Entrega** | 1 de 3 — Producto y diseño técnico (documental) |
| **Modalidad** | Individual |
| **Estado** | Fase de definición: producto y diseño técnico listos para pasar a implementación |

> Nota de confidencialidad: el repositorio es privado. Para la evaluación se concederá acceso al Teacher Assistant / equipo evaluador según el proceso oficial de entrega.

---

## 2. Descripción breve

> **Chispa ayudará a los niños a aprender desde su curiosidad, convirtiendo cada pregunta en una pequeña
> aventura de conocimiento adaptada a su edad, segura para la familia y acumulada en su propio mapa de aprendizaje.**

No es una app de deberes ni una enciclopedia con IA: es un **espacio personal de descubrimiento** —curiosidad
guiada con **memoria pedagógica**— donde cada niño construye su propio **mapa de conocimiento**.

**Chispa** será una **app web responsive de aprendizaje por curiosidad para niños**. Dentro de una **cuenta
familiar**, cada niño será un **perfil con PIN**. El niño escribirá o dictará una pregunta ("encender una chispa"),
recibirá una **mini-lección adaptada a su edad**, la reforzará con un **reto (quiz)** y podrá **seguir preguntando
en una conversación tipo chat**. Cada tema explorado se convertirá en una **isla** de su **grafo de conocimiento**
("archipiélago"), que podrá reabrir para profundizar. Los padres **administrarán, supervisarán y aprobarán** contenido.

La IA (texto e imagen) se diseña **multiproveedor y configurable por familia**, con **claves cifradas** y
**degradación elegante**: sin proveedor configurado, todo funcionará en **modo demo sin coste ni errores**.

---

## 3. Resumen ejecutivo

| Dimensión | Síntesis |
|---|---|
| **Problema** | La curiosidad infantil choca con pantallas pasivas, contenido no adaptado a la edad y sin supervisión parental. |
| **Usuarios** | **Familia/Adulto** (gestiona y supervisa) y **Explorador/Niño** (aprende con PIN, sin exponer sus datos). |
| **Propuesta de valor** | Convertir cualquier pregunta del niño en micro-aprendizaje seguro y adaptado por edad, visible como un archipiélago que crece, con control parental real. |
| **MVP** | 11 historias planificadas, organizadas en 6 épicas (onboarding, bucle de aprendizaje, conocimiento vivo, cuentos, IA configurable, plataforma/accesibilidad). |
| **Arquitectura propuesta** | SPA React+TS → API FastAPI (capas routers/services/repositories/models) → PostgreSQL/SQLite; IA tras dos *seams* con fábrica por familia y *fallback* al stub. |
| **IA en el producto** | Texto (stub/Ollama/Claude; OpenAI/Gemini/DeepSeek/Kimi como opción) e imagen (HuggingFace/SDXL local/OpenAI/Gemini/Pollinations), desactivada por defecto. |
| **IA en el proceso** | Se desarrollará con flujo **SDD / subagent-driven** (spec→implementación→revisión), con validación en dos capas y una estrategia de pruebas por riesgo. |
| **Seguridad** | JWT tipado familia/niño, claves de IA cifradas (Fernet), moderación de entrada + fallback seguro, aislamiento de datos por propietario, mitigación SSRF, el backend nunca enviará la respuesta del quiz. |
| **Despliegue** | Docker Compose autoalojable (postgres + backend + frontend + Ollama), acceso LAN + QR, CI a configurar (ruff/pytest + tsc/vitest). |

---

## 4. Enlaces y referencias

| Recurso | Ubicación |
|---|---|
| Documentación de la entrega | [`docs/entrega-1/`](README.md) (este directorio) |
| Sistema de diseño ("Archipiélago") | [`docs/design-system.md`](../design-system.md) |
| Mockup visual (fuente del diseño) | claude.ai/design (privado, destilado en `design-system.md`) |
| Guía académica de la entrega | [`docs/Guia_integrada_proyecto_final_AI_for_Devs.md`](../Guia_integrada_proyecto_final_AI_for_Devs.md) |

---

## 5. Índice de la Entrega 1

Ver [**README.md**](README.md) para el índice completo con la checklist de cumplimiento.
Estructura resumida:

- `01-product/` — problema y usuarios, PRD, alcance, historias de usuario, requisitos (RF/RNF) y trazabilidad.
- `02-technical-design/` — arquitectura, modelo de datos, contratos de API, seguridad, decisiones tecnológicas y ADRs.
- `03-testing/` — estrategia de pruebas y casos de aceptación.
- `04-delivery/` — estrategia de despliegue y guion de demo previsto.
- `05-ai-log/` — uso previsto de IA: flujo de trabajo, agentes, prompts y bitácora (formato).
