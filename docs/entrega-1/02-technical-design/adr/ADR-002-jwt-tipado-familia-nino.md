# ADR-002 — JWT tipado familia/niño con doble sesión separada

**Estado:** Aceptada (fase de diseño)

## Contexto

Chispa tiene dos actores con superficies muy distintas: la **familia** (contraseña, panel de control, config de IA, aprobación de cuentos) y el **niño** (PIN, lecciones, quiz). Deben poder estar activos a la vez en el mismo dispositivo de casa, y un fallo de uno no debe afectar al otro (p. ej., el padre no debe desloguearse porque el niño falle el PIN).

## Decisión

Emitir **JWT firmados con HS256** que incluirán un claim `type` con valor `family` o `child`. En el cliente se mantendrán **dos sesiones independientes** en `localStorage`:

- familia → `chispa_token` (gestionada por `SessionContext`).
- niño → `chispa_child_token`.

Cada endpoint validará el `type` requerido, aislando las superficies de familia y de niño.

## Alternativas consideradas

- **Una sola sesión con roles**: mezcla ambas superficies en un token; un cambio de contexto obligaría a re-login y acoplaría los dos flujos.
- **Sesiones de servidor**: añade estado y almacenamiento en el backend, innecesario para una app autoalojada familiar; los JWT son suficientes y sin estado.

## Consecuencias

- **Aislamiento de superficies**: el padre no se deslogueará cuando el niño falle el PIN, y viceversa.
- **Expiración de 30 días**, razonable para una app autoalojada de uso doméstico frecuente.
- **Fail-closed del secreto**: fuera de entorno de desarrollo, la ausencia de `JWT_SECRET` hará fallar el arranque/firma en lugar de usar un valor por defecto inseguro.

## Componentes de diseño

- Módulo de dependencias de auth (`HTTPBearer(auto_error=False)`, validación de `type`).
- Configuración (`JWT_SECRET`, comportamiento fail-closed).
- Frontend: `SessionContext`, claves `chispa_token` / `chispa_child_token`, `ProtectedRoute`.
