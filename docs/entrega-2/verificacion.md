# Verificación — Entrega 2 · Chispa ✨

> Fecha de ejecución: **15 de septiembre de 2026**. Todas las salidas de este documento se
> obtuvieron ejecutando los comandos, no se transcribieron de memoria.

---

## 1. Suites de pruebas

```
$ cd backend && python -m pytest -q
144 passed, 1 warning in 20.64s

$ cd backend && python -m ruff check .
All checks passed!

$ cd frontend && npm test
 Test Files  31 passed (31)
      Tests  60 passed (60)

$ cd frontend && npm run lint      # tsc --noEmit
(sin salida: sin errores)
```

Evolución: backend **108 → 144**, frontend **48 → 60**.
Avisos de deprecación: **4 → 1** (el restante pide migrar a `httpx2`, decisión aplazada).

### Cobertura por riesgo

La estrategia no persigue un porcentaje, sino que cada regla de seguridad del menor tenga su caso
negativo:

| Regla | Test |
|---|---|
| El backend nunca envía la respuesta del quiz | `test_security.py` + verificación por `curl` |
| Moderación de la entrada del niño | `test_moderation.py` (21 casos: bloqueo, falsos positivos y formas derivadas) |
| Aislamiento entre familias y niños | `test_security.py`, `test_family_panel.py` |
| JWT tipado con rechazo cruzado | `test_deps.py`, `test_deps_child.py`, `test_family_panel.py` |
| Cuentos invisibles hasta aprobarse | `test_story_api.py` |

## 2. Integración continua

GitHub Actions ejecuta `ruff`, `pytest`, `tsc` y `vitest` en cada *push*. Último estado: **verde**.

> **Incidente resuelto en esta entrega.** El primer *push* dejó la CI en rojo con 146 errores de
> `ruff` mientras en local pasaba limpio. No era el código: `pyproject.toml` declaraba `ruff>=0.5`,
> un rango abierto, y la CI instalaba **0.16.7** frente a la **0.15.20** local. Los ficheros
> señalados no se tocaban desde julio: era un fallo latente, no una regresión.
>
> Se arregló de raíz en lugar de fijar la versión vieja: reglas **declaradas explícitamente**
> (`select = ["E","W","F","I","UP","B"]`), `B008` configurado para no marcar `Depends(...)` —el
> idioma de FastAPI, y origen de 52 de los 146 avisos—, `E501` excluida a propósito, 94 avisos
> auto-arreglados y 9 corregidos a mano. La versión de `ruff` queda fijada para que local y CI
> ejecuten lo mismo.

## 3. Despliegue con Docker Compose

`RNF-08` exige que la app sea autoalojable. Verificado con el código de esta entrega:

```
$ docker compose up --build -d
$ docker compose ps
SERVICE    STATUS
backend    Up
frontend   Up
ollama     Up
postgres   Up (healthy)

$ curl http://localhost:8000/health
{"status":"ok"} [200]
$ curl -o /dev/null -w "%{http_code}" http://localhost:5173/
200
$ curl -o /dev/null -w "%{http_code}" http://localhost:8000/docs
200

$ docker compose exec backend alembic current
ad23d09d1b34 (head)
```

Las **11 migraciones** aplican limpias sobre PostgreSQL 16 desde base vacía, y la reejecución es
idempotente (en un arranque posterior con volumen existente, Alembic no aplica nada y el esquema
sigue en HEAD).

## 4. Pruebas manuales de endpoints

Ejecutadas por el agente contra la API real, **no** contra el cliente de pruebas.

### 4.1. Contra `uvicorn` (desarrollo)

| Petición | Caso | Esperado | Obtenido |
|---|---|---|---|
| `GET /children/{id}/profile` | camino feliz | 200 | 200 · `{"name":"Nora","age":8,"islands":1}` |
| `GET /children/{id}/knowledge` | maestría tras acertar | `mastery: 2` | `mastery: 2` |
| `GET /children/{id}/profile` | token `child` | 401 | 401 |
| `GET /children/{id}/knowledge` | sin token | 401 | 401 |
| `GET /children/99999/profile` | niño ajeno | 404 | 404 |
| `GET /lessons/{id}` | fuga del quiz | 0 apariciones | 0 apariciones |

### 4.2. Contra el stack de Docker (imagen de producción)

| Petición | Caso | Esperado | Obtenido |
|---|---|---|---|
| `POST /lessons` | «como se hace una armadura» | 201 (no bloquear) | **201** |
| `POST /lessons` | «quiero matarte» | 422 (bloquear) | **422** |
| `GET /children/{id}/profile` | panel de familia | 200 | **200** |
| `POST /children` | PIN `"12a4"` | 422 | **422** |

