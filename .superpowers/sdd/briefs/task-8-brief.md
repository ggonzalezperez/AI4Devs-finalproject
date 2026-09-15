# Task 8: CORS en el backend + CI del frontend + README

Estas son tus REQUISITOS. Usa el código EXACTO que aparece aquí.

**Files:**
- Modify: `backend/app/main.py` (CORS middleware)
- Modify: `backend/app/config.py` (origen permitido configurable)
- Test: `backend/tests/test_cors.py`
- Modify: `.github/workflows/ci.yml` (job de frontend)
- Create: `README.md` (arranque local)

**Produces:** backend acepta peticiones del origen del frontend; CI corre tests de frontend; README documenta el arranque.

- [ ] **Step 1: Añadir el campo de origen permitido en `backend/app/config.py`**

Dentro de la clase `Settings`, junto a los demás campos (antes del validador `@model_validator`), añade:

```python
    cors_origins: str = "http://localhost:5173"
```

- [ ] **Step 2: Escribir el test `backend/tests/test_cors.py`**

```python
def test_cors_headers_present(client):
    r = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"
```

- [ ] **Step 3: Reemplazar `backend/app/main.py` por:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, children

app = FastAPI(title="Chispa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(children.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 4: Ejecutar el test de CORS (usa el venv del backend)**

Run (desde `backend/`): `./.venv/Scripts/python.exe -m pytest tests/test_cors.py -v`
Expected: PASS.

- [ ] **Step 5: Ejecutar toda la suite del backend para no romper nada**

Run (desde `backend/`): `./.venv/Scripts/python.exe -m pytest -q`
Expected: todos PASS (19 previos + 1 nuevo = 20).

- [ ] **Step 6: Extender `.github/workflows/ci.yml`** añadiendo un segundo job `frontend` al mismo nivel que `backend` (no borres el job `backend` existente). El archivo completo debe quedar así:

```yaml
name: CI
on:
  push:
    branches: ["**"]
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: pytest -v

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm run lint
      - run: npm test
```

- [ ] **Step 7: Crear `README.md`** en la raíz del repo

```markdown
# Chispa ✨

App de aprendizaje por curiosidad para niños (familia + niño con PIN).

## Backend (FastAPI)

    cd backend
    py -3.12 -m venv .venv
    . .venv/Scripts/activate   # Linux/Mac: . .venv/bin/activate
    pip install -e ".[dev]"
    alembic upgrade head
    uvicorn app.main:app --reload

## Frontend (React + Vite)

    cd frontend
    npm install
    npm run dev   # http://localhost:5173

El frontend lee `VITE_API_URL` (default `http://localhost:8000`).
```

- [ ] **Step 8: Generar `package-lock.json`** (necesario para `npm ci` en CI)

Run (desde `frontend/`): `npm install`
Expected: crea/actualiza `frontend/package-lock.json`.

- [ ] **Step 9: Verificar lint + tests del frontend**

Run (desde `frontend/`): `npm run lint && npm test`
Expected: ambos verdes.

- [ ] **Step 10: Commit**

```bash
git add backend/ frontend/ .github/ README.md
git commit -m "feat: CORS for frontend, frontend CI job and README"
```
