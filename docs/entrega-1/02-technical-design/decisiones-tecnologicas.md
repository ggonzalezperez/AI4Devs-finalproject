# Decisiones tecnológicas — Chispa

> Entrega 1 · Diseño técnico (previo a la implementación)
> Cada elección propuesta se justifica frente al problema real: una **app familiar autoalojable**, **segura para menores**, con **IA opcional** y **sin lock-in** de proveedor.

## 1. Backend

| Tecnología | Versión | Por qué (orientado al problema) |
|------------|---------|---------------------------------|
| **Python** | 3.12 | Lenguaje maduro para IA y web; tipado moderno (`Mapped`, `str \| None`) que da seguridad sin ceremonia en un proyecto de un solo mantenedor. |
| **FastAPI** | ≥0.111 | API async con OpenAPI/Swagger automático y validación por Pydantic: contratos autodocumentados y menos código boilerplate para un backend que debe ser fácil de mantener en casa. |
| **SQLAlchemy** | ≥2.0 | ORM tipado (estilo `Mapped`/`mapped_column`) que abstrae Postgres y SQLite con el mismo código, clave para el modelo autoalojable dev↔prod. |
| **Alembic** | ≥1.13 | Migraciones versionadas y lineales; imprescindible para actualizar el PC de casa sin perder los datos de la familia (ver ADR-006). |
| **Pydantic** + **pydantic-settings** | ≥2.7 | Contratos de API validados y configuración por `.env`: separa secretos y ajustes del código, adecuado para despliegues caseros distintos. |
| **PyJWT** | ≥2.8 | JWT HS256 ligero, sin dependencias pesadas; permite el token tipado familia/niño (ver ADR-002) sin sesiones de servidor. |
| **passlib[bcrypt]** | — | Hash robusto de contraseñas (familia) y PIN (niño); estándar probado, nunca se guardan credenciales en claro. |
| **cryptography (Fernet)** | ≥42 | Cifrado simétrico de las claves de IA que aporta la familia (BYOK); privacidad sin montar un secret manager externo (ver ADR-003). |
| **httpx** | ≥0.27 | Cliente HTTP único para **todos** los proveedores de IA **sin SDKs**: menos dependencias, menos superficie de fallo y control total del request/parseo. |
| **psycopg[binary]** | — | Driver PostgreSQL para producción; binario para instalar sin toolchain de compilación en el equipo de casa. |
| **Ruff** | — | Lint rápido (line-length 100): calidad consistente con una sola herramienta. |
| **pytest** | — | Tests sobre SQLite en memoria: rápidos y sin infra, apoyan la evolución segura del código. |

**Arquitectura de código**: capas `routers → services → repositories → models` con schemas Pydantic como contrato. Los detalles de IA se aislarán tras dos seams (puerto/adaptador) para poder cambiar de proveedor o funcionar sin IA (ver ADR-001).

## 2. Frontend

| Tecnología | Versión | Por qué (orientado al problema) |
|------------|---------|---------------------------------|
| **React** | 18.3 | UI declarativa y ecosistema amplio; base sólida para 18 pantallas con dos flujos (familia y niño). |
| **TypeScript** | 5.5 (strict) | Tipado estricto que evita errores en tiempo de ejecución en una app usada por niños; el cliente `apiFetch<T>` propaga los tipos de la API. |
| **Vite** | 5.4 | Build y HMR muy rápidos: iteración ágil para un proyecto de máster con tiempo limitado. |
| **React Router** | 6.26 | Enrutado declarativo con `ProtectedRoute`; separa rutas públicas de las que exigen sesión familia. |
| **Vitest** + **Testing Library** | 2.0 | Tests de componentes cercanos al uso real, coherentes con el toolchain de Vite. |
| **qrcode.react** | — | Genera el QR para abrir la sesión del niño en tablet/móvil de casa; degrada con elegancia si el navegador no soporta la función (ver ADR-007). |
| **Sin framework CSS** | — | Un único `theme.css` con variables CSS (tokens del design system "Archipiélago") e inline styles: cero peso extra y control total del look, evitando dependencias que envejecen. |

**Nota de tooling**: `"lint"` en frontend equivaldrá a `tsc --noEmit` (comprobación de tipos como puerta de calidad).

## 3. Datos y despliegue

| Elección | Por qué (orientado al problema) |
|----------|---------------------------------|
| **PostgreSQL** (producción) | Motor robusto y fiable para los datos de la familia en el despliegue permanente del hogar. |
| **SQLite** (dev/tests) | Sin servidor, cero configuración; mismo ORM que Postgres → portabilidad total y tests instantáneos. |
| **Docker Compose** | Un `docker compose up` levanta `postgres + backend + frontend + ollama`. Es la piedra angular de la promesa **autoalojable**: cualquier familia lo corre en su PC. Ollama se expone solo en `127.0.0.1`; el backend lo alcanza por la red interna de Docker. |
| **Ollama** (IA local) | Permite IA **gratis y privada** en el propio hardware (sin enviar las preguntas del niño a la nube), con el catálogo `ai_catalog` recomendando modelo según VRAM/RAM. |

## 4. Principios transversales

- **Sin lock-in de proveedor**: la lógica de negocio dependerá de los puertos `LessonGenerator` / `ImageGenerator`, no de ningún SDK concreto. Cambiar de Claude a Ollama, DeepSeek o Gemini será cambiar la config de la familia.
- **IA opcional por defecto**: sin configuración, todo funcionará con el stub determinista, sin coste ni conexión externa.
- **Seguridad para menores como requisito, no añadido**: moderación de entrada, aprobación parental de cuentos, cifrado de claves y sesiones separadas familia/niño estarán en el núcleo del diseño.
- **Menos dependencias**: HTTP directo con `httpx`, CSS sin framework y JWT en vez de sesiones de servidor reducirán la superficie a mantener en un proyecto autoalojado.

Ver el detalle de cada decisión estructural en los [ADR](./adr/).
