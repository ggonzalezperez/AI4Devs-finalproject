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
~~Minor open: OpenAIImageGenerator missing response_format=b64_json~~ — **ANOTACIÓN ERRÓNEA,
cerrada el 27-09-2026**: `response_format` existe solo para dall-e-2/3. La familia gpt-image-*
—la única del catálogo— devuelve siempre b64_json y RECHAZA el parámetro con «Unknown parameter»,
así que añadirlo habría roto un adaptador que funciona, y el 400 lo habría absorbido el
best-effort en silencio. Verificado contra la documentación del proveedor, no de memoria.
No se añade nada; lo vigila `test_openai_does_not_send_response_format`.

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

Fix voz en contexto inseguro (commit 6f0890d, rama `fix/voz-contexto-seguro`): la Web Speech
API exige contexto seguro, así que servida por IP de la red local el navegador rechazaba sin
pedir permiso y la app insistía en «da permiso al micrófono». Ahora comprueba isSecureContext
y explica la causa real. Frontend 61 tests (31 ficheros), tsc limpio.

Autoenvío por voz (commit 7caee95): MicButton recibe onAutoSubmit y la pregunta dictada se
envía sola en Spark y LessonScreen. Retira la mitigación que RF-PLT-02 declaraba (editar antes
de enviar); el requisito queda actualizado con el riesgo aceptado. Frontend 63 tests.

Origen único + https en la red local (commit 3c40386): nginx enruta /api al backend y el
cliente usa ruta relativa, así que el bundle deja de llevar un host horneado — era la causa de
que la app no funcionase al abrirla por IP desde el móvil. Requisito previo del TLS: con dos
orígenes, el https habría roto la app por contenido mixto. nginx escucha en 443 (publicado en
5443) con CA propia; certs/ excluido del repositorio. Frontend 65 tests, backend 144, tsc y
ruff limpios. Verificado por curl sobre https: SPA 200, /api/health 200, login 401.

Endurecimiento del acceso (commits ae16a12, 798a1c4, 2dd0f2f, 3cbc0fd): la app se publicó en
internet y dos riesgos aceptados dejaron de serlo. Código de invitación opcional en el alta
(403 si no coincide; sin INVITE_CODE el registro sigue abierto, que es lo normal en casa) y
límite de intentos en los cinco endpoints de credenciales, con dos cubos —IP y cuenta— porque
la IP se falsifica tras un proxy y el email no. La IP se resuelve fail-closed: sin
CLIENT_IP_HEADER no se cree ninguna cabecera, y el backend pasa a escuchar solo en 127.0.0.1.
Contador propio en memoria (ADR-008) en vez de slowapi+Redis: el backend corre en un proceso.
Backend 179 tests, frontend 73 (la pantalla de login estrena cobertura), ruff y tsc limpios.
Verificado contra la VM: 403 sin código, 201 con el correcto, y corte al sexto login fallido
con Retry-After. Documentada además la infraestructura real de la demo (dominio, túnel como
contenedor, Cloudflare Access) en docs/entrega-2/demo-publica.md.

Primera sesión de uso real de la demo publicada (commits 5292576..). Tres fallos que solo
existen en la imagen de producción: caché sin cabeceras servía el bundle anterior (nginx no
recibió una sola petición en una hora mientras la pantalla se mostraba), VITE_API_URL horneada
en el .env de la VM apuntando a la IP de casa, y `??` en lugar de `||` para la base de la API,
que con la cadena vacía del Dockerfile dejaba las peticiones en /auth/register -> 405. Los dos
de código quedan con test.

Ilustraciones de 2,5 MB a 74 KB (commits posteriores): se piden a OpenAI en WebP con compresión
80 y calidad media —parámetros verificados en la documentación del proveedor—, el fichero se
guarda con la extensión de su formato real y el backend registra el tipo MIME webp. nginx sirve
/api/media sin buffering y con caché inmutable de un año, e index.html deja de cachearse. Las 8
imágenes existentes convertidas: el volumen pasó de 19 MB a 2 MB. Backend 182 tests, frontend 74.

Documentación: manual de uso nuevo para familias (docs/manual-usuario.md), manual de instalación
actualizado con INVITE_CODE, CLIENT_IP_HEADER y el aviso de no definir VITE_API_URL en un
despliegue con dominio.

# Task e3-cierre — fallos silenciosos y acceso de revisores (2026-09-27)

Brief: briefs/task-e3-cierre-brief.md · Informe: reports/task-e3-cierre-report.md · Veredicto PASA.

Tres correcciones del mismo patrón. (1) `image_provider` no se validaba contra el catálogo: un id
inventado se guardaba con 200 y caía al stub; ahora 422, como el de texto (RF-IA-06 ya lo declaraba).
(2) El panel no avisaba con proveedor de imagen elegido e imágenes apagadas; el aviso se deriva del
render, así que aparece también al ABRIR una configuración guardada así — el motivo por el que llevaba
invisible desde el 15-09. (3) La anotación de `response_format` del libro mayor era ERRÓNEA y
aplicarla habría roto el adaptador de OpenAI; cerrada con centinela y lectura defensiva.
Backend 182 → 186, frontend 74 → 76. Verificado con curl y en Chrome real, escritorio y móvil.

Cloudflare Access: la documentación afirmaba «One-time PIN, sin proveedor de identidad» y era FALSO
—solo estaba el IdP de Cloudflare, que exige cuenta propia—. Un revisor no habría podido entrar
jamás, tuviera su correo en la política o no. Añadido One-time PIN en Integraciones → Proveedores de
identidad; como la aplicación ya acepta todos los disponibles, quedó activo solo. Verificado de punta
a punta en incógnito. Corregir la afirmación en demo-publica.md.

Cuarto fallo silencioso, encontrado al fallar un alta en la demo: `apiFetch` llamaba a `JSON.parse`
antes de mirar `res.ok` y sin try/catch, así que cualquier cuerpo no-JSON reventaba con SyntaxError
—que no es ApiError— y las pantallas mostraban su mensaje genérico. El caso importante ni siquiera es
un error HTTP: `fetch` sigue las redirecciones, así que un corte de Access llega como 200 con HTML.
Ahora lanza ApiError con mensaje útil. Frontend 76 → 78. **La causa raíz del alta fallida sigue sin
conocerse**: funcionó al reintentar y la evidencia se perdió.
