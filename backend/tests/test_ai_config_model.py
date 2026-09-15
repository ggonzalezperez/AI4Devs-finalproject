from app.models.ai_config import FamilyAIConfig
from app.models.family import Family


def test_default_config_is_free_stub(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    cfg = FamilyAIConfig(family_id=fam.id)
    db_session.add(cfg)
    db_session.commit()
    assert cfg.tier == "free"
    assert cfg.provider == "stub"
    assert cfg.monthly_quota == 0
    assert cfg.api_key_encrypted is None
