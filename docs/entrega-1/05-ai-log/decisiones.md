# Decisiones de IA (AI-LOG) — Chispa

> Uso previsto de IA · Entrega 1 · Máster LIDR–AI4Devs
> Este documento define **la bitácora de IA que se mantendrá** durante el desarrollo, en el
> formato de la guía §5.6. Cada entrada documentará el ciclo
> **revisión → corrección → decisión justificada**, que es la evidencia del uso estructurado
> y responsable de la IA.
>
> **Estado:** en la Entrega 1 (documental) todavía no hay código, así que la bitácora aún no
> tiene entradas reales. Aquí se fija el **formato**, se incluye **un ejemplo ilustrativo**
> claramente marcado como plantilla y se listan los **temas de decisión** que la bitácora
> cubrirá. El registro completo se irá rellenando durante las **Entregas 2 y 3**, a medida
> que cada tarea se implemente y revise.

## 1. Formato de cada entrada (guía §5.6)

Cada registro **AI-LOG-00X** seguirá esta plantilla:

- **Fecha** — de la interacción con IA (se anotará el commit como ancla verificable).
- **Objetivo** — qué se le pidió a la IA.
- **Herramienta/modelo** — Claude Code + skills empleadas; proveedor en runtime si aplica.
- **Entrada** — contexto suministrado (brief, PRD, restricciones).
- **Salida** — qué produjo la IA.
- **Validaciones** — tests, lint, revisión de spec/calidad, migración segura.
- **Problemas detectados** — errores o alucinaciones encontrados en la revisión.
- **Corrección** — cambio manual o ajuste aplicado.
- **Decisión** — aceptado / aceptado con hallazgo abierto / desviación justificada, y por qué.

## 2. Ejemplo ilustrativo (PLANTILLA — no es una decisión ya tomada)

> El siguiente registro es un **ejemplo de referencia** con el estilo del AI-LOG-007 de la
> guía §5.6. Sirve para mostrar el nivel de detalle esperado; **no** documenta una decisión
> real del proyecto. Las entradas reales se añadirán en las Entregas 2 y 3.

### AI-LOG-000 (ejemplo) — Costura de IA con fallback seguro (generador de lecciones)

- **Fecha:** *(se anotará cuando se implemente)* · commit *(SHA como ancla)*
- **Objetivo:** Enchufar un proveedor de IA real por familia sin que un fallo del proveedor
  llegue nunca al niño.
- **Herramienta/modelo:** Claude Code (skills `test-driven-development`,
  `subagent-driven-development`); proveedor en runtime configurable.
- **Entrada:** Brief de adaptadores HTTP + fábrica, y brief de cableado del servicio de
  lecciones a la config de familia con fallback.
- **Salida:** Una fábrica `build_generator(cfg)` que devuelve el adaptador configurado; el
  servicio intentaría `generator.generate(...)` y, ante **cualquier** excepción, caería a un
  `StubLessonGenerator` determinista.
- **Validaciones:** Tests dirigidos + suite completa en verde; `ruff` limpio; sin llamadas
  HTTP reales (mock con `monkeypatch`); además, una prueba funcional real contra el proveedor.
- **Problemas detectados:** *(ejemplo)* el `monkeypatch` de la fábrica no surtiría efecto si
  se invocara por ruta totalmente cualificada.
- **Corrección:** Importar la fábrica al **namespace del módulo** que la usa para que el
  parcheo de tests funcione.
- **Decisión:** **Aceptado.** El fallback silencioso hacia el stub sería deliberado: el niño
  nunca vería un error del proveedor (continuidad de la experiencia).

## 3. Temas de decisión que la bitácora cubrirá

Durante las Entregas 2 y 3 se prevé registrar, como mínimo, entradas AI-LOG para estas
decisiones de diseño (se listan como **temas a documentar**, no como hechos consumados):

