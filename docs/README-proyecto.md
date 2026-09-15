# Chispa ✨

**App web (responsive: móvil / tablet / PC) de aprendizaje por curiosidad para niños.**

Cada niño es un perfil con **PIN** dentro de una **cuenta familiar**. Sigue su curiosidad: enciende una
"chispa" (una pregunta), recibe una **mini-lección adaptada a su edad** y puede **seguir preguntando en una
conversación tipo chat**. Cada tema explorado se convierte en una **isla** de su **grafo de conocimiento**
("archipiélago"), que puede reabrir para profundizar. Los padres administran, supervisan y aprueban contenido.
Dirección visual: *Archipiélago / explorador* (náutica, coral + teal, tipografías Fredoka/Mulish).

> Proyecto Final de **LIDR – AI4Devs**. Construido de forma incremental (de la idea al despliegue) apoyándose en IA en todas las fases.

---

## ✨ Características

**Familia y perfiles**
- Cuenta de familia (registro/login con JWT) y **perfiles de niño** con fecha de nacimiento → **edad calculada** + **PIN**.
- **Avatares**: set diseñado (SVG: animales, espacio, deportes) **o generados por IA** a partir de una descripción.
- Pantalla de **bienvenida** + acceso claro para volver a entrar; sesiones de familia y de niño separadas.

**Aprendizaje**
- **Bucle central**: curiosidad → mini-lección → **reto (quiz)** → **isla** en el grafo de conocimiento.
- **Lecciones ricas y adaptadas a la edad** (bandas 3–5 / 6–8 / 9–12), con pedagogía inspirada en la skill `teach`.
- **Conversación tipo chat**: el niño **sigue preguntando** en el mismo hilo con contexto; el reto es **opcional por turno** y no interrumpe la conversación.
- **Islas vivas**: las islas se crean solas por detrás; **pinchar una isla reabre su conversación** guardada; **buscador** del archipiélago.
- **Voz**: **dictar** la pregunta (🎤) y **leer la lección en voz alta** (🔊) con las APIs nativas del navegador (multiidioma, sin servidor).
- **Imágenes** en las lecciones acordes a la edad (cuando se configura un modelo de imagen).

**Cuentos**
- **Biblioteca de cuentos** del niño con **aprobación parental**: el niño crea un cuento (queda pendiente) y solo lee los aprobados; la familia aprueba, edita o rechaza.

**IA multi-proveedor (por familia, con clave cifrada)**
- **Texto**: `stub` (demo), **Ollama** (local), **Claude** y **OpenAI** activos; Gemini/DeepSeek/Kimi preparados. Recomendador de modelo local por hardware (VRAM/RAM).
- **Imagen**: **HuggingFace** (FLUX.1-schnell, gratis con token), **SDXL local** (Automatic1111), OpenAI (gpt-image-1-mini), Gemini (gemini-3.1-flash-image). *(Ollama no genera imágenes.)*
- **Degradación elegante**: si no hay proveedor configurado, todo funciona en modo demo/diseñado sin errores ni coste.

**Plataforma**
- **Multilenguaje** es/en (detecta el navegador, el usuario puede cambiarlo) · **responsive** y táctil.
- **Acceso desde la red de casa** (móvil/tablet) + pantalla **"Conectar móvil"** con URL y **QR**.
- **Seguridad**: moderación de la entrada del niño (con *fallback seguro*); el backend nunca envía la respuesta correcta del quiz; JWT con tipo (familia/niño); claves de IA **cifradas (Fernet)**; SSRF mitigado en el endpoint de imagen local; cada niño solo accede a sus datos; imágenes generadas fuera del control de versiones.

---

## 🏗️ Arquitectura

```
[ React + TS (Vite) ] ──HTTPS/REST──► [ FastAPI ] ──► [ PostgreSQL / SQLite ]
  · Bienvenida / auth (JWT)            routers → services → repositories → models (SQLAlchemy 2.0)
  · Niño con PIN · avatares                 │
  · Chat de lecciones · islas          [ LessonGenerator ]  [ ImageGenerator ]   (interfaces + fábricas)
  · Cuentos · panel familia                 ├─ Stub (demo)       ├─ Stub (off)
  · i18n (es/en) · voz · responsive         ├─ Ollama / Claude   ├─ HuggingFace / SDXL local
                                            └─ OpenAI/Gemini…    └─ OpenAI / Gemini
```

La generación de **texto** e **imagen** vive tras dos interfaces (`LessonGenerator`, `ImageGenerator`) con
**fábricas por familia** y **fallback al stub**: los proveedores reales se enchufan sin tocar el resto, y el
niño nunca ve un fallo del proveedor. Las imágenes se guardan en disco y se sirven en `/media`.

**Stack:** Backend Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2 (pytest, ruff).
Frontend React 18 + TypeScript + Vite + React Router (Vitest + Testing Library). DB: PostgreSQL (prod) / SQLite (dev/tests).

---

## 🐳 Docker (auto-alojable, recomendado)

```bash
cp .env.example .env          # rellena JWT_SECRET y AI_CONFIG_KEY (ver docs/MANUAL.md)
docker compose up --build -d
# Frontend: http://localhost:5173 · API: http://localhost:8000
```
Incluye **Ollama** para IA de texto local gratuita. Guía completa: **`docs/MANUAL.md`**.

