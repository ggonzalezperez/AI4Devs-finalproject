# Task C4 Report — HTTP Provider Adapters + Factory

## Status: DONE

## Commit
- SHA: d408f32
- Subject: `feat(backend): HTTP provider adapters (Claude/Ollama active, others ready) + factory`
- Branch: `feature-entrega4-ai-config` (not pushed)

## Files Created
- `backend/app/services/ai_providers.py` — ClaudeGenerator, OllamaGenerator, OpenAICompatGenerator, GeminiGenerator, _parse_lesson helpers, build_generator factory
- `backend/tests/test_ai_providers.py` — 6 tests mocking httpx.post; no real network

## Test Summary
- Targeted: 6/6 passed (`tests/test_ai_providers.py`)
- Full suite: 52/52 passed
- No real HTTP calls; all mocked via `monkeypatch.setattr(httpx, "post", ...)`

## Ruff
- Clean (removed one unused import `ai_providers` from test file — the brief import was redundant since specific names were imported from the same module directly)

## Self-Review
- Factory fallback to StubLessonGenerator verified for: None config, provider="stub", missing/invalid key, unknown provider
- Claude/Ollama active; OpenAI/DeepSeek/Kimi/Gemini prepared (disabled in catalog)
- _decrypt_key swallows exceptions safely (bad key → None → fallback to stub)
- No concerns
