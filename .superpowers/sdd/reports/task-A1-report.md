# Task A1 Report: Núcleo Models + Child Auth Dependency

## Status
DONE

## Commit
- SHA: `8ccbe4a`
- Subject: `feat(backend): nucleo models (Lesson, KnowledgeNode) + child auth dependency`
- Branch: `feature-entrega3-nucleo` (not pushed)

## Files Created / Modified
- `backend/app/models/lesson.py` — `Lesson` SQLAlchemy model (14 columns, FK→children)
- `backend/app/models/knowledge.py` — `KnowledgeNode` SQLAlchemy model (6 columns, FK→children)
- `backend/app/models/__init__.py` — added `Lesson` and `KnowledgeNode` imports
- `backend/app/deps.py` — added `get_current_child` dependency (token type="child")
- `backend/alembic/versions/f500d39dfa90_nucleo_lessons_and_knowledge_nodes.py` — migration
- `backend/tests/test_models_nucleo.py` — model integration test
- `backend/tests/test_deps_child.py` — child token type test

## Test Summary
- Targeted: `2 passed` (test_models_nucleo.py, test_deps_child.py)
- Full suite: `22 passed, 1 warning` in 4.49s — all green

## Migration Safety Verification
Migration file: `f500d39dfa90_nucleo_lessons_and_knowledge_nodes.py`

### upgrade() operations (complete list):
```
op.create_table('knowledge_nodes', ...)
op.create_index('ix_knowledge_nodes_child_id', 'knowledge_nodes', ['child_id'], unique=False)
op.create_table('lessons', ...)
op.create_index('ix_lessons_child_id', 'lessons', ['child_id'], unique=False)
```

### downgrade() operations (only drops the two new tables):
```
op.drop_index('ix_lessons_child_id', table_name='lessons')
op.drop_table('lessons')
op.drop_index('ix_knowledge_nodes_child_id', table_name='knowledge_nodes')
op.drop_table('knowledge_nodes')
```

**Result: NON-DESTRUCTIVE.** No `op.drop_table`, `op.drop_column`, or `op.drop_index` on existing tables (families/users/children) anywhere in upgrade(). Migration applied successfully.

## Concerns
None. Implementation matches brief exactly (verbatim code used).
