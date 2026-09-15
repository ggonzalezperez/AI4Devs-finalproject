# Diseño — Demo pública de Chispa con IA de pago

> Fecha: 2026-09-14 · Estado: aprobado, pendiente de plan de implementación
> Objetivo: que un evaluador externo pueda **probar Chispa desde internet**, con IA real y fluida, sin que el coste pueda dispararse nunca.

---

## 1. Problema

La Entrega 3 (29 de septiembre de 2026) se valora con revisión humana. El evaluador debería poder **usar** Chispa, no solo leer su documentación. Hoy la app únicamente corre en la LAN doméstica y, por defecto, con el generador *stub*: quien la abriera no vería la IA que justifica el proyecto.

Hacen falta dos cosas que son independientes entre sí:

1. **Exposición**: una URL pública y estable con HTTPS.
2. **IA real**: claves de pago funcionando, con la app respondiendo de forma fluida.

Y una restricción que domina sobre ambas, expresada por el propietario del proyecto:

> **El coste no puede excederse nunca de 50 €, y no puede existir ninguna cuenta capaz de generar una factura ilimitada.**

## 2. Decisiones tomadas

| Decisión | Elección | Motivo |
|---|---|---|
| Dónde corre | Autoalojado + Cloudflare Tunnel | Coincide con la arquitectura ya documentada; ningún proveedor puede facturar |
| Proveedor de IA | **OpenAI** (texto e imagen) | Una sola cuenta y una sola factura; el prepago da tope físico |
| IA local (Ollama) | **Fuera de alcance** | El servidor no tiene potencia; se excluye también del despliegue |
| Origen de las claves | Tier `managed` (servidor) **+ BYOK** | La demo funciona sola, sin perder el BYOK ya construido |
| Tope de gasto | Techo de 50 €, con **degradado** y no corte | El evaluador nunca debe ver la app rota |

**Sobre las cifras de gasto**: 50 € es el techo que no debe superarse bajo ninguna circunstancia. La carga prepagada inicial es de **20 $**, recargable a mano si la demo consume más de lo previsto, siempre sin pasar del techo. La auto-recarga queda **desactivada**: cada recarga es una decisión manual y consciente.
| Acceso | Cuenta demo sembrada **+ código de invitación** | Permite evaluar el alta de familia sin dejar la puerta abierta |

### 2.1. Alternativas descartadas

- **Google Cloud Run + Neon + Cloud Storage.** Coste efectivo 0 € con el crédito de prueba y sin cobro automático posible, pero añade cuatro piezas de infraestructura (Neon, bucket GCS, Secret Manager, dos dominios) y contradice la tesis de aplicación autoalojable del proyecto. Descartado por complejidad, no por coste.
- **Suscripción Google AI Pro (~24 €/mes).** **No incluye acceso a la API**; es el chat de consumo. Comprarla para esto sería dinero perdido.
- **Gemini + Imagen como proveedor principal.** Más barato por imagen, pero Google no ofrece prepago con corte duro. Se conserva como escalón de degradado gratuito.
- **VM bhyve en TrueNAS CORE como primer paso.** Es el destino deseable, no el punto de partida: bhyve en CORE tiene un problema conocido de consumo de memoria por encima de lo asignado y Debian arrastra fallos de instalación por VNC y de arranque UEFI. Con 16 GB compartidos con ZFS y 15 días de plazo, se pospone al paso 2.

## 3. Arquitectura

```
Internet ──HTTPS──> Cloudflare edge ──túnel saliente──> cloudflared
                                                            │
                                            docker compose (sin ollama)
                                                            │
                          ┌─────────────────┬───────────────┴──────────┐
                     frontend (nginx)   backend (uvicorn)         postgres
                                             │                    (volumen pgdata)
                                             ├─> MEDIA_DIR (volumen local)
                                             └─> OpenAI API (clave del servidor)
                                                      └─ sin cuota → Gemini free / Pollinations
```

`cloudflared` abre una conexión **saliente** hacia Cloudflare. No se abre ningún puerto en el router, no se expone la IP doméstica, y el TLS lo termina Cloudflare con certificados que se renuevan solos.

