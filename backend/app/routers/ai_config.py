from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_family_user
from app.models.family import User
from app.repositories import ai_config as ai_config_repo
from app.schemas.ai_config import AIConfigRead, AIConfigUpdate, HardwareQuery, Recommendation
from app.services import ai_catalog, crypto

router = APIRouter(prefix="/family/ai-config", tags=["ai-config"])


@router.get("/catalog")
def catalog(_user: User = Depends(get_current_family_user)) -> dict:
    return {
        "providers": ai_catalog.PROVIDERS,
        "ollama_models": ai_catalog.OLLAMA_MODELS,
        "default_local_model": ai_catalog.DEFAULT_LOCAL_MODEL,
        "image_providers": ai_catalog.IMAGE_PROVIDERS,
    }


@router.post("/recommend", response_model=Recommendation)
def recommend(
    payload: HardwareQuery,
    _user: User = Depends(get_current_family_user),
) -> Recommendation:
    return Recommendation(**ai_catalog.recommend_local(payload.vram_gb, payload.ram_gb))


_VALID_TIERS = {"free", "byok", "managed"}


def _to_read(cfg) -> AIConfigRead:
    return AIConfigRead(
        tier=cfg.tier,
        provider=cfg.provider,
        model=cfg.model,
        base_url=cfg.base_url,
        has_api_key=bool(cfg.api_key_encrypted),
        monthly_quota=cfg.monthly_quota,
        used_count=cfg.used_count,
        image_provider=cfg.image_provider,
        image_model=cfg.image_model,
        image_base_url=cfg.image_base_url,
        image_enabled=cfg.image_enabled,
        has_image_api_key=bool(cfg.image_api_key_encrypted),
    )


@router.get("", response_model=AIConfigRead)
def get_config(
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> AIConfigRead:
    return _to_read(ai_config_repo.get_or_create(db, user.family_id))


@router.put("", response_model=AIConfigRead)
def put_config(
    payload: AIConfigUpdate,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> AIConfigRead:
    if payload.tier not in _VALID_TIERS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Nivel inválido")
    provider = next((p for p in ai_catalog.PROVIDERS if p["id"] == payload.provider), None)
    if provider is None or not provider["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Proveedor no disponible",
        )
    # El de imagen se valida igual que el de texto. Sin esto, un id que no está en
    # el catálogo se guardaba con 200, `build_image_generator` no lo reconocía y
    # devolvía el stub: la familia creía tener ilustraciones y no salía ninguna.
    # RF-IA-06 declara la lista cerrada como regla de negocio.
    image_provider = next(
        (p for p in ai_catalog.IMAGE_PROVIDERS if p["id"] == payload.image_provider), None
    )
    if image_provider is None or not image_provider["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Proveedor de imagen no disponible",
        )
    cfg = ai_config_repo.get_or_create(db, user.family_id)
    cfg.tier = payload.tier
    cfg.provider = payload.provider
    cfg.model = payload.model
    cfg.base_url = payload.base_url
    if payload.api_key is not None:
        if payload.api_key == "":
            cfg.api_key_encrypted = None
        else:
            try:
                ai_catalog.check_key_shape(payload.provider, payload.api_key)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
                ) from None
            try:
                cfg.api_key_encrypted = crypto.encrypt(payload.api_key, get_settings().ai_config_key)
            except RuntimeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El servidor no tiene AI_CONFIG_KEY configurada para guardar claves.",
                ) from None
    cfg.image_provider = payload.image_provider
    cfg.image_model = payload.image_model
    cfg.image_base_url = payload.image_base_url
    cfg.image_enabled = payload.image_enabled
    if payload.image_api_key is not None:
        if payload.image_api_key == "":
            cfg.image_api_key_encrypted = None
        else:
            try:
                ai_catalog.check_key_shape(payload.image_provider, payload.image_api_key)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
                ) from None
            try:
                cfg.image_api_key_encrypted = crypto.encrypt(
                    payload.image_api_key, get_settings().ai_config_key
                )
            except RuntimeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El servidor no tiene AI_CONFIG_KEY configurada para guardar claves.",
                ) from None
    db.commit()
    db.refresh(cfg)
    return _to_read(cfg)
