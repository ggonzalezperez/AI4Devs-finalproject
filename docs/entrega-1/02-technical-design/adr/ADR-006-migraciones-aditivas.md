# ADR-006 — Migraciones Alembic siempre aditivas

**Estado:** Aceptada (fase de diseño)

## Contexto

Chispa es autoalojada: la familia actualiza la app en su propio PC y sus datos (progreso del niño, cuentos, config) deben sobrevivir a cada actualización. Las migraciones autogeneradas por Alembic pueden incluir `DROP`/`ALTER` destructivos que borrarían datos reales.

## Decisión

Adoptar la regla de que **toda migración será aditiva**. Cada tarea de trabajo obligará a **detenerse si la migración autogenerada contiene drops o alters destructivos** y a reescribirla en términos aditivos:

- `add_column` **nullable** o **con `server_default`**.
- `create_table`.

El resultado previsto será una **cadena de migraciones lineales y aditivas**, sin ramas ni pasos destructivos.

## Alternativas consideradas

- **Aceptar las migraciones autogeneradas tal cual**: cómodo, pero un `DROP COLUMN`/`ALTER` no revisado puede destruir los datos de la familia en una actualización.
- **Backfills/alters destructivos con scripts de datos**: mayor complejidad y riesgo en un entorno sin DBA; innecesario para el alcance actual.

## Consecuencias

- **Cero pérdida de datos** y **despliegues seguros**: actualizar solo añadirá estructura, nunca la eliminará.
- Historial de migraciones **lineal y auditable**.
- Coste asumido: a veces habrá que mantener columnas antiguas nullable en lugar de renombrarlas/eliminarlas.

## Componentes de diseño

- Directorio de migraciones Alembic (cadena lineal de `add_column` nullable/`server_default` y `create_table`).
- Regla de trabajo: "detente si la migración trae drops/alters" incorporada al flujo de desarrollo.