### 3.1. Despliegue en dos pasos

El paso 2 es opcional y no bloquea la entrega.

**Paso 1 — máquina donde la app ya corre.** `docker compose` + `cloudflared`. No introduce infraestructura nueva ni requiere depurar nada: la app ya funciona en esa máquina.

**Paso 2 — VM Debian con Docker en TrueNAS CORE.** Mismo compose dentro de la VM; el túnel se repunta a la nueva máquina. La configuración de Cloudflare no cambia. Si bhyve da problemas, el proyecto se queda en el paso 1 sin consecuencias.

### 3.2. Configuración del despliegue

- `docker-compose.demo.yml`: override que **no arranca el servicio `ollama`** (RAM innecesaria en una máquina justa).
- `VITE_API_URL` y `CORS_ORIGINS` apuntando al dominio del túnel. `VITE_API_URL` se hornea en build (`frontend/src/api/client.ts:1`), así que el frontend debe reconstruirse al fijar el dominio.
- Secretos (`JWT_SECRET`, `AI_CONFIG_KEY`, `POSTGRES_PASSWORD`, claves de IA, `INVITE_CODE`) en el `.env` local. **`.env` nunca se commitea.**

## 4. Los tres frenos de gasto

Son independientes: para que llegue una factura sorpresa tendrían que fallar los tres a la vez.

| # | Freno | Mecanismo | Garantía |
|---|---|---|---|
| 1 | Infraestructura | Autoalojado | No existe proveedor que pueda facturar |
| 2 | IA | OpenAI prepago, auto-recarga **desactivada** | La API deja de aceptar peticiones al llegar a cero; no hay descubierto |
| 3 | Aplicación | Cuota global en código | Corta antes que el freno 2 y degrada a gratis |

Peor caso absoluto: **los 20 $ ya pagados por adelantado**.

> Matiz documentado: OpenAI advierte de que su sistema de facturación puede tardar un poco en cortar tras agotarse el saldo. El margen es de céntimos, y el freno 3 actúa mucho antes.

## 5. Componentes de código

### 5.1. Tier `managed` — claves del servidor

**Problema**: hoy las claves son por familia (`FamilyAIConfig.api_key_encrypted`). Un evaluador tendría que aportar la suya, y no lo hará. El modelo ya contempla `tier: free | byok | managed`, pero `managed` no está implementado: `config.py` no tiene ninguna clave a nivel de servidor.

**Cambios**:
- `app/config.py`: nuevos ajustes opcionales `openai_api_key`, `gemini_api_key` (respaldo), `managed_monthly_quota`, `invite_code`. Al ser opcionales, ni el desarrollo local ni la suite actual cambian de comportamiento.
- `app/services/ai_providers.py:build_generator` y `app/services/image_providers.py:build_image_generator`: si la familia **no** tiene clave propia y el tier es `managed`, se usa la del servidor.

**Invariante**: si la familia tiene clave propia, **gana la suya**. El BYOK con cifrado Fernet es un punto fuerte documentado en la Entrega 1 y no se toca.

### 5.2. Cuota efectiva

**Problema**: `monthly_quota` está en el modelo y `used_count` se incrementa (`app/services/lesson_service.py:48` y `:84`), pero **nadie comprueba nunca si se ha superado**. El contador existe; el límite no.

**Cambios**:
- Nuevo `app/services/quota.py` con una única función que pregunta y consume de forma atómica.
- Nueva tabla `managed_usage (year_month, used_count)` con migración Alembic aditiva. La cuota es **global, no por familia**: el saldo pertenece al propietario del despliegue, no a cada familia. `FamilyAIConfig.monthly_quota` se mantiene intacta para BYOK.
- **Unidad de la cuota**: número de generaciones con IA de pago al mes, no euros. El código no conoce precios ni consulta saldos. El valor de `managed_monthly_quota` se calibra al configurar el despliegue, dividiendo el presupuesto entre el coste por generación del momento (texto + imagen). Contar peticiones en lugar de dinero evita acoplar la app a una tarifa que cambia.
- `lesson_service.py`: los dos incrementos sueltos pasan a la llamada centralizada.

