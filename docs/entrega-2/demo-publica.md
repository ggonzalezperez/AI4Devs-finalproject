# Demo pública — infraestructura real (21-09-2026)

Qué hay montado, por qué así, y cómo rehacerlo si se pierde. El
[diseño previo](../superpowers/specs/2026-09-14-despliegue-demo-publica-design.md) describía esta
infraestructura como intención; esto describe lo que existe.

**URL:** `https://chispa.chispalearn.com`

## 1. El camino que recorre una petición

```
Navegador ──https──> Cloudflare (borde, TLS) ──> Cloudflare Access (¿quién eres?)
                                                        │
                                              túnel saliente cifrado
                                                        │
                            VM Ubuntu en el TrueNAS de casa (192.168.31.18)
                                                        │
                        contenedor cloudflared ──> contenedor frontend (nginx)
                                                        │
                                           /api ──> backend ──> postgres
```

No se abre **ningún puerto** en el router y no se publica la IP doméstica: `cloudflared` abre una
conexión **saliente** hacia Cloudflare. El TLS lo termina Cloudflare con certificados que se renuevan
solos.

## 2. Dominio

`chispalearn.com`, registrado en **Cloudflare Registrar**. Se eligió ahí porque el dominio nace
dentro de la cuenta: nameservers puestos, zona activa al instante y sin esperar propagación.

Ajustes de la zona, todos verificados desde fuera de la red:

| Ajuste | Valor | Por qué |
|---|---|---|
| Modo SSL/TLS | Completo (estricto) | El tráfico no viaja sin cifrar en ningún tramo. No exige certificado en la VM porque entra por el túnel |
| Usar siempre HTTPS | Activado | `http://` responde 301 |
| DNSSEC | Activo | Registro DS publicado en `.com`; las respuestas validan (`AD: true`) |
| DNSSEC multifirmante | **No** | Incompatible con el registrador |

El registro DNS de `chispa.chispalearn.com` lo creó el propio túnel: es un CNAME a
`<id>.cfargotunnel.com`, y no debe editarse a mano.

## 3. El túnel corre como contenedor, no como servicio del sistema

Esta es la decisión menos obvia del despliegue. Lo habitual es `sudo cloudflared service install`,
pero **la contraseña de `sudo` del usuario `german` en la VM se había perdido**: se administra por
clave SSH y no hay forma de escalar a root sin pasar por la consola VNC.

En lugar de arreglar eso a las prisas, el conector se añadió al mismo `docker-compose` de la
aplicación (fichero `docker-compose.override.yml`, que vive **solo en la VM**):

```yaml
  cloudflared:
    image: cloudflare/cloudflared:latest
    restart: unless-stopped
    command: tunnel --no-autoupdate run
    environment:
      TUNNEL_TOKEN: ${TUNNEL_TOKEN:?define TUNNEL_TOKEN en .env}
    depends_on:
      - frontend
```

Consecuencias que hay que tener presentes:

- El *public hostname* del túnel apunta a **`frontend:80`**, no a `localhost:5173`. Dentro de Docker,
  `localhost` es el propio conector. Si alguien lo cambia a `localhost`, la web deja de cargar.
- `TUNNEL_TOKEN` vive en el `.env` de la VM, con el resto de secretos, **fuera de git**.
- El conector arranca y se reinicia con el resto de la aplicación (`restart: unless-stopped`), así
  que sobrevive a un reinicio de la VM sin necesitar `systemd`.
- En los registros aparece `failed to sufficiently increase receive buffer size`. Es un ajuste del
  kernel que un contenedor sin privilegios no puede aplicar; QUIC funciona igual.

## 4. Cloudflare Access delante

La aplicación está detrás de una aplicación *self-hosted* de Cloudflare Access (`chispa` →
`chispa.chispalearn.com`) con una política reutilizable **Allow** llamada `Autorizados`, que incluye
una regla **Include → Emails** con la lista de correos permitidos.

> **Corregido el 27-09-2026.** Esta sección afirmaba «One-time PIN como método de identidad, sin
> configurar proveedor de identidad». **Era falso**, y de la peor manera: el único método activo era
> el **proveedor de identidad de Cloudflare**, que exige tener cuenta propia de Cloudflare. Un
> revisor externo **no habría podido entrar jamás**, tuviera su correo en la política o no. Se
> descubrió probando el acceso en una ventana de incógnito, que es la única forma de verlo: con la
> sesión del propietario abierta, todo parece funcionar.
>
> La lección, que ya es la tercera de este despliegue: **la política decide *quién* pasa; el método
> de inicio de sesión decide *cómo* se identifica.** Tener bien lo primero no sirve de nada si lo
> segundo no existe.

