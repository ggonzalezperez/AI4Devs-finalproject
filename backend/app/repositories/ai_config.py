from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_config import FamilyAIConfig


def get_or_create(db: Session, family_id: int) -> FamilyAIConfig:
    cfg = db.execute(
        select(FamilyAIConfig).where(FamilyAIConfig.family_id == family_id)
    ).scalar_one_or_none()
    if cfg is None:
        cfg = FamilyAIConfig(family_id=family_id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg
