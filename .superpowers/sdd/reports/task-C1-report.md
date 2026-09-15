# Task C1 Report: Fernet Crypto + FamilyAIConfig Model + Migration

## Status: DONE

---

## Files Created

- `backend/app/services/crypto.py` — Fernet encryption helpers (`generate_key`, `encrypt`, `decrypt`, `_resolve_key`)
- `backend/app/models/ai_config.py` — `FamilyAIConfig` SQLAlchemy model (`family_ai_config` table)
- `backend/tests/test_crypto.py` — roundtrip encrypt/decrypt test
- `backend/tests/test_ai_config_model.py` — model default values test
- `backend/alembic/versions/30776978742d_ai_config_family_ai_config_table.py` — Alembic migration

## Files Modified

- `backend/pyproject.toml` — added `httpx>=0.27` and `cryptography>=42` to runtime dependencies
- `backend/app/config.py` — added `ai_config_key: str | None = None` field to `Settings`
- `backend/app/models/__init__.py` — appended `from app.models.ai_config import FamilyAIConfig  # noqa: F401`

---

## Test Results (verbatim)

```
============================== test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
...
36 passed, 2 warnings in 2.98s
```

All 36 tests pass (2 new + 34 pre-existing).

---

## Migration Safety Inspection

Migration file: `backend/alembic/versions/30776978742d_ai_config_family_ai_config_table.py`

**upgrade() op.* lines:**
```python
op.create_table('family_ai_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=False),
    sa.Column('tier', sa.String(length=20), nullable=False),
    sa.Column('provider', sa.String(length=20), nullable=False),
    sa.Column('model', sa.String(length=80), nullable=True),
    sa.Column('base_url', sa.String(length=255), nullable=True),
    sa.Column('api_key_encrypted', sa.String(length=500), nullable=True),
    sa.Column('monthly_quota', sa.Integer(), nullable=False),
    sa.Column('used_count', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['family_id'], ['families.id'], ),
    sa.PrimaryKeyConstraint('id')
)
op.create_index(op.f('ix_family_ai_config_family_id'), 'family_ai_config', ['family_id'], unique=True)
```

**Verdict: SAFE** — upgrade contains only `op.create_table("family_ai_config", ...)` and `op.create_index(...)`. No `op.drop_table` or `op.drop_column` on pre-existing tables. Migration applied successfully (`f500d39dfa90 -> 30776978742d`).

---

## Concerns

None. All requirements met.