Métodos de inicio de sesión activos hoy, los dos a la vez:

| Método | Para quién | Dónde se configura |
|---|---|---|
| **Cloudflare** (IdP) | El propietario | Ya estaba |
| **One-time PIN** | Revisores y cualquier invitado sin cuenta de Cloudflare | Añadido en **Integraciones → Proveedores de identidad** |

Como la aplicación tiene activado *«Acepte todos los proveedores de identidad disponibles»*, dar de
alta el PIN a nivel de cuenta bastó para que apareciera en `chispa`: no hubo que tocar la aplicación.

Del One-time PIN conviene recordar que Cloudflare **solo envía el código si la política ya permite
esa dirección**, y que la pantalla muestra el mismo mensaje tanto si lo envía como si no. Por eso un
correo mal escrito en la lista se diagnostica como «no llega el email». El código caduca a los **10
minutos**, es de **un solo uso**, y pedir otro invalida el anterior. El remitente es
`noreply@notify.cloudflare.com`.

Protege **todas las rutas, incluida `/api`**: una petición sin sesión recibe 302 hacia la pantalla de
login de Cloudflare y nunca llega al backend.

Access es una defensa **perimetral y externa**: cierra la puerta mientras está puesto, pero no forma
parte del producto. Por eso, en el mismo trabajo, se implementaron en la aplicación el
[código de invitación](estado-implementacion.md) y el
[límite de intentos](../entrega-1/02-technical-design/adr/ADR-008-rate-limiting-en-memoria-por-proceso.md):
si un día se quita Access, la aplicación no vuelve a quedar desnuda.

## 5. Variables propias de este despliegue

Además de las de siempre (`JWT_SECRET`, `AI_CONFIG_KEY`, `POSTGRES_*`), el `.env` de la VM define:

| Variable | Valor | Efecto |
|---|---|---|
| `INVITE_CODE` | palabra secreta | El alta de familia la exige; sin ella, 403 |
| `CLIENT_IP_HEADER` | `CF-Connecting-IP` | El límite de intentos cuenta por IP real. Cloudflare sobrescribe esta cabecera en el borde |
| `TUNNEL_TOKEN` | token del túnel | Credencial del conector |
| `RATE_LIMIT_ENABLED` | sin definir (activo) | Interruptor del límite de intentos. Si una familia se autobloquea y hay prisa, se puede apagar un rato; en condiciones normales no se toca |

**Lo que NO debe estar en ese `.env`:** `VITE_API_URL`. Hornea la dirección del backend dentro del
bundle y rompe la app publicada. Estuvo ahí de las pruebas por la red local y costó una hora de
diagnóstico el 21-09.

El puerto 8000 del backend se publica **solo en `127.0.0.1`**. Si se expusiera a la red local,
cualquiera podría falsificar `CF-Connecting-IP` y esquivar el cubo por IP del limitador.

## 6. Operación

```bash
ssh -i ~/.ssh/chispa_vm_key german@192.168.31.18
cd /opt/chispa
git pull
docker compose up -d --build     # ~2 min en frío, ~1 min incremental
docker compose ps
docker compose logs --tail 20 cloudflared
```

El código llega por un **deploy key de solo lectura** del repositorio privado. El volumen `pgdata`
sobrevive al borrado y reclonado del código; el volumen `media` guarda las ilustraciones generadas.

### Migración de las ilustraciones a WebP (21-09-2026)

Operación manual ejecutada una vez sobre el volumen `media`, al pasar a pedir las imágenes en WebP.
Se deja escrita porque **modificó datos del despliegue**, no solo código:

```bash
# 1. Convertir, conservando los originales
docker run --rm -v chispa_media:/media alpine:latest sh -c '
  apk add --no-cache libwebp-tools
  mkdir -p /media/lessons/_originales_png
  for f in /media/lessons/*.png; do
    b=$(basename "$f" .png)
    cwebp -q 80 "$f" -o "/media/lessons/$b.webp" && mv "$f" /media/lessons/_originales_png/
  done'

# 2. Apuntar la base de datos a los nuevos ficheros
docker compose exec -T postgres psql -U chispa -d chispa   -c "update lessons set image_url = replace(image_url, '.png', '.webp') where image_url like '%.png';"

# 3. Comprobar en la app que se ven, y solo entonces borrar los originales
```

Resultado: ocho ilustraciones de entre 1,4 y 2,9 MB pasaron a entre 55 y 322 KB. El volumen bajó de
**19 MB a 2 MB**. Las generadas ya en WebP rondan los 74 KB; las convertidas pesan más porque
arrastran el ruido del PNG original.