| Tema previsto | Qué decisión de IA se registrará |
|---|---|
| **Costura de IA + fallback seguro** | Integrar el proveedor tras una interfaz (*seam*) con degradación a stub determinista si falla o no está configurado |
| **Conversación en hilos / grafo de conocimiento** | Cómo la lección se convierte en conversación con contexto y cómo/cuándo se crea la "isla" en el archipiélago |
| **Aprobación parental de cuentos** | Flujo aprobar/editar/rechazar; el rechazo debe conservar el texto original para trazabilidad |
| **Config de IA por familia con clave cifrada** | Cifrado de la clave de API (Fernet), sin almacenarla en claro; clave inválida ⇒ fallback seguro |
| **Recuperación de contraseña sin email** | Código de recuperación de un solo uso (solo se guarda su hash) y protección **anti-enumeración** de cuentas |
| **Mitigación de SSRF en endpoint de imagen local** | Validar la URL antes de cualquier petición saliente; permitir LAN/localhost (uso legítimo) y bloquear direcciones link-local |
| **Aislamiento entre familias** | Guards de token y filtrado por `family_id`; el niño solo ve contenido `approved` |
| **JWT tipado** | Separar y verificar el tipo de token (niño ↔ familia) para evitar escaladas de privilegio |
| **Validación funcional real (E2E)** | Contrastar la integración de IA e imagen contra un proveedor vivo, más allá de los mocks |
| **Hallazgos de calidad abiertos** | Registrar deuda técnica no bloqueante (p. ej. `except` genérico sin logging, opción de proveedor no ideal) como hallazgo documentado |

Cada uno de estos temas generará una o varias entradas con el formato de la sección 1,
reflejando el ciclo real de revisión y corrección cuando la tarea se implemente.

---

# 4. Entradas reales — jornada del 14 de septiembre de 2026

A partir de aquí la bitácora deja de ser previsión y pasa a ser registro. Se anotan los aciertos y,
sobre todo, **los errores del modelo que fueron detectados y corregidos**: una bitácora donde la IA
nunca se equivoca no demuestra que hubo validación, demuestra que no la hubo.

## AI-LOG-001 · 14-09-2026 · validación

- **Objetivo:** contrastar `docs/entrega-1/` completo contra el código, requisito a requisito.
- **Herramienta/modelo:** Claude Code (Opus) con la skill propia `chispa-auditoria`.
- **Entrada:** los 32 RF, los 25 contratos de API, las 7 entidades y la matriz de trazabilidad.
- **Salida:** 1 requisito sin implementar (`RF-PLT-01`, el panel de familia) y 6 divergencias entre
  lo documentado y lo construido.
- **Validaciones:** cada hallazgo con su `fichero:línea`; los falsos positivos de moderación se
  comprobaron **ejecutando** la función, no leyéndola; el cruce de tests documentados contra tests
  reales se hizo con `grep`, no de memoria.
- **Decisión:** **Aceptado.** Las 6 divergencias se cerraron en el commit `32703f9`.

## AI-LOG-002 · 14-09-2026 · corrección manual sobre salida de IA

- **Objetivo:** que la moderación deje de bloquear curiosidades legítimas («armadura», «armario»,
  «Armada Invencible» caían por contener la subcadena «arma»).
- **Salida inicial del modelo:** sustituir la comparación por subcadena por comparación de
  **palabra completa**, enumerando a mano las variantes que sí deben bloquearse.
- **Problema detectado:** la **revisión adversaria** sobre el propio cambio encontró que la
  enumeración manual dejaba fuera conjugaciones y derivados. «matarte», «matarnos», «suicidar»,
  «suicidas», «drogadicto», «drogar», «pornograficos», «sexualidad» y «armamento» **dejaron de
  bloquearse**, y la versión anterior sí los paraba. Se arregló un agujero abriendo el contrario.
- **Cómo se detectó:** ejecutando la función contra una lista de formas derivadas que la versión
  por subcadena bloqueaba. No se dedujo leyendo el código.
