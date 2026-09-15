# Task E1: Dockerización (compose: Postgres + backend + frontend + Ollama) + manual + README

Repo raíz `chispa/`. Rama `feature-entrega4-ai-config`. SIN push. (Infra: crear archivos; validar `docker compose config`; NO hacer build pesado de imágenes.)

**Files:**
- Modify: `backend/pyproject.toml` (añadir `[build-system]` y `[tool.setuptools]` para build determinista en Docker)
- Create: `backend/Dockerfile`
- Create: `backend/docker-entrypoint.sh`
- Create: `backend/.dockerignore`
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`
- Create: `frontend/.dockerignore`
- Create: `docker-compose.yml` (raíz)
- Create: `.env.example` (raíz)
- Create: `docs/MANUAL.md`
- Modify: `README.md` (sección Docker)

## Step 1: `backend/pyproject.toml` — añadir al final del archivo:
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["app"]
```

## Step 2: `backend/Dockerfile`
```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1
COPY pyproject.toml ./
COPY app ./app
RUN pip install .
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
```

## Step 3: `backend/docker-entrypoint.sh`
```sh
#!/bin/sh
set -e
echo "Aplicando migraciones..."
alembic upgrade head
echo "Arrancando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Step 4: `backend/.dockerignore`
```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
*.db
*.egg-info/
tests/
```

## Step 5: `frontend/Dockerfile`
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

## Step 6: `frontend/nginx.conf`
```nginx
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  location / {
    try_files $uri /index.html;
  }
}
```

## Step 7: `frontend/.dockerignore`
```
node_modules/
dist/
.env
```

## Step 8: `docker-compose.yml` (raíz)
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: chispa
      POSTGRES_PASSWORD: chispa
      POSTGRES_DB: chispa
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chispa"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+psycopg://chispa:chispa@postgres:5432/chispa
      JWT_SECRET: ${JWT_SECRET}
      AI_CONFIG_KEY: ${AI_CONFIG_KEY}
      ENVIRONMENT: production
      CORS_ORIGINS: http://localhost:5173
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: http://localhost:8000
    ports:
      - "5173:80"
    depends_on:
      - backend

  ollama:
    image: ollama/ollama
    volumes:
      - ollama:/root/.ollama
    ports:
      - "11434:11434"
    # GPU (descomenta si tienes nvidia-container-toolkit instalado):
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]

volumes:
  pgdata:
  ollama:
```

## Step 9: `.env.example` (raíz)
```bash
# Copia a .env y rellena. NO se commitea (.env está en .gitignore del backend; añade .env a .gitignore raíz si hace falta).
# Secreto JWT (mínimo 32 caracteres en producción)
JWT_SECRET=cambia-esto-por-un-secreto-largo-de-al-menos-32-caracteres

# Clave maestra para cifrar las API keys de las familias (Fernet).
# Genera una con:
#   docker compose run --rm backend python -c "from app.services.crypto import generate_key; print(generate_key())"
AI_CONFIG_KEY=
```
Además, crea/añade un `.gitignore` en la raíz con `.env` si no existe (sin borrar el `.gitignore` raíz actual que ignora `.superpowers/`): añade la línea `.env`.

## Step 10: `docs/MANUAL.md`
```markdown
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
- **Tu propia clave (BYOK):** proveedor **Claude** (activo), pega tu API key (se guarda **cifrada**). Obtén la clave en console.anthropic.com.
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

## Seguridad
- Las API keys de las familias se guardan **cifradas** (Fernet, `AI_CONFIG_KEY`). Nunca se devuelven por la API.
- Los datos viven en el Postgres del stack de la familia (auto-alojable).
```

## Step 11: README — añadir sección Docker
Añade cerca del inicio del `README.md` (sin borrar lo existente) una sección:
```markdown
## 🐳 Docker (auto-alojable, recomendado)

```bash
cp .env.example .env   # genera AI_CONFIG_KEY y JWT_SECRET (ver docs/MANUAL.md)
docker compose up --build -d
# Frontend: http://localhost:5173 · API: http://localhost:8000
```
Incluye **Ollama** para IA local gratuita. Guía completa: **`docs/MANUAL.md`**.
```

## Step 12: Validar compose (sin build)
Run en la raíz: `docker compose config >/dev/null && echo "compose OK"`. Si falla, corrige la sintaxis. (NO ejecutes `docker compose up`/`build` — es pesado.)

## Step 13: Commit (local, SIN push)
```bash
git add backend/ frontend/ docker-compose.yml .env.example docs/ README.md .gitignore
git commit -m "feat: dockerize (compose: postgres+backend+frontend+ollama) + manual"
```
