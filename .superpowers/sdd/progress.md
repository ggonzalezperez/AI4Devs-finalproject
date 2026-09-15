# Plan 2 — Frontend onboarding · Progress ledger

Branch: feature-entrega2-chispa
Base (merge-base with main): d7ff020

Task 1: complete (commit bb5ce15, scaffold, 1 test pass)
Task 2: complete (commit c703762, tokens+Button/ScreenCard, 3 tests pass)
Task 3: complete (commit f34a620, API client, 7 tests pass)
Task 4: complete (commit 550fbdd, auth API + session, 8 tests pass)
Task 5: complete (commit fecdb84, routing+ProtectedRoute, 10 tests pass)
Task 6: complete (commit 35af0af, create-family+login screens, 12 tests pass)
Task 7: complete (commit 2013cfd, explorer/who/PIN screens, 14 tests pass)
Task 8: complete (commit dc7371d, CORS+frontend CI+README, backend 20 + frontend 14 tests pass)
Task i18n: complete (commit 1732fe7, es/en + responsive theme, 16 tests)
Task UX: complete (commit 70038db, 4-digit PIN+confirmations+polish, 18 tests; verified end-to-end in browser)

# Plan 3 — Nucleo · Progress ledger
Branch: feature-entrega3-nucleo (local, no push)

Task A1: complete (commit 8ccbe4a, models+child auth+migration, 22 tests)
Task A2: complete (commit 53cf8ac, generator+moderation, 26 tests)
Task A3: complete (commit bfa2800, lessons endpoints, 29 tests)
Task A4: complete (commit 43b5bf3, answer+graph, 31 tests)
Task A5: complete (commit 8d7cc50, /me endpoints, 34 tests) — BACKEND NUCLEO DONE
Task B1: complete (commit 27fe94c, nucleo API client, 20 frontend tests)
Task B2: complete (commit 45834c4, Spark screen, 21 frontend tests pass)
Task B2: complete (commit 45834c4, Spark screen, 21 tests)
Task B3: complete (commit 670cd0c, Lesson+quiz screen, 22 tests)

# Plan 4 — IA multi-proveedor configurable + Docker · Progress ledger
Branch: feature-entrega4-ai-config (local, no push)


Task C1: complete (commits 782888e..6390413, review clean)
Task C1: complete (commit 6390413, crypto+FamilyAIConfig+migration, 36 tests)
Task C2: complete (commit 0c95a63, catalog+recommender+endpoints, 42 tests)
Task C3: complete (commit 890bae3, AI config GET/PUT encrypted, 46 tests)
Task C4: complete (commit d408f32, provider adapters+factory, 52 tests)
Task C5: complete (commit 3068cb7, lesson_service wired to family AI config + fallback, 55 tests) — BACKEND PLAN 4 DONE
--- Frontend Plan 4 (panel IA) ---
Task D1: complete (commit 5a22a5f, AI config API client)
Task D2: complete (commit f8c22a8, AI settings panel, 26 frontend tests)
Task E1: complete (commit 464253e, docker+manual). Security fixes commit c97eaba. LIVE CLAUDE TEST: PASS (lección real generada).
UX 1-3: complete+pushed (token split, child header+/me/profile+readability, onboarding hints). Verified in browser.

# Producto: Biblioteca de cuentos + aprobación parental (rama feature-cuentos)
Task S1: complete (commit 79e29aa, Story model+stub gen+migration, 59 tests)
Task S2+S3: complete (commit 643898d, story endpoints, 65 tests, ruff clean)
Task S4: complete (commit aa19ad8, child story library+reader, 28 tests)
Task S5: complete (commit c502e8d, family approval panel, 29 frontend tests)
Final review: SHIP (1 minor applied: reject keeps original text)
Fase A: avatares diseñados (b7a63d9 backend + 564c8f3 frontend) — subido
B1 lecciones ricas: 6a5a68b backend + 706d710 frontend — subido

# Task B2a — Conversational lesson threads
Task B2a: complete (commits b25ce93..b656075, spec PASS, quality Approved)
B2 chat: b656075 backend + 62111b7 frontend — conversación con contexto, islas auto, quiz opcional por turno — subido

Task B2c: complete (commits 62111b7..fe69f7b, spec PASS, quality Approved)
B2c islas-conversación: fe69f7b — pinchar isla abre su chat guardado — subido

Task B3-buscador: complete (commit 22d5715, archipelago search, 36 tests PASS, lint clean)

# Task QR — ConnectDevice screen (rama feature-infra-lan)
Task QR: complete (commits ccb43e3..fb83af2, spec PASS, quality Approved, 39/39 tests)

# Task IMG-1 — Image generation seam (rama feature-imagenes)
Task IMG-1: complete (commit fb83af2..771ac89, spec PASS, quality Approved, 88/88 tests)
Minor open: OpenAIImageGenerator missing response_format=b64_json (spec-faithful; brief omits it; best-effort swallows it)

# Task IMG-2b — Image config panel + lesson render (frontend, feature-imagenes)
Task IMG-2b: complete (commits 17f16ff..d4c642e, spec PASS, quality Approved, 40/40 tests)
Fase C imagen: 771ac89+fix + 17f16ff + d4c642e — costura imagen (HF/SDXL-local/OpenAI/Gemini), off por defecto, SSRF mitigado — fusionado a main
Fase C extra: TTS(774e38e) + animaciones + avatares-IA(d521723) — fusionado a main

# Task PWD-a — change password + recovery-code reset
Branch: feature-password
Base: 89e2f97

Task PWD-a: complete (commit 7076c9a, change password + recovery-code reset, 107 tests pass, review clean)


# Task PWD-b — Password UI (frontend, rama feature-password)
Base: 3203a89

Task PWD-b: complete (commits 5a09ac1..b9a4230, spec PASS, quality Approved, 46/46 tests)
Password: cambiar + recuperar (código 128-bit rotado) — fusionado a main
Imágenes: Pollinations sin clave + botón Guardar en panel — imagen real E2E OK — fusionado a main

# Entrega 2 — rama `entrega_2` (2026-09-14)

Metodología: estándares en `docs/estandares/` + 6 skills en `.claude/skills/` + TDD Guard
con reporters de pytest y vitest (adaptado de lidr-specboot y nizos/tdd-guard).

Auditoría doc↔código: 6 desviaciones cerradas (commit 40e9d3b) — moderación por palabra
completa, PIN validado en servidor, stub adaptado por edad, 409/502 del avatar, RF-CUE-01
corregido, deprecación + i18n + favicon. Backend 108 → 121.

Task panel-familia: complete — US5/US6 (RF-PLT-01), la última historia del MVP.
Endpoints `GET /children/{id}/profile` y `/knowledge` con token de familia (los `/me/*`
exigen token de niño por diseño). Backend 127 tests, frontend 52, ruff y tsc limpios,
curl y E2E verificados, 4 capturas en docs/entrega-2/evidencias/. Veredicto: PASA.