- **Corrección:** dos listas en lugar de una — raíces por **prefijo** donde no hay colisión con
  vocabulario inocente (`suicid`, `drog`, `porno`, `matar`, `asesin`, `violen`, `sexual`) y
  **palabra completa** donde sí la hay (`arma`, `armas`, `armamento`, `sexo`).
- **Validaciones:** 21 tests, verificando las **dos** direcciones: 9 formas derivadas vuelven a
  bloquearse y 10 curiosidades inocentes siguen pasando (armadura, armazón, armadillo, matorral,
  violonchelo, armonía).
- **Decisión:** **Aceptado tras corrección** (commit `d96f452`).
- **Lección:** enumerar variantes a mano siempre deja conjugaciones fuera. Cuando un cambio de
  criterio de coincidencia arregla falsos positivos, hay que medir **explícitamente** si abre falsos
  negativos, porque el test que lo delata no existe todavía.

## AI-LOG-003 · 14-09-2026 · decisión

- **Objetivo:** implementar el panel de familia (US5/US6).
- **Problema detectado:** la historia daba por supuesto que el panel se serviría desde los endpoints
  `/me/*`, pero ésos exigen token `child` por diseño (`ADR-002`, JWT tipado). Seguir la historia al
  pie de la letra habría exigido dar a la familia acceso a endpoints de niño, rompiendo una garantía
  de seguridad documentada.
- **Decisión:** **se corrigió la historia, no la seguridad.** Se añadieron
  `GET /children/{id}/profile` y `GET /children/{id}/knowledge` con token de familia, y se anotó la
  corrección en la propia HU para que quede rastro de por qué cambió.
- **Validaciones:** 5 tests de backend incluyendo 404 cruzado y 401 por token de niño; `curl` real
  contra `uvicorn` y contra el stack de Docker; E2E en navegador con el selector de hermanos.

## AI-LOG-004 · 14-09-2026 · validación

- **Objetivo:** comprobar que la capa de obligación de TDD funciona de verdad.
- **Salida:** `tdd-guard` **bloqueó al agente tres veces** durante la jornada: al intentar añadir
  tres tests de golpe en lugar de uno, al escribir `build_profile` antes de tener un test que lo
  exigiera, y al crear el componente `FamilyPanel` completo sin test previo en rojo.
- **Decisión:** **Aceptado.** Los bloqueos se acataron escribiendo antes el test correspondiente. En
  el segundo caso el hook tenía razón sólo a medias —era una extracción de código ya probado— pero
  el test unitario que obligó a escribir para el helper compartido aporta valor por sí mismo.
- **Relevancia:** el TDD deja de ser una intención declarada en un documento y pasa a ser una
  barrera que el programa aplica, incluida sobre el propio agente.

## AI-LOG-005 · 14-09-2026 · hallazgo no detectado por la auditoría

- **Qué pasó:** `FamilyAIConfig.monthly_quota` se lee y se serializa, y `used_count` se incrementa
  en dos puntos de `lesson_service.py`, pero **el límite no se comprueba en ningún sitio**. El
  contador existe; la cuota no hace nada.
- **Cómo se detectó:** **no** lo encontró la auditoría automática, que se centró en contrastar
  requisitos contra código. Apareció al leer un documento de diseño redactado en otra sesión para la
  Entrega 3, que lo señalaba como prerrequisito.
- **Decisión:** **Aplazado** a la Entrega 3, donde la cuota es necesaria de verdad (demo pública con
  IA de pago). Queda declarado como deuda conocida en `docs/entrega-2/estado-implementacion.md`.
- **Lección:** una auditoría que contrasta *requisitos contra código* no ve lo que **ningún
  requisito reclama**. Un campo del modelo sin requisito asociado es un punto ciego del método.

## AI-LOG-006 · 14-09-2026 · corrección manual + hallazgo de infraestructura