### Acceso desde el móvil/tablet de tu red
Pon en `.env` la IP de tu PC (`ipconfig`) y reconstruye:
```bash
VITE_API_URL=http://192.168.1.50:8000
CORS_ORIGINS=http://localhost:5173,http://192.168.1.50:5173
```
Luego abre `http://192.168.1.50:5173` en el móvil (misma WiFi). También hay un QR dentro de la app en **Familia → 📱 Conectar móvil**.

---

## 🚀 Puesta en marcha (desarrollo)

### Backend (FastAPI)
```bash
cd backend
py -3.12 -m venv .venv
. .venv/Scripts/activate            # Linux/Mac: . .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload       # http://localhost:8000  (docs en /docs)
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev                         # http://localhost:5173
```
El frontend lee `VITE_API_URL` (por defecto `http://localhost:8000`).

### Variables de entorno (backend)
| Variable | Por defecto | Notas |
|---|---|---|
| `JWT_SECRET` | (inseguro para dev) | **Obligatorio** y ≥32 chars fuera de desarrollo |
| `AI_CONFIG_KEY` | — | Clave Fernet para cifrar las claves de IA de las familias |
| `DATABASE_URL` | `sqlite+pysqlite:///./chispa.db` | Postgres en producción |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes permitidos (coma-separados) |
| `MEDIA_DIR` | `media` | Carpeta de imágenes generadas (servidas en `/media`) |
| `ENVIRONMENT` | `development` | `production`/`staging` exigen secreto fuerte |

---

## 🤖 Activar IA real (opcional)

Todo funciona en **modo demo** sin configurar nada. Para IA real, en la app: **Familia → ⚙️ Configurar IA**.

- **Texto (lecciones)** — elige **Claude** o **OpenAI** (pega tu API key, se guarda cifrada) o **Ollama** local (pon la URL y elige modelo; hay recomendador por hardware).
- **Imágenes** — sección **🖼️ Imágenes en las lecciones**: la vía gratis es **HuggingFace** (crea un token en `huggingface.co/settings/tokens` con permiso *Inference Providers*), o **SDXL local** (URL de Automatic1111). Al activarlo, lecciones y avatares salen con imágenes acordes a la edad.

Las claves nunca se muestran ni se devuelven; se almacenan cifradas.

---

## 🔌 API (resumen)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/auth/register` · `/auth/login` | — | Crear/entrar familia → token |
| POST/GET | `/children` | familia | Crear / listar perfiles de niño (con avatar) |
| POST | `/children/{id}/login` | familia | Login del niño con PIN → token de niño |
| POST | `/children/{id}/avatar/generate` | familia | Generar avatar con IA (409 si imagen off) |
| POST | `/lessons` | niño | Encender una chispa → lección raíz |
| POST | `/lessons/{id}/ask` | niño | Seguir la conversación (turno con contexto) |
| GET | `/lessons/{id}/thread` | niño | Hilo completo de la conversación |
| POST | `/lessons/{id}/answer` | niño | Responder el reto (acertar sube maestría) |
| GET | `/me/profile` · `/me/knowledge` · `/me/suggestions` | niño | Perfil, islas, sugerencias |
| POST/GET | `/me/stories` · `/me/stories/{id}` | niño | Crear / leer cuentos aprobados |
| GET/PUT | `/family/stories` · `/family/stories/{id}` | familia | Revisar / aprobar / editar / rechazar |
| GET/PUT | `/family/ai-config` (+ `/catalog`, `/recommend`) | familia | Config de IA (texto + imagen) |

Documentación interactiva completa en **`/docs`** (Swagger).

---

## 🧪 Tests y calidad

```bash
cd backend && pytest -q && ruff check .             # 144 tests
cd frontend && npm test && npm run lint            # 60 tests · tsc --noEmit
```
Migraciones Alembic siempre aditivas (no destructivas). CI en `.github/workflows/ci.yml` (lint + tests).

---

## 📁 Estructura

```
chispa/
├── backend/   FastAPI
│   └── app/{routers,services,repositories,models,schemas}
│       services/  lesson_generator · ai_providers · image_generator · image_providers · crypto · moderation · ai_catalog
├── frontend/  React + Vite
│   └── src/{api,auth,components,screens,i18n,routes,styles}
│       components/ avatars · MicButton · SpeakButton · ChildHeader · ScreenCard …
├── docs/      MANUAL.md (Docker/despliegue) · design-system.md (tokens "Archipiélago")
├── docker-compose.yml   postgres + backend + frontend + ollama
└── .github/workflows/ci.yml
```

---

## 🗺️ Estado

Roadmap construido de punta a punta: familia + perfiles + avatares · lecciones ricas por edad · **chat conversacional
con islas vivas** · cuentos con aprobación parental · **voz (dictado + lectura)** · **generación de imagen y avatares por IA**
(4 proveedores, off por defecto) · acceso LAN + QR · IA multi-proveedor con claves cifradas.

Pendiente de **activación** por el operador: pegar un token de imagen (HuggingFace gratis) o levantar SDXL local
para ver imágenes reales. Efectos de sonido/vídeo generados por IA quedarían para cuando exista un modelo de audio/vídeo.
