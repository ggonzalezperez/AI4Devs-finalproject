---
name: chispa-bitacora
description: Registra en la bitácora de IA de Chispa los prompts usados, el resultado real que produjeron, las alucinaciones detectadas y las correcciones manuales aplicadas. Úsala al cerrar una tarea, y cuando el usuario diga "apunta esto en la bitácora", "registra el prompt" o pregunte por el registro de uso de IA.
---

# chispa-bitacora

Mantiene `docs/entrega-1/05-ai-log/`, que es lo que la guía académica evalúa bajo "uso real de
inteligencia artificial": no basta con decir que se usó IA, hay que poder demostrar **cómo** y
**cómo se validó**.

Formato heredado del patrón de `AI4Devs-tdd-2604/prompts.md`: cada prompt se registra con **el
resultado que produjo de verdad**, no con el que se esperaba.

## Qué fichero toca

| Fichero | Contenido |
|---|---|
| `prompts.md` | Los prompts relevantes, con su resultado real |
| `decisiones.md` | Entradas AI-LOG: hallazgos, alucinaciones, correcciones, validaciones |
| `agentes.md` | Roles de agentes y skills empleados |
| `flujo-trabajo-ia.md` | El método (brief → TDD → verificación → revisión) |

## Entrada de prompt

En `prompts.md`:

```markdown
## <n> — <qué se pedía>

**Contexto:** <tarea, rama, qué existía antes>

```
<el prompt literal, sin retocar para que quede bonito>
```

**Resultado:** <qué produjo realmente: ficheros, decisiones, números de tests>

**Corrección manual:** <qué hubo que arreglar a mano, o "ninguna">
```

El prompt se copia **literal**. Un prompt embellecido a posteriori no sirve como evidencia de
proceso, que es justo para lo que se guarda.

## Entrada AI-LOG

En `decisiones.md`, para hallazgos, errores del modelo y validaciones:

```markdown
### AI-LOG-<nnn> · <fecha> · <tipo>

- **Qué pasó:** <descripción>
- **Cómo se detectó:** <test que falló, revisión adversaria, lectura del diff, ejecución real>
- **Corrección:** <qué se hizo>
- **Lección:** <qué se cambia en el método para que no se repita>
```

Tipos: `alucinación` · `deriva doc-código` · `decisión` · `validación` · `corrección manual`.

## Qué merece entrada

**Sí:**

- El modelo afirmó algo falso sobre el código y se detectó (alucinación). **Esta es la entrada más
  valiosa del registro.**
- Una divergencia entre lo documentado y lo implementado.
- Una decisión tomada durante la implementación que no estaba en el brief.
- Una corrección manual sobre la salida de la IA.
- Una validación que cambió el rumbo (un test que reveló un supuesto erróneo).

**No:**

- Prompts triviales ("arregla el import").
- Cada iteración de un ciclo TDD normal.
- Lo que ya cuenta el historial de git.

## Reglas

- **Registrar los fallos.** Una bitácora donde la IA nunca se equivoca no es creíble y vale cero en
  la evaluación. Los errores detectados y corregidos son la prueba de que hubo validación humana.
- Fechas absolutas, nunca "ayer" ni "la semana pasada".
- Enlazar al commit o al informe cuando exista.
- Español, y sin adornar: lo que pasó, cómo se detectó, qué se hizo.