### Comprobar que el despliegue responde

Comprobación rápida desde fuera (con sesión de Access iniciada):

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://chispa.chispalearn.com/
curl -s https://chispa.chispalearn.com/api/health
```

## 6.b Endurecimiento de la máquina (21-09-2026)

La VM vive en la misma red doméstica que el NAS, donde hay fotos y archivos personales. La pregunta
que guió estos ajustes no fue *"¿es segura la aplicación?"* sino *"si alguien toma la aplicación,
¿qué alcanza desde ahí?"*.

| Medida | Estado antes | Ahora |
|---|---|---|
| Acceso por SSH | Aceptaba **contraseña**, sin `fail2ban` | Solo clave (`/etc/ssh/sshd_config.d/00-solo-clave.conf`) |
| Cortafuegos | `ufw` instalado pero **inactivo** | Activo: entra solo 22, 5173 y 5443 |
| Salida hacia la red de casa | Sin restricción: alcanzaba SMB y el panel del NAS | **Denegada** hacia `192.168.31.0/24`, salvo el router (DNS y salida a internet) |

El nombre del fichero de SSH importa: **sshd se queda con el primer valor que lee**, y
`50-cloud-init.conf` activa la contraseña. Un `99-` no habría surtido efecto —de hecho no lo surtió
al primer intento— y renumerarlo reabriría el acceso por contraseña sin que nada avise.

Lo que ya era correcto y conviene no perder: la VM **no monta ningún recurso del NAS**, no guarda
credenciales suyas —la única clave presente es la de despliegue de GitHub, de solo lectura— y los
contenedores corren sin privilegios y sin acceso al disco del host.

**Nota sobre el grupo `docker`**: el usuario `german` pertenece a él, y eso equivale a ser root
(basta un contenedor que monte el disco). Fue la vía para recuperar la contraseña de `sudo` perdida,
sin pasar por la consola VNC, y es también la razón por la que cerrar el SSH importa más que la
contraseña en sí.

## 6.c Caché: por qué la app se actualiza al desplegar

nginx no enviaba ninguna cabecera de caché, y el 21-09 eso sirvió durante una hora el bundle del
despliegue anterior: la pantalla mostraba un formulario de alta sin el campo de código de
invitación **mientras el servidor no recibía ni una petición**. La configuración actual:

| Ruta | Cabecera | Por qué |
|---|---|---|
| `index.html` | `no-store, must-revalidate` | Es el único fichero con nombre fijo y quien decide qué bundle se carga. Si se cachea, el despliegue no llega al usuario |
| `/assets/*` | `public, max-age=31536000, immutable` | Llevan un hash en el nombre: si el contenido cambia, cambia el nombre |
| `/api/media/*` | `public, max-age=31536000, immutable` + `proxy_buffering off` | Las ilustraciones no cambian nunca, y sin desactivar el búfer nginx las escribía en un fichero temporal antes de enviarlas |

Al desplegar una versión nueva conviene **purgar la caché de Cloudflare** (panel del dominio →
Caché → Purgar todo) la primera vez, porque el borde puede conservar copias anteriores a este
cambio.

## 7. Límites conocidos

| Asunto | Detalle |
|---|---|
| **Corte a los 100 s** | Cloudflare aborta con 524 cualquier petición que pase de 100 segundos, y `nginx.conf` permite 180 s. **Medido el 21-09: una lección con ilustración de OpenAI tarda 18,1 s**, cinco veces por debajo del límite. El registro de nginx incluye `$request_time` y `$upstream_response_time` (formato `con_tiempo`) precisamente para poder vigilarlo: `docker compose logs frontend \| grep "POST /api/lessons"` |
| **Disponibilidad** | Depende de que el NAS de casa y la conexión estén encendidos. La guía del máster acepta un vídeo de la demo como respaldo |
| **Actualizaciones del sistema** | `unattended-upgrades` está activo, así que los parches de seguridad de Ubuntu se aplican solos. La contraseña de `sudo`, que se había perdido, se recuperó el 21-09 |
| **El NAS sigue siendo blando en la LAN** | Expone panel web y SMB a toda la red de casa. La VM ya no lo alcanza, pero cualquier otro dispositivo sí: la defensa ahí es la contraseña del NAS, su doble factor y las instantáneas ZFS |
| **Base de datos independiente** | La de la VM no es la del portátil: un `git pull` trae código, nunca datos. La demo arranca vacía |
| **Access se salta con la política** | Si se desactiva la política para una demo, el registro sigue protegido por `INVITE_CODE`, no por Access |
