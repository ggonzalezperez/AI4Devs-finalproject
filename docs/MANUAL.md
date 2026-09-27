# Chispa — Manual de instalación

Cómo poner Chispa en marcha en tu propia máquina. Para aprender a **usarla** —crear la familia,
añadir exploradores, revisar cuentos— está el [manual de uso](manual-usuario.md).

## Requisitos
- Docker y Docker Compose.
- (Opcional, para IA local) GPU NVIDIA + `nvidia-container-toolkit` para acelerar Ollama.

## 1. Configurar secretos
```bash
cp .env.example .env
# Genera la clave de cifrado de claves API:
docker compose run --rm backend python -c "from app.services.crypto import generate_key; print(generate_key())"
# Pega el resultado en AI_CONFIG_KEY del .env, y pon un JWT_SECRET largo.
```

## 2. Levantar todo
```bash
docker compose up --build -d
```
- Frontend: http://localhost:5173 (y https://localhost:5443 si has generado los certificados)
- API: bajo el mismo origen, en `/api` (por ejemplo http://localhost:5173/api/health)
- API directa, para depurar: http://localhost:8000 (docs en /docs). Solo desde la propia
  máquina: el puerto está atado a `127.0.0.1` a propósito, porque exponerlo en la red local
  permitiría falsificar la cabecera de IP en la que se apoya el límite de intentos.

## 3. Elegir cómo se genera la IA (panel de padres → "⚙️ Configurar IA")
Tres niveles:
- **Gratis / local (Ollama):** descarga un modelo primero, p. ej.:
  ```bash
  docker compose exec ollama ollama pull qwen3:4b
  ```
  En el panel: proveedor **Local (Ollama)**, modelo `qwen3:4b`, URL `http://ollama:11434`.
  Usa el **recomendador por hardware** (VRAM/RAM) para saber qué modelo te cabe.
- **Tu propia clave (BYOK):** proveedores **Claude** y **OpenAI** (activos), pega tu API key (se guarda **cifrada**). Obtén la clave en console.anthropic.com o platform.openai.com.
  Si pegas algo que no tiene forma de clave del proveedor, la app lo rechaza al guardar en vez de aceptarla y fallar en silencio después.
- **Comercial:** previsto para 2ª fase (cuota + facturación), aún no activo.

> Si no configuras nada, funciona en modo **demo (stub)** sin coste.

## 4. Modelos locales recomendados (Ollama)
| Modelo | VRAM aprox. | Para |
|---|---|---|
| `llama3.2:3b` | ~3 GB | equipos flojos / portátil |
| `qwen3:4b` | ~5 GB | por defecto, equilibrio |
| `qwen3:14b` | ~10 GB | más calidad |
| `deepseek-r1:32b` | ~22 GB | GPU 24 GB (RTX 3090) |

## 5. Parar / logs
```bash
docker compose logs -f backend
docker compose down          # parar
docker compose down -v       # parar y borrar datos
```

> ⚠️ `down -v` borra **los volúmenes**: la base de datos **y también las ilustraciones
> generadas**, que viven en el volumen `media` (`MEDIA_DIR` dentro del contenedor). Las
> lecciones conservarían la ruta de una imagen que ya no existe; la app lo tolera y
> simplemente no la muestra. Para parar sin perder nada, usa `down` a secas.

## 6. Exponer la instalación fuera de casa (opcional)

Si publicas Chispa en internet, dos variables más en el `.env`:

| Variable | Para qué |
|---|---|
| `INVITE_CODE` | Cierra el alta de familias: quien no tenga la palabra recibe un 403. Sin definir, el registro queda abierto, que es lo normal en una instalación doméstica. **Es un secreto único y compartido, no una invitación por persona:** sirve infinitas veces, no caduca, y la única forma de revocarlo es cambiar la variable, lo que lo invalida para todos a la vez |
| `CLIENT_IP_HEADER` | Cabecera de la que fiarse para conocer la IP real de quien llama, que usa el límite de intentos. **Solo** si hay un proxy de confianza delante: tras un túnel de Cloudflare es `CF-Connecting-IP`. Sin definir no se cree ninguna cabecera |

Hay un caso real documentado paso a paso —dominio, túnel, control de acceso y endurecimiento de
la máquina— en [la demo pública](entrega-2/demo-publica.md).

> ⚠️ **No pongas `VITE_API_URL`** si publicas la app en un dominio. Esa variable hornea la
> dirección del backend dentro del bundle y ata la aplicación a una máquina concreta: deja de
> funcionar por https y el navegador bloquea las llamadas. Solo sirve para apuntar a un backend
> ajeno a propósito.

## Seguridad
- Las API keys de las familias se guardan **cifradas** (Fernet, `AI_CONFIG_KEY`). Nunca se devuelven por la API.
- Los datos viven en el Postgres del stack de la familia (auto-alojable).
- Los flujos de credenciales (alta, entrada, recuperación, PIN del niño y confirmación del adulto)
  tienen **límite de intentos** por IP y por cuenta; al superarlo responden 429. Se puede desactivar
  con `RATE_LIMIT_ENABLED=false`, pero solo tiene sentido para depurar.
