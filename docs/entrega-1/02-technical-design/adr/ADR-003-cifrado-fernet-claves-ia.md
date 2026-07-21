# ADR-003 — Cifrado Fernet de las claves de IA (BYOK)

**Estado:** Aceptada (fase de diseño)

## Contexto

Las familias pueden aportar su propia clave de proveedor de IA (BYOK: Claude, OpenAI, DeepSeek, Kimi, Gemini, y claves de imagen). Esas claves son secretos sensibles que no deben guardarse en claro ni exponerse nunca en las respuestas de la API.

## Decisión

Cifrar las claves con **Fernet** (cifrado simétrico) usando la variable `AI_CONFIG_KEY` antes de persistirlas. La clave en claro **nunca se serializará**: la API solo expondrá banderas booleanas `has_api_key` / `has_image_api_key`. El descifrado ocurrirá solo en memoria, en el momento de construir el adaptador (función `_decrypt_key` del servicio de proveedores de IA).

## Alternativas consideradas

- **Guardar la clave en claro**: inaceptable; cualquier acceso a la BD o volcado expondría los secretos de la familia.
- **Secret manager externo** (Vault, KMS, etc.): sobredimensionado para una app autoalojada en un PC de casa; añade infraestructura y coste operativo.

## Consecuencias

- **Privacidad de las claves BYOK**: se almacenarán cifradas y nunca se devolverán al cliente.
- **Dependencia de `AI_CONFIG_KEY`**: si no está definida, cifrar fallará (respuesta **400**), forzando una configuración segura. El descifrado defensivo devolverá `None` ante error, cayendo al stub (coherente con ADR-001).

## Componentes de diseño

- Servicio `crypto` (`encrypt` / `decrypt` con Fernet).
- Servicio de proveedores de IA (`_decrypt_key`, uso de `get_settings().ai_config_key`).
- Router `/family/ai-config` (respuesta con `has_api_key` / `has_image_api_key`, sin la clave).
- `docker-compose.yml` (`AI_CONFIG_KEY` inyectada al backend).