**Comportamiento al agotarse**: no se devuelve error. Se baja de escalón a Gemini free (texto) y Pollinations (imagen), ambos sin coste. El niño nunca ve un fallo.

### 5.3. Acceso

- `app/routers/auth.py:register`: campo `invite_code` en `RegisterRequest`, validado **solo si** `settings.invite_code` está definida. Sin definir, el registro se comporta como hoy y la suite actual sigue verde.
- `backend/scripts/seed_demo.py`: familia demo, dos exploradores y un par de lecciones ya generadas, para que la app se vea con contenido desde el primer clic.

### 5.4. Catálogo de modelos

`app/services/ai_catalog.py`:
- Proveedor de texto OpenAI: `enabled: False` → `True` (los generadores ya existen y funcionan).
- IDs de modelo actualizados. Los actuales (`gpt-4o-mini`, `gemini-1.5-flash`, `imagen-3.0-generate-002`) son de 2024. **Los vigentes se verificarán contra la documentación del proveedor durante la implementación, no de memoria.**

### 5.5. Documentación

- `docs/entrega-1/04-delivery/despliegue.md`: sección nueva de **entorno de demostración**, para que el despliegue público no parezca un abandono no explicado de la arquitectura autoalojada.
- Bitácora de IA (`docs/entrega-1/05-ai-log/`) actualizada.

## 6. Flujo de datos

Un niño pregunta algo →
`create_lesson` → **`quota.consume()`** →
&nbsp;&nbsp;· queda cuota → OpenAI con la clave del servidor
&nbsp;&nbsp;· agotada → Gemini free →
genera el texto de la lección →
`_attach_image` genera la imagen y la escribe en `MEDIA_DIR` →
se sirve en `/media/lessons/{id}.png`.

Si cualquier proveedor falla, el `except` ya existente en `lesson_service.py` cae al stub.

## 7. Manejo de errores

El principio ya presente en el código — *el niño nunca ve un fallo del proveedor* — se mantiene y se extiende:

| Situación | Respuesta |
|---|---|
| Proveedor caído o con error | Fallback a stub (comportamiento actual) |
| Cuota agotada | Degradado a proveedor gratuito, sin error |
| Clave de servidor ausente | Se comporta como hoy: stub |
| Código de invitación inválido | 403 explícito (es un error de adulto, no del niño) |

## 8. Pruebas

Unitarias nuevas:
- Cuota agotada → degrada en lugar de fallar.
- Familia con clave propia → se usa la suya, **no** la del servidor.
- Familia sin clave y tier `managed` → se usa la del servidor.
- Código de invitación inválido → 403; código no configurado → registro abierto.

Reglas:
- **Ningún test golpea la API real de OpenAI.** `httpx` se mockea, siguiendo la práctica ya establecida en la suite.
- **Los 33 ficheros de test actuales deben seguir verdes.** Es criterio de aceptación.

Humo tras el despliegue, contra la URL pública: `/health`, alta de familia con código, creación de una lección real con IA, y verificación de que la imagen persiste tras reiniciar los contenedores.

## 9. Seguro de disponibilidad

Un despliegue autoalojado depende de que la máquina y la conexión estén levantadas cuando el evaluador decida entrar. Se mitiga grabando un **vídeo de la demo**, que la guía del máster acepta explícitamente como entregable.

## 10. Fuera de alcance (YAGNI)

CI/CD automatizado, observabilidad, backups programados, dominio propio de pago, Cloud Armor o equivalentes, migración a almacenamiento de objetos, y Ollama. Todo ello ya figura como trabajo futuro en `despliegue.md` y nada de ello hace falta para una demo evaluable de dos semanas.

## 11. Criterios de aceptación

1. Existe una URL pública HTTPS donde un tercero puede registrarse con código y usar Chispa.
2. Las lecciones se generan con IA real de OpenAI, texto e imagen.
3. Agotada la cuota, la app sigue funcionando con proveedores gratuitos.
4. Una familia con clave propia usa su clave, no la del servidor.
5. No existe ninguna cuenta configurada que pueda facturar por encima del saldo prepagado.
6. La suite completa pasa en verde.
7. La documentación de despliegue refleja el entorno de demostración.
