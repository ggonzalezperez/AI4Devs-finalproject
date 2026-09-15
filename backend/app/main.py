from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers import ai_config, auth, children, lessons, me, stories

app = FastAPI(title="Chispa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(children.router)
app.include_router(lessons.router)
app.include_router(me.router)
app.include_router(ai_config.router)
app.include_router(stories.router)

_media_root = Path(get_settings().media_dir)
(_media_root / "lessons").mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_media_root)), name="media")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
