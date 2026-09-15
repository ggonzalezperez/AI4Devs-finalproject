# Task A4 Report: Answer Quiz + Knowledge Graph Update

## Status: DONE

## Commit
- SHA: `43b5bf3`
- Subject: `feat(backend): answer quiz updates child knowledge graph`

## Files Created/Modified
- **Created** `backend/app/repositories/knowledge.py` — `upsert_node` and `list_for_child`
- **Created** `backend/app/schemas/answer.py` — `AnswerRequest`, `AnswerResult` Pydantic models
- **Modified** `backend/app/services/lesson_service.py` — added `answer_lesson` function + `knowledge_repo` import
- **Modified** `backend/app/routers/lessons.py` — added `POST /{lesson_id}/answer` endpoint + answer schema imports
- **Created** `backend/tests/test_answer_api.py` — TDD tests (written before implementation)

## Test Summary
- Targeted: 2/2 passed (`test_answer_api.py`)
- Full suite: 31/31 passed (0 failures, 2 deprecation warnings unrelated to this task)

## Design Notes
- Correct answer (index == quiz_correct_index) marks `lesson.answered = True` and upserts a `KnowledgeNode` (mastery +1 if concept already exists, create with mastery=1 if new)
- Idempotent: re-answering a lesson that is already `answered=True` skips the upsert (no double-counting mastery)
- Wrong answer returns `correct: False` with no side effects
- The stub generator always sets `quiz_correct_index=1`, so the test sends `choice_index=1` for correct, `0` for wrong

## Concerns
- None. Implementation is straightforward and fully spec-compliant.
