# Demo E2E — Chispa

> Entrega 1 (documental) · Máster LIDR–AI4Devs
> **Guion de demostración previsto** de extremo a extremo (**camino feliz**) mapeado a pantallas: describe qué mostrará la demo cuando el MVP esté implementado y qué evidencias se capturarán en entregas posteriores.

---

## 1. Preparación prevista

1. Arrancar el entorno autoalojado: `docker compose up --build -d` (ver `docs/entrega-1/04-delivery/despliegue.md`).
2. Abrir el frontend en `http://localhost:5173`.
3. (Opcional) Tener a mano la API en `http://localhost:8000/docs` (Swagger) para mostrar el backend.

---

## 2. Guion de demo previsto (camino feliz)

Recorrido paso a paso por pantallas que se mostrará cuando el MVP esté implementado. Cada paso indica la **pantalla** y la **acción**.

| # | Pantalla | Acción | Resultado esperado |
|---|---|---|---|
| 1 | Registro / Crear familia | Crear una familia (cuenta de la persona adulta). | Familia creada; sesión iniciada en el panel de familia. |
| 2 | Código de recuperación | Se mostrará el **código de recuperación** al crear la familia. | Guardar el código (permitirá restablecer acceso sin email). |
| 3 | Panel de familia → Añadir explorador | Crear un perfil de niño/a ("explorador") con **PIN**. | Explorador añadido a la familia. |
| 4 | Acceso niño (selección de perfil + PIN) | Entrar como el explorador con su PIN. | Sesión del niño; entorno infantil. |
| 5 | Inicio del niño → "Encender la chispa" | Pulsar **encender la chispa** para empezar una actividad. | Se generará / abrirá una mini-lección. |
| 6 | Mini-lección | Leer la lección; usar **leer en voz alta** (TTS). | Contenido mostrado y narrado. |
| 7 | Reto / Quiz | Responder el reto o quiz asociado a la lección. | Feedback de la respuesta; progreso registrado. |
| 8 | Archipiélago (mapa) | Al completar, ver la **isla** generada en el archipiélago. | Nueva isla visible en el mapa de progreso. |
| 9 | Archipiélago → Buscar isla | Buscar una isla y **reabrir el chat** de esa lección. | Se recuperará la conversación / lección anterior. |
| 10 | Crear cuento | El niño solicitará **crear un cuento**. | Cuento generado (texto + imagen). |
| 11 | Panel de familia → Aprobar cuento | La persona adulta **aprobará** el cuento. | Cuento marcado como aprobado / visible para el niño. |
| 12 | Panel de familia → ⚙️ Configurar IA | Configurar proveedor de IA: **Claude (BYOK)** u **Ollama local**. | Clave (si Claude) guardada **cifrada**; o modelo Ollama seleccionado. |
| 13 | Panel de familia → 📱 Conectar móvil | Abrir "Conectar móvil": mostrará URL + **QR**. | Escanear el QR desde el móvil (misma WiFi) y abrir Chispa. |

> El camino feliz completo demostrará: onboarding familiar, control parental (PIN + aprobación de cuentos), bucle de aprendizaje (lección → quiz → isla), IA configurable y acceso multi-dispositivo.

---

## 3. Evidencias a capturar (entregas posteriores)

Material a producir cuando el MVP esté implementado. **Aún no existen**; no deben presentarse como capturadas. Se capturarán y adjuntarán en las entregas posteriores:

1. **Capturas por pantalla** de cada paso del §2 (crear familia, PIN, encender la chispa, isla, cuento aprobado, QR).
2. **Vídeo de la demo E2E** (2–4 min) recorriendo el camino feliz completo.
3. **Captura de Swagger** mostrando los endpoints principales de la API.
4. **Captura del run de CI** en GitHub Actions (backend: ruff + pytest / frontend: tsc + vitest).
5. **Captura de una lección generada** por el proveedor de IA y de una **imagen generada** de extremo a extremo, presentadas visualmente.
6. **Grabación de "Conectar móvil"** escaneando el QR desde un dispositivo real.

---

## Referencias

- `docs/entrega-1/04-delivery/despliegue.md`
- `docs/MANUAL.md` · `README.md`
- `.github/workflows/ci.yml`