Las dos primeras filas son la prueba de que la moderación quedó corregida **en ambas direcciones**:
ya no bloquea lo inocente y sigue bloqueando lo que debe.

## 4.3. Evidencia de despliegue

Salida literal en [`evidencias/despliegue/`](evidencias/despliegue/):

| Fichero | Contenido |
|---|---|
| `01-arranque.txt` | `docker compose up --build -d` desde cero, tras `down -v` |
| `02-servicios-y-migraciones.txt` | `docker compose ps` con los 4 servicios · `/health`, frontend y Swagger a 200 · `alembic current` en HEAD · **11 migraciones aplicadas desde base vacía** |
| `03-humo-api.txt` | 10 casos de API contra el stack de producción, incluidos los negativos |

Los 10 casos del humo coinciden con lo esperado, incluidos los cuatro que protegen al menor: token
cruzado → 401, hijo ajeno → 404, moderación → 422 y la respuesta del quiz sin filtrar.

## 5. Recorrido end-to-end

Navegador real (Playwright), escritorio 1280×900 y móvil 390×844.

| # | Captura | Qué demuestra |
|---|---|---|
| 01 | `e2-01-familia-tripulacion.png` | Zona de familia con sus accesos |
| 02 | `e2-02-panel-familia-nora.png` | **Panel de familia**: 2 conceptos dominados, 1 emergente, con la flecha `←` de vuelta |
| 03 | `e2-03-panel-familia-leo-sin-actividad.png` | Estado vacío coherente de un hijo sin actividad |
| 04 | `e2-04-panel-familia-movil.png` | El panel a 390 px (`RNF-06`) |
| 05 | `e2-05-acceso-nino-pin.png` | Acceso del niño con teclado de PIN |
| 06 | `e2-06-encender-la-chispa.png` | Entrada de la curiosidad, micrófono, enlace **«Salir»** y sugerencias rotatorias |
| 07 | `e2-07-leccion-armadura-no-bloqueada.png` | Lección para «armadura», con el cuerpo de la banda 6-8 |
| 08 | `e2-08-reto-acertado.png` | Reto resuelto, lo único que sube la maestría |
| 09 | `e2-09-archipielago-del-nino.png` | Islas del niño con su buscador |
| 10 | `e2-10-panel-ia-multiproveedor.png` | Configuración de IA con **OpenAI habilitado** y los modelos vigentes |
| 11 | `e2-11-conectar-movil-qr.png` | URL de LAN y QR |
| 12 | `e2-12-aprobacion-parental-cuentos.png` | Aprobación parental de cuentos |
| 13 | `e2-13-clave-invalida-rechazada.png` | **`RF-IA-02`**: una clave sin forma de clave se rechaza al guardar, en vez de fallar en silencio después |
| 14 | `e2-14-chispa-esta-pensando.png` | **`RNF-07`**: el indicador de espera, donde aparecerá la respuesta |
| 15 | `e2-15-salir-sesion-nino.png` | **`RF-SEG-04`**: salir de la sesión del niño pide la contraseña de la familia |
| 16 | `e2-16-salir-contrasena-incorrecta.png` | **`RF-SEG-04`**: contraseña incorrecta → no se cierra nada |

> La 14 se obtuvo **retrasando la respuesta a propósito** (interceptando `fetch` en el navegador):
> con el generador de demo la espera dura milisegundos y no se puede fotografiar. Con un proveedor
> real ese estado dura entre 2 y 5 segundos, que es justo el motivo de que el indicador exista.

**Consola del navegador: 0 errores** en todo el recorrido. Quedan 2 avisos de *future flags* de
React Router v6→v7, ajenos a esta entrega.

La captura 07 sirve doble: prueba que la moderación ya no bloquea «armadura» y muestra el cuerpo de
la banda 6-8 (Nora tiene 8 años) con su analogía, que es el arreglo de `RF-APR-03`.

## 6. Revisión adversaria

Ejecutada sobre el trabajo de la jornada antes de dar nada por cerrado. Halló un **bloqueante en mi
propio arreglo**: al pasar la moderación de subcadena a palabra completa se cerraron los falsos
positivos pero se abrieron falsos negativos («matarte», «suicidar», «drogadicto», «pornográficos»
dejaron de bloquearse). Corregido con un esquema de dos listas —raíces por prefijo y palabras
exactas— y verificado en ambas direcciones.

Queda anotada una limitación del método: la revisión la hizo la misma sesión que implementó, no una
independiente como pide el estándar.
