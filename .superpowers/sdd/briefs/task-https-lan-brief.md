# Brief — https-lan: origen único y HTTPS en la red de casa

## Contexto

La app se sirve en dos orígenes: el frontend en `:5173` (nginx) y la API en `:8000`. Eso obliga
a `VITE_API_URL` (horneado en tiempo de build) y a `CORS_ORIGINS`, y ya ha costado un fallo
real: al abrir la app desde el móvil por IP, el bundle seguía llamando a `localhost:8000` y no
funcionaba nada hasta reconstruir con la IP dentro.

Además el micrófono (RF-PLT-02) no funciona fuera de `localhost`: la Web Speech API exige
contexto seguro. Para que funcione en cualquier dispositivo de casa hace falta HTTPS.

**Dependencia dura:** con dos orígenes, poner HTTPS solo en el frontend rompe la app entera —
una página https no puede llamar a `http://192.168.x.x:8000` (contenido mixto bloqueado). El
origen único no es una mejora opcional, es el requisito previo del HTTPS.

## Alcance

- **Entra:** nginx del frontend hace de proxy inverso de la API bajo `/api`; el cliente del
  frontend pasa a usar ruta relativa por defecto; certificado de CA propia para la IP de la
  red local; nginx escucha en 443 además de 80; compose publica el puerto https.
- **No entra:** exponer nada a Internet (túneles, ngrok, Cloudflare); Let's Encrypt; dominio
  propio; HTTP/2; redirección forzosa de http a https (se deja http operativo para no romper
  el acceso actual mientras se prueba); despliegue en el servidor final.
- **Mínimo entregable:** desde un móvil de casa con la CA instalada, `https://192.168.31.91`
  abre la app, la API responde bajo el mismo origen y el micrófono pide permiso y transcribe.

## Diseño

- **Backend:** ninguno en el código. `CORS_ORIGINS` deja de ser crítico (mismo origen), pero se
  conserva la variable para el acceso http directo durante la transición.
- **Frontend:**
  - `nginx.conf`: `location /api/ { proxy_pass http://backend:8000/; }` con cabeceras
    `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`. Bloque `listen 443 ssl` con
    el certificado montado. `location /media/` también al backend (las imágenes generadas se
    sirven desde ahí y si no quedarían fuera del origen único).
  - `api/client.ts`: `BASE_URL` pasa a `import.meta.env.VITE_API_URL ?? ""` — cadena vacía =
    ruta relativa = mismo origen. Con `VITE_API_URL` definido sigue funcionando como antes,
    así que el modo desarrollo (`npm run dev` contra `uvicorn` en :8000) no se rompe.
  - `Dockerfile`: el `ARG VITE_API_URL` pasa a vacío por defecto.
- **Infra:**
  - `certs/` (fuera del control de versiones) con `rootCA.crt`, `chispa.crt`, `chispa.key`
    generados con openssl, SAN = `IP:192.168.31.91`, `DNS:localhost`, `IP:127.0.0.1`.
  - `docker-compose.yml`: el frontend publica `5173:80` y `5443:443`, y monta `./certs` en
    solo lectura. El backend deja de necesitar publicar `8000` hacia fuera (se conserva
    publicado durante la transición para poder depurar).
  - `.gitignore`: `certs/`.
- **Datos:** ninguno. Sin migración.

## Reglas de negocio

- Las claves privadas **nunca** entran en el repositorio. `certs/` va a `.gitignore` y se
  verifica con `git check-ignore` antes de commitear.
- El proxy no debe exponer nada nuevo: solo `/api/` y `/media/` van al backend; el resto sigue
  sirviendo el SPA.
- No se abre ningún puerto a Internet. El certificado es para uso en la red local.
- El aislamiento por niño y la moderación no cambian: el backend es el mismo, solo cambia por
  dónde le llegan las peticiones.

## Validación

| Caso | Dado / Cuando / Entonces | Test previsto |
|---|---|---|
| Ruta relativa | Dado `VITE_API_URL` vacío, cuando el cliente pide `/auth/login`, entonces usa el mismo origen | `client.test.ts` (nuevo) |
| Respeta la variable | Dado `VITE_API_URL` definido, entonces se usa tal cual | `client.test.ts` (nuevo) |
| API por el proxy | `curl -k https://192.168.31.91:5443/api/health` → 200 `{"status":"ok"}` | curl manual |
| SPA intacta | `curl -k https://192.168.31.91:5443/` → 200 y sirve `index.html` | curl manual |
| Media por el proxy | `curl -k https://192.168.31.91:5443/media/...` llega al backend | curl manual |
| Certificado correcto | El certificado presenta SAN `IP:192.168.31.91` | `openssl s_client` |
| Suite completa | Frontend y backend siguen verdes | `vitest run`, `pytest` |

## Trazabilidad

HU: US11 · RF: RF-PLT-02 (micrófono fuera de localhost), RF-PLT-04 (conectar dispositivo) ·
Ficheros: `frontend/nginx.conf`, `frontend/Dockerfile`, `frontend/src/api/client.ts`,
`docker-compose.yml`, `.gitignore` · Tests: `frontend/src/api/client.test.ts`

## Riesgos

- **La CA hay que instalarla en cada dispositivo.** No cumple "cualquier móvil sin tocar
  nada": para el móvil de un evaluador haría falta un certificado públicamente confiable, que
  a su vez exige dominio propio. Asumido: el alcance de hoy es la red de casa.
- **Android exige bloqueo de pantalla** (PIN o patrón) para instalar una CA de usuario, y
  muestra un aviso permanente de red supervisada.
- **La IP es DHCP.** Si el router cambia la IP, el certificado deja de casar. Mitigación:
  reservar la IP en el router, o regenerar el certificado.
- **Deriva de configuración:** si alguien deja `VITE_API_URL` apuntando a `:8000` en su `.env`,
  vuelve el problema de contenido mixto. Mitigación: documentarlo y dejar el valor vacío.
