# Chispa — Manual de instalación y uso

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
- Frontend: http://localhost:5173
- API: http://localhost:8000 (docs en /docs)

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

## Seguridad
- Las API keys de las familias se guardan **cifradas** (Fernet, `AI_CONFIG_KEY`). Nunca se devuelven por la API.
- Los datos viven en el Postgres del stack de la familia (auto-alojable).
