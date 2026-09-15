---
name: chispa-revision-adversaria
description: Revisión independiente que intenta romper una implementación de Chispa antes de fusionarla — busca deriva entre documentación y código, casos negativos sin cubrir y fugas de seguridad del menor — y emite veredicto PASA/FALLA. Úsala antes de fusionar a main, y cuando el usuario diga "revisa esto", "revisión adversaria" o "¿está listo para fusionar?".
---

# chispa-revision-adversaria

Actúa como **revisor independiente y hostil**: da por supuesto que hay fallos hasta haber
argumentado, con evidencia, que no los hay.

Adaptado de `adversarial-review` (lidr-specboot). Se ejecuta en la ventana entre "implementado" y
"fusionado", idealmente en sesión distinta de la que implementó.

## Mentalidad

- **Intenta romper el sistema**, no confirmar el camino feliz.
- Caza **supuestos incorrectos**: forma de los datos, orden, concurrencia, idempotencia, permisos,
  estados vacíos, cargas grandes, doble envío.
- Mira **entre las piezas**: cosas que funcionan aisladas y fallan juntas (API + UI, reintentos +
  efectos secundarios).
- Trata el diff como **contexto incompleto**: lo que falta (un test, una rama negativa) importa tanto
  como lo que está.
- **Calibra la profundidad al riesgo.** En Chispa, lo que toca a un menor se revisa más duro que lo
  que toca a un panel de configuración.

## Paso 1 — Cargar primero el lado de la especificación

1. Lee el brief en `.superpowers/sdd/briefs/`.
2. Lee la HU y los RF que dice cubrir.
3. Extrae los **criterios de aceptación** y los **no-objetivos**. Lista qué debe ser cierto para
   dar la tarea por "hecha".
4. Anota lo que esté **infraespecificado**: aceptación ambigua, errores sin definir, seguridad
   implícita.

Solo después mira el código. Al revés, el código te convence de que lo que hace es lo que debía hacer.

## Paso 2 — Cargar el lado de la implementación

`git diff` contra la base de la rama. Mapea cada fichero cambiado a la sección del brief que dice
realizar. Un fichero tocado que no corresponde a nada del brief es un hallazgo.

## Paso 3 — Pasada adversaria

Para cada criterio de aceptación:

1. Explica **cómo podría fallar igualmente** mientras el autor cree que pasa.
2. Comprueba los casos de abuso relevantes.
3. Pregunta a los tests si **prueban** el criterio o solo el camino feliz.
4. Registra las **discrepancias entre documento y código** como hallazgos de primera clase.

### Lista específica de Chispa

Estas se comprueban siempre, aunque el cambio parezca no tocarlas:

- [ ] ¿Alguna respuesta filtra `quiz_correct_index` o `quiz_explanation`?
- [ ] ¿Toda entrada de texto del niño pasa por moderación, incluidas las repreguntas del hilo?
- [ ] ¿Los accesos cruzados devuelven **404** y no 403 ni 200 con lista vacía?
- [ ] ¿Un token `child` en endpoint de familia da 401, y al revés?
- [ ] ¿Algún esquema de lectura serializa `pin_hash`, `password_hash`, `family_id`,
      `recovery_code_hash` o una clave cifrada?
- [ ] ¿Qué ve el niño si el proveedor de IA falla? ¿Y si devuelve basura o un quiz de 4 opciones?
- [ ] ¿La migración es aditiva y reversible? ¿Mantiene un único HEAD?
- [ ] ¿Hay texto visible sin pasar por `t()`, o una clave i18n sin su par en el otro idioma?
- [ ] ¿La regla de negocio documentada se aplica en **servidor**, o solo en cliente?

Esta última ha producido ya un hallazgo real: el PIN de 4 dígitos que exige `RF-ONB-03` solo se
valida en el frontend.

## Paso 4 — Severidad

| Severidad | Criterio | ¿Bloquea? |
|---|---|---|
| **Bloqueante** | Comportamiento incorrecto, fallo de seguridad o violación del requisito | Sí |
| **Mayor** | Bug probable o hueco significativo | Sí |
| **Menor** | Claridad, mantenibilidad, riesgo bajo | No |
| **Pregunta** | Necesita confirmación humana | Resolver antes |

Para cada hallazgo, indica dónde va el arreglo: **código**, **tests**, **documentación** o
**requisito**.

## Paso 5 — Salida

```markdown
## Revisión adversaria

**Alcance:** <tarea / rama / diff>
**Fuentes:** <brief, HU/RF, diff>

### Alineación con la especificación
- …

### Hallazgos

| Severidad | Área | Hallazgo | Evidencia | Arreglo (código/tests/docs/requisito) |
|---|---|---|---|---|

### Veredicto
PASA · PASA CON RESERVAS · FALLA

### Antes de fusionar
- …
```

## Salvaguardas

- **No elogies** la implementación para equilibrar la crítica, salvo que una fortaleza mitigue
  directamente un riesgo documentado.
- No te saltes la lectura del brief cuando existe.
- Si no puedes ver el diff, dilo y pide exactamente lo que necesitas. No revises de memoria.
- Termina siempre diciendo si fusionar es **aconsejable** en el estado actual.