- **Qué pasó:** el primer *push* de la Entrega 2 dejó la CI **en rojo** con 146 errores de `ruff`,
  mientras en local `ruff check .` pasaba limpio.
- **Causa:** no era el código. `pyproject.toml` declaraba `ruff>=0.5`, un rango abierto: la máquina
  local tenía **0.15.20** y la CI instalaba **0.16.7**, cuyas reglas por defecto son distintas. Los
  ficheros señalados no se habían tocado desde julio. Era un fallo **latente** que habría saltado en
  cualquier *push* desde que salió la 0.16.
- **Decisión:** en lugar de fijar el linter a la versión vieja (que esconde el problema), se
  declararon las reglas **explícitamente** (`select = ["E","W","F","I","UP","B"]`) y se fijó la
  versión exacta, para que local y CI ejecuten lo mismo. De los 146 avisos:
  - **52 eran falsos positivos**: `B008` marca llamadas en argumentos por defecto, pero
    `Depends(...)` en la firma **es** el idioma de FastAPI. Resuelto con `extend-immutable-calls`.
  - **63 eran `E501`** (longitud de línea), que el proyecto nunca aplicó: excluida a propósito y
    documentado el porqué.
  - **94 se arreglaron automáticamente** (orden de imports, sintaxis moderna).
  - **9 a mano**, entre ellos 7 `B904` (encadenar excepciones) y un `pytest.raises(Exception)`
    demasiado ancho.
- **Error del modelo durante la corrección:** el primer intento de arreglar los `B904` usó una
  expresión regular amplia y añadió `from None` a **16** `raise`, no a los 5 que estaban dentro de un
  `except`. Fuera de un `except` eso es legal pero engañoso: declara que se suprime una causa que no
  existe. Detectado al comparar el recuento aplicado con el esperado; revertido y rehecho dirigido
  por número de línea.
- **Validaciones:** `ruff` limpio, 136 tests en verde, y los cinco `from None` comprobados en su
  contexto.
- **Lección:** un rango de versión abierto en una herramienta de calidad convierte la CI en algo no
  reproducible. Y cuando una corrección masiva se aplica con una regla amplia, hay que **contar** lo
  que ha tocado, no confiar en que el linter quede verde: el linter solo mira lo que sabe mirar.

## AI-LOG-007 · 15-09-2026 · validación + hallazgo

- **Objetivo:** habilitar OpenAI como proveedor de texto y actualizar los identificadores de modelo
  de todo el catálogo.
- **Cómo se resolvió:** **verificando contra la documentación de cada proveedor**, no de memoria.
  El conocimiento del modelo tiene fecha de corte y los identificadores caducan más rápido que eso.
- **Hallazgos:**
  - OpenAI **no necesitaba código**: `OpenAICompatGenerator` ya existía y estaba cableado en
    `build_generator`; solo un flag `enabled: False` lo ocultaba.
  - **La serie Imagen de Google se apagó el 17-08-2026** y el catálogo seguía ofreciéndola, además
    de usarla como valor por defecto en `image_providers.py`.
  - **La serie `moonshot-v1` de Kimi se retiró el 31-08-2026.**
  - `gpt-4o`, `gemini-1.5-*`, `claude-sonnet-4-6` y `claude-opus-4-8` habían dejado de ser la
    generación vigente.
  - Los **valores por defecto del código** estaban peor que el catálogo: se usan cuando la familia
    no elige modelo, así que fallan sin que nadie los haya seleccionado.
- **Por qué importa más de lo que parece:** un identificador caducado **no da error visible**. La
  llamada al proveedor falla, el `except` la absorbe y el niño recibe una lección del stub. La
  familia creería estar usando la IA que configuró y pagando por ella.
- **Decisión:** dos tests nuevos que fallan si aparece un identificador de una lista de retirados,
  uno para el catálogo y otro para los valores por defecto del código. No evitan que caduquen, pero
  convierten un fallo silencioso en uno ruidoso la próxima vez que alguien los revise.
