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

---

# Verificación — Endurecimiento del acceso (21-09-2026)

> Salidas obtenidas ejecutando los comandos el 21 de septiembre de 2026, tras publicar la aplicación
> en internet. Contexto en [demo pública](demo-publica.md).

## 7. Suites tras el cambio

```
$ cd backend && python -m pytest -q
179 passed, 1 warning in 36.40s

$ cd backend && ruff check .
All checks passed!

$ cd frontend && npx vitest run
 Test Files  32 passed (32)
      Tests  73 passed (73)

$ cd frontend && npm run lint      # tsc --noEmit
(sin salida: sin errores)
```

Evolución: backend **144 → 179** (+35), frontend **67 → 73** (+6, incluida la primera cobertura de
la pantalla de login, que no tenía ninguna).

| Fichero nuevo | Tests | Qué sujeta |
|---|---|---|
| `backend/tests/test_invite_code.py` | 8 | Registro abierto sin configurar · 403 con código erróneo o ausente · ningún usuario creado al rechazar · el mensaje no revela el código |
| `backend/tests/test_rate_limit.py` | 9 | Ventana deslizante con reloj falso · `Retry-After` decreciente · aislamiento de claves · **20 hilos concurrentes aceptan exactamente el límite** · desalojo por tope de memoria |
| `backend/tests/test_client_ip.py` | 6 | **Cabecera falsificada ignorada si no hay proxy declarado** · lectura de la cabecera configurada · cadena `X-Forwarded-For` · valor que no es IP |
| `backend/tests/test_rate_limit_api.py` | 12 | 429 por IP y por cuenta · el login correcto olvida su cubo · un hermano no bloquea al otro · **JSON malformado sigue devolviendo 422** |

## 8. Humo contra el despliegue real

Ejecutado dentro de la VM contra el origen de la aplicación (`http://localhost:5173/api`), que es el
mismo camino que recorre el navegador tras el túnel.

```
--- registro SIN codigo ---
403
--- registro con codigo MALO ---
{"detail":"Código de invitación no válido"}
403
--- registro con codigo BUENO ---
201
--- 11 logins fallidos ---
401 401 401 401 401 429 429 429 429 429 429
--- cabeceras del corte ---
HTTP/1.1 429 Too Many Requests
retry-after: 898
```

El corte llega al **sexto** intento, no al undécimo: el cubo por cuenta (5) se agota antes que el de
IP (10), que es exactamente el comportamiento buscado contra quien ataca una cuenta concreta.

Los usuarios creados en esta prueba se borraron después; la base de datos de la demo queda como
estaba.

## 9. Cloudflare Access

```
$ curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" https://chispa.chispalearn.com/
302 -> https://small-sky-a744.cloudflareaccess.com/cdn-cgi/access/login/chispa.chispalearn.com?...

$ curl -s -o /dev/null -w "%{http_code}\n" https://chispa.chispalearn.com/api/health
302
```

Access protege **todas** las rutas, incluida la API: sin sesión, la petición no llega al backend.
Antes de activarlo, esas mismas dos llamadas devolvían `200` y `{"status":"ok"}`.

## 10. Uso real de la demo publicada (21-09-2026, noche)

Primera sesión de uso completo desde un móvil, por el dominio público. Sirvió para medir dos cosas
que hasta entonces eran suposiciones, y para encontrar tres fallos que ninguna suite habría visto
(ver [AI-LOG-011](../entrega-1/05-ai-log/decisiones.md)).

**El corte de 100 segundos de Cloudflare ya no es un riesgo abierto.** Con el tiempo de respuesta
añadido al registro de nginx:

```
POST /api/lessons  ->  201 en 18.139s (upstream 18.137s)
```

Cinco veces por debajo del límite del borde. El dato es de una lección con ilustración generada por
OpenAI, que es el caso más lento.

**Peso de las ilustraciones**, antes y después de pedirlas en WebP:

```
$ ls -lh /app/media/lessons/   # antes
2.5M 3.png   2.4M 4.png   2.1M 5.png   2.4M 6.png   2.2M 7.png   2.9M 8.png

$ ls -lh /app/media/lessons/   # después, generada ya en WebP
74K 11.webp

$ du -sh /app/media/lessons    # tras convertir las ocho anteriores
2.0M        (eran 19M)
```

**Humo del alta con código de invitación**, contra el origen real:

```
alta sin código    -> 403
alta con el código -> 201
```

## 11. Suites tras el trabajo de imágenes y documentación (22-09-2026)

```
$ cd backend && python -m pytest -q
182 passed, 1 warning in 38.63s

$ cd backend && ruff check .
All checks passed!

$ cd frontend && npx vitest run
 Test Files  32 passed (32)
      Tests  74 passed (74)

$ cd frontend && npm run lint      # tsc --noEmit
(sin salida: sin errores)
```

Evolución completa de la entrega: backend **108 → 144 → 179 → 182**, frontend **48 → 60 → 73 → 74**.

Las tres pruebas nuevas cubren los fallos que solo aparecían en producción y la optimización de
imagen: que una `VITE_API_URL` vacía siga cayendo en `/api`, que a OpenAI se le pidan WebP
comprimido y calidad media, y que el fichero se guarde con la extensión de su formato real.

**Las ilustraciones se sirven correctamente** (comprobado contra el despliegue, tras convertir las
antiguas):

```
$ curl -sI http://localhost:5173/api/media/lessons/11.webp
HTTP/1.1 200 OK
Content-Type: image/webp
Content-Length: 75730
Cache-Control: public, max-age=31536000, immutable
```

El tipo MIME correcto importa: antes salían como `application/octet-stream` porque la imagen base
del contenedor no conoce la extensión `.webp`.

## 12. Lo que estas pruebas no cubren
- El límite se ejercita con el limitador en su configuración real, pero **no se ha probado bajo carga
  concurrente contra el despliegue**, solo en el test de 20 hilos del contador.
- **Un solo recorrido de usuario real**, hecho por el propio autor. No hay pruebas con un niño ni con
  un evaluador externo.
- La conversión de las ilustraciones antiguas se verificó **abriendo las lecciones**, no comparando
  las imágenes píxel a píxel.
