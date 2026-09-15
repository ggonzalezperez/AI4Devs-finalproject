# Task IMG-2a: Config de imagen en el panel de IA (backend)

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-imagenes`. SIN push. TDD.
Expón los ajustes de imagen (que IMG-1 añadió a `FamilyAIConfig`) en el endpoint `/family/ai-config` y el catálogo, para que la familia los configure (cifrando la clave de imagen). NO cambies la lógica de texto existente.

**Files:**
- Modify: `app/schemas/ai_config.py` (AIConfigRead + AIConfigUpdate con campos de imagen)
- Modify: `app/routers/ai_config.py` (_to_read, put_config, catalog)
- Test: `tests/test_ai_config.py` (o donde estén) — round-trip de imagen

## Step 1: `app/schemas/ai_config.py`
En `AIConfigRead` añade:
```python
    image_provider: str
    image_model: str | None
    image_base_url: str | None
    image_enabled: bool
    has_image_api_key: bool
```
En `AIConfigUpdate` añade:
```python
    image_provider: str = "none"
    image_model: str | None = None
    image_base_url: str | None = None
    image_api_key: str | None = None
    image_enabled: bool = False
```

## Step 2: `app/routers/ai_config.py`
- En `_to_read(cfg)`, añade los campos de imagen al `AIConfigRead(...)`:
```python
        image_provider=cfg.image_provider,
        image_model=cfg.image_model,
        image_base_url=cfg.image_base_url,
        image_enabled=cfg.image_enabled,
        has_image_api_key=bool(cfg.image_api_key_encrypted),
```
- En `put_config`, tras fijar los campos de texto y antes del `db.commit()`, fija los de imagen:
```python
    cfg.image_provider = payload.image_provider
    cfg.image_model = payload.image_model
    cfg.image_base_url = payload.image_base_url
    cfg.image_enabled = payload.image_enabled
    if payload.image_api_key is not None:
        if payload.image_api_key == "":
            cfg.image_api_key_encrypted = None
        else:
            try:
                cfg.image_api_key_encrypted = crypto.encrypt(
                    payload.image_api_key, get_settings().ai_config_key
                )
            except RuntimeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El servidor no tiene AI_CONFIG_KEY configurada para guardar claves.",
                )
```
- En el endpoint `catalog`, añade `image_providers` al dict devuelto:
```python
        "image_providers": ai_catalog.IMAGE_PROVIDERS,
```

## Step 3: Test
Reutiliza el patrón de token de familia existente. Verifica:
- GET `/family/ai-config` por defecto devuelve `image_provider == "none"`, `image_enabled == False`, `has_image_api_key == False`.
- PUT con `{... , "image_provider": "huggingface", "image_enabled": true, "image_api_key": "hf_test"}` (incluye los campos de texto requeridos: `tier`, `provider`) → 200; GET posterior devuelve `image_provider == "huggingface"`, `image_enabled == true`, `has_image_api_key == true`, y NO se devuelve la clave en claro.
- `GET /family/ai-config/catalog` incluye `image_providers` (lista no vacía con un id `"huggingface"`).
- Mantén verdes los tests existentes (el PUT ahora exige los nuevos campos con defaults, así que los tests antiguos que hacen PUT deben seguir pasando porque los campos de imagen tienen default; si alguno falla por validación, añade los defaults mínimos). `./.venv/Scripts/python.exe -m pytest -q` → todo PASS.

## Step 4: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): expose image generation settings in the AI config panel API"
```