- **Excepción razonada:** los modelos de **Ollama no se tocaron**. Son locales: un tag antiguo se
  sigue pudiendo descargar, así que no caducan como los de una API de pago. Cambiarlos sin datos de
  hardware reales habría empeorado el recomendador.

## AI-LOG-008 · 21-09-2026 · decisión + corrección manual

**Contexto:** la aplicación se publicó en internet (`chispa.chispalearn.com`) y el registro estaba
abierto y sin límite de intentos. Se implementaron el código de invitación y el límite, dirigiendo a
la IA con un plan previo (exploración en paralelo → diseño → plan aprobado → TDD).

- **Qué pasó:** el diseño propuesto por el modelo daba por bueno leer `X-Forwarded-For` para conocer
  la IP del cliente detrás del túnel. Al revisarlo se vio que eso convertía el control en
  decorativo: con el puerto 8000 publicado en la LAN, cualquiera falsifica una IP por intento y el
  cubo por IP deja de contar nada.
- **Cómo se detectó:** revisando el propio plan antes de implementar, no por un test. El diseño
  mencionaba el riesgo en un párrafo pero proponía la variable con valor por defecto activo.
- **Corrección:** el comportamiento se invirtió a **fail-closed**: sin `CLIENT_IP_HEADER` no se cree
  ninguna cabecera, y el despliegue público se cambió para atar el backend a `127.0.0.1:8000`. Hay
  un test que lo sujeta (`test_uses_the_socket_peer_when_no_header_is_configured`), y el cubo por
  cuenta —que no es falsificable— actúa como segunda línea.
- **Lección:** cuando un control de seguridad depende de un dato que viene del cliente, el valor por
  defecto tiene que ser *no fiarse*. Un plan que menciona el riesgo pero deja el valor inseguro por
  defecto es peor que uno que no lo menciona, porque parece revisado.

## AI-LOG-009 · 21-09-2026 · validación

- **Qué pasó:** el limitador necesita saber a qué cuenta imputar el intento, y el email viaja en el
  cuerpo de la petición. Leerlo en una dependencia, antes de que Pydantic valide el cuerpo, es el
  punto frágil del diseño: si el cuerpo no quedara cacheado, todos los endpoints empezarían a ver
  cuerpos vacíos y a devolver 422 aunque la petición fuese correcta.
- **Cómo se detectó:** no se detectó un fallo, se **previno**: se escribió un test de regresión
  (`test_a_malformed_json_body_still_returns_422`) antes de dar el diseño por bueno, y los ~20 tests
  de login y registro existentes hacen de red adicional.
- **Corrección:** ninguna; el comportamiento de Starlette es el esperado. Queda escrito en ADR-008
  por qué funciona, para que quien lo toque sepa qué está sosteniendo.
- **Lección:** cuando una pieza depende de un detalle de implementación de un framework, el test que
  lo sujeta vale más que el comentario que lo explica. Aquí se escribieron los dos.

## AI-LOG-010 · 21-09-2026 · decisión

- **Qué pasó:** el túnel de Cloudflare no pudo instalarse como servicio del sistema en la VM porque
  **se había perdido la contraseña de `sudo`** del usuario. La alternativa inmediata era recuperarla
  por consola VNC, en modo de recuperación, en mitad del despliegue.
- **Decisión:** no arreglar eso entonces. El conector se levantó como **un contenedor más** del
  mismo `docker compose`, con `restart: unless-stopped`. No necesita root, se gestiona con los
  mismos comandos que el resto de la aplicación y sobrevive a reinicios igual que un servicio.
- **Efecto secundario que hubo que entender:** al correr dentro de Docker, `localhost` es el propio
  conector, así que el destino del túnel es `frontend:80` y no `localhost:5173`. Un despiste ahí
  deja la web caída sin ningún error evidente.
- **Lección:** un bloqueo operativo no siempre exige resolverse en el momento; a veces la vía
  alternativa es mejor que la original. Queda anotado como deuda con su disparador, para que no se
  olvide que la VM sigue sin poder actualizarse.

