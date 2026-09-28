# Entrega 2 — Código funcional y estructura base · Chispa ✨

> **Máster LIDR – AI4Devs · Proyecto Final** · Alumno: **Germán González Pérez**
> Fecha: **14 de septiembre de 2026** · Rama: `entrega_2`

La Entrega 1 fue documental: definía qué construir y cómo. Ésta es el código, y **el MVP está
completo**: las 10 historias de usuario implementadas, 256 pruebas automatizadas en verde y la
aplicación arrancando de punta a punta con Docker Compose.

---

## Índice

| Documento | Qué contiene |
|---|---|
| [**estado-implementacion.md**](estado-implementacion.md) | Qué existe hoy, historia por historia; las divergencias con la Entrega 1 y cómo se resolvieron; deuda conocida |
| [**verificacion.md**](verificacion.md) | Salida real de suites, linters, Docker, `curl` y recorrido E2E |
| [**demo-publica.md**](demo-publica.md) | La infraestructura que sostiene `chispa.chispalearn.com`: dominio, túnel, Access, operación y límites conocidos |
| [**evidencias/**](evidencias/) | 16 capturas del recorrido completo (escritorio y móvil) y la salida literal del despliegue |

Documentos de referencia fuera de esta carpeta:

- [`docs/manual-usuario.md`](../manual-usuario.md) — cómo se usa la aplicación, para familias.
- [`docs/MANUAL.md`](../MANUAL.md) — cómo se instala y se despliega.
- [`docs/estandares/`](../estandares/base.md) — cómo se trabaja en el proyecto (base, backend, frontend, verificación, documentación).
- [`docs/entrega-1/`](../entrega-1/README.md) — la propuesta previa, conservada en futuro a propósito.
- `.superpowers/sdd/` — briefs, informes y libro mayor, tarea a tarea.

## Lo que pide la guía (§4.2)

| Requisito | Estado | Dónde se comprueba |
|---|---|---|
| Repositorio organizado | ✅ | Monorepo `backend/` + `frontend/`, arquitectura por capas |
| Aplicación ejecutable | ✅ | `docker compose up --build -d` · [verificacion.md §3](verificacion.md) |
| Estructura de frontend y backend | ✅ | 4 capas en backend; pantallas, componentes y cliente tipado en frontend |
| Persistencia / modelo de datos | ✅ | 7 entidades, 11 migraciones aditivas, SQLite y PostgreSQL |
| Flujos principales conectados | ✅ | 10 de 10 historias · [estado-implementacion.md §2](estado-implementacion.md) |
| Primeras pruebas automatizadas | ✅ | **182 backend + 74 frontend**, CI en GitHub Actions |
| Documentación actualizada | ✅ | Esta carpeta + `docs/entrega-1/` corregida donde divergía |
| Bitácora del uso de IA | ✅ | [`docs/entrega-1/05-ai-log/`](../entrega-1/05-ai-log/prompts.md) |
| Evidencias del funcionamiento | ✅ | [verificacion.md](verificacion.md) + [evidencias/](evidencias/) |

## Cómo comprobarlo en cinco minutos

```bash
# 1) Arrancar
cp .env.example .env     # rellenar JWT_SECRET, POSTGRES_PASSWORD y AI_CONFIG_KEY
docker compose up --build -d

# 2) Ver que responde
curl http://localhost:8000/health     # {"status":"ok"}
#    Frontend: http://localhost:5173   ·   API: http://localhost:8000/docs

# 3) Pasar las pruebas
cd backend  && python -m pytest -q && python -m ruff check .
cd frontend && npm test && npm run lint
```

No hace falta ninguna clave de IA: sin proveedor configurado la aplicación funciona entera en modo
demo, con un generador determinista. Es una decisión de diseño (`ADR-001`), no una limitación.

## Qué cambió en esta entrega

**Construido:** el panel de familia (US5/US6), que era la única historia del MVP sin implementar.
La familia ya puede ver qué domina y qué está descubriendo cada hijo.

**Corregido:** las divergencias entre lo documentado y lo implementado —seis en la primera tanda,
encontradas con una
auditoría sistemática. La más relevante para el usuario final: la moderación bloqueaba
curiosidades legítimas de un niño («armadura», «armario», «Armada Invencible») porque comparaba
subcadenas.

**Incorporado:** estándares de proyecto, seis skills propias y TDD Guard con hooks que bloquean
escribir implementación sin un test previo. Detalle en
[estado-implementacion.md §5](estado-implementacion.md).

## Acceso al código

El repositorio de producto es **privado**. Se concede acceso al Teacher Assistant a solicitud,
según el proceso oficial de entrega.
