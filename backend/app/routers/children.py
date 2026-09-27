from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import LIMITE_PIN, get_current_family_user
from app.models.child import Child
from app.models.family import User
from app.repositories import ai_config as ai_config_repo
from app.repositories import child as child_repo
from app.repositories import knowledge as knowledge_repo
from app.schemas.auth import Token
from app.schemas.child import AvatarGenerate, ChildCreate, ChildPinLogin, ChildRead
from app.schemas.knowledge import ChildProfile, KnowledgeNodeRead
from app.security import create_token
from app.services import child_service, rate_limit
from app.services.image_generator import build_avatar_prompt
from app.services.image_providers import build_image_generator

router = APIRouter(prefix="/children", tags=["children"])


@router.post("", response_model=ChildRead, status_code=status.HTTP_201_CREATED)
def create_child(
    payload: ChildCreate,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> ChildRead:
    child = child_service.create_child(
        db, user.family_id, payload.name, payload.birthdate, payload.pin, payload.avatar
    )
    return ChildRead.model_validate(child)


@router.get("", response_model=list[ChildRead])
def list_children(
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> list[ChildRead]:
    return [
        ChildRead.model_validate(c) for c in child_service.list_children(db, user.family_id)
    ]


@router.post(
    "/{child_id}/login", response_model=Token, dependencies=[Depends(LIMITE_PIN)]
)
def child_login(
    child_id: int,
    payload: ChildPinLogin,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> Token:
    child = child_service.verify_child_pin(db, user.family_id, child_id, payload.pin)
    if not child:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="PIN incorrecto")
    # PIN correcto: el niño legítimo no arrastra los fallos de tecleo previos.
    rate_limit.limitador.olvidar(f"pin:cuenta:{child_id}")
    return Token(access_token=create_token(subject=str(child.id), token_type="child"))


@router.get("/{child_id}/profile", response_model=ChildProfile)
def child_profile(
    child_id: int,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> ChildProfile:
    child = child_repo.get_child_for_family(db, user.family_id, child_id)
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explorador no encontrado")
    return child_service.build_profile(db, child)


@router.get("/{child_id}/knowledge", response_model=list[KnowledgeNodeRead])
def child_knowledge(
    child_id: int,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> list[KnowledgeNodeRead]:
    child = child_repo.get_child_for_family(db, user.family_id, child_id)
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explorador no encontrado")
    return [
        KnowledgeNodeRead.model_validate(n) for n in knowledge_repo.list_for_child(db, child.id)
    ]


@router.post("/{child_id}/avatar/generate", response_model=ChildRead)
def generate_child_avatar(
    child_id: int,
    payload: AvatarGenerate,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> ChildRead:
    child = db.get(Child, child_id)
    if child is None or child.family_id != user.family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explorador no encontrado")
    cfg = ai_config_repo.get_or_create(db, user.family_id)
    # Desactivada y «falló el proveedor» son problemas distintos: mandar a
    # activar algo que ya está activado deja al usuario sin salida.
    if not cfg.image_enabled or cfg.image_provider == "none":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La generación de imágenes no está activada. Actívala en «Configurar IA».",
        )
    generator = build_image_generator(cfg)
    try:
        img = generator.generate(build_avatar_prompt(payload.description))
    except Exception:
        img = None
    if img is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo dibujar el avatar ahora mismo. Inténtalo de nuevo en un momento.",
        )
    media = Path(get_settings().media_dir) / "avatars"
    media.mkdir(parents=True, exist_ok=True)
    (media / f"{child_id}.png").write_bytes(img.data)
    child.avatar_image_url = f"/media/avatars/{child_id}.png"
    db.commit()
    db.refresh(child)
    return child