## AI-LOG-011 · 21-09-2026 · hallazgo · tres fallos que solo existen en producción

**Contexto:** primera sesión de uso real de la aplicación publicada, desde un móvil y por el dominio
propio. Los 182 tests estaban verdes y ninguno de los tres fallos aparecía en desarrollo.

- **Qué pasó, en cadena:**
  1. El formulario de alta salía **sin el campo de código de invitación**. Causa: nginx no enviaba
     ninguna cabecera de caché, así que el navegador y el borde de Cloudflare conservaban el bundle
     del despliegue anterior. Los registros lo demostraron: nginx **no recibió ni una petición** en
     una hora mientras la pantalla se mostraba.
  2. Corregido eso, el alta fallaba con un error de red. El `.env` de la VM conservaba
     `VITE_API_URL=http://192.168.31.18:8000` de cuando se probaba por la red de casa. Esa variable
     hornea la dirección dentro del bundle: la app publicada llamaba a otra máquina, por `http`
     desde una página `https`, y a un puerto que se había cerrado esa misma tarde.
  3. Corregido eso, llegó un **405**. El cliente calculaba la base de la API con
     `import.meta.env.VITE_API_URL ?? "/api"`, y el `Dockerfile` define la variable como **cadena
     vacía**. `??` solo cubre `undefined`, así que la base quedaba en `""` y las peticiones salían a
     `/auth/register`, que nginx sirve como fichero estático.
- **Cómo se detectaron:** los dos primeros leyendo los registros del servidor y comparando con lo
  que mostraba la pantalla; el tercero con el panel de red del navegador, donde la presencia de una
  petición **preflight** delataba que la llamada iba a otro origen.
- **Corrección:** cabeceras de caché en nginx (`no-store` para `index.html`, inmutable para los
  assets), retirada de `VITE_API_URL` del despliegue, y `?.trim() || "/api"` en el cliente, con un
  test que recarga el módulo con la variable vacía.
- **Lección:** los tres comparten forma. Son **diferencias entre el entorno de desarrollo y la
  imagen de producción**, no errores de lógica: en desarrollo la variable no existe, el servidor no
  cachea y no hay proxy delante. Ninguna suite de tests los habría encontrado sin ejecutar la
  aplicación desplegada. La verificación contra el despliegue real no es un extra del método: es
  donde vive esta clase de fallo.

## AI-LOG-012 · 21-09-2026 · validación + decisión

- **Qué pasó:** las ilustraciones pesaban entre 1,5 y 3 MB. Nadie lo había notado porque en local
  la red no duele; en el móvil son megas por lección. La causa: a OpenAI no se le pedían ni formato
  ni calidad, y por defecto devuelve PNG al máximo.
- **Cómo se detectó:** un aviso de nginx en los registros —*an upstream response is buffered to a
  temporary file*— al revisar si había errores. No era un error, sino la señal de que las respuestas
  no cabían en el búfer.
- **Decisión y verificación:** se piden los tres parámetros que el modelo admite (`output_format`
  webp, `output_compression` 80, `quality` medium), **confirmados contra la documentación del
  proveedor y no de memoria**, siguiendo la lección de AI-LOG-007. Resultado medido: **74 KB frente
  a 2,5 MB**, 34 veces menos, sin pérdida visible. Las 8 ilustraciones ya generadas se convirtieron
  y el volumen bajó de 19 MB a 2 MB.
- **Efecto colateral que hubo que cazar:** el fichero se guardaba siempre como `.png` viniera lo que
  viniera, y el contenedor no conocía el tipo MIME `webp`, así que las imágenes se servían como
  `application/octet-stream`. Dos correcciones más, cada una con su test.
- **Lección:** revisar los registros buscando errores encontró algo que no era un error. Los avisos
  de infraestructura describen costes que el código no declara en ninguna parte.
