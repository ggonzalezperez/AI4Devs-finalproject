from app.services.ai_catalog import recommend_local


def test_recommend_high_end_gpu_fits_32b():
    r = recommend_local(vram_gb=24, ram_gb=64)
    assert r["can_run_local"] is True
    assert "deepseek-r1:32b" in r["fits"]
    assert r["recommended"] == "deepseek-r1:32b"


def test_recommend_low_gpu_falls_back():
    r = recommend_local(vram_gb=2, ram_gb=8)
    assert r["can_run_local"] is False
    assert r["recommended"] == "llama3.2:3b"


def test_recommend_midrange_gpu():
    r = recommend_local(vram_gb=8, ram_gb=16)
    assert r["can_run_local"] is True
    assert "qwen3:4b" in r["fits"]
    assert "deepseek-r1:32b" not in r["fits"]


def test_openai_is_enabled_with_current_models():
    """El adaptador de OpenAI ya existe y está cableado (OpenAICompatGenerator);
    solo el flag del catálogo lo mantenía oculto. Los ids de modelo deben ser los
    vigentes, no los de 2024."""
    from app.services.ai_catalog import PROVIDERS

    openai = next(p for p in PROVIDERS if p["id"] == "openai")
    assert openai["enabled"] is True
    assert openai["models"], "debe ofrecer al menos un modelo"
    assert not any(m.startswith("gpt-4") for m in openai["models"]), (
        "gpt-4o/gpt-4o-mini están obsoletos"
    )


def test_no_retired_model_ids_in_catalog():
    """Los ids de modelo caducan y el fallo es silencioso: la llamada revienta y
    el niño cae al stub sin que nadie sepa por qué. Verificados 09-2026 contra la
    documentación de cada proveedor.

    Retirados de verdad: la serie Imagen (apagada el 17-08-2026) y moonshot-v1
    (sunset 31-08-2026). Las generaciones gpt-4o, claude-*-4-6 y gemini-1.5 ya
    no son las vigentes.
    """
    from app.services.ai_catalog import IMAGE_PROVIDERS, PROVIDERS

    retirados = ("gpt-4o", "imagen-3", "moonshot-v1", "gemini-1.5", "claude-sonnet-4-6", "claude-opus-4-8")
    for grupo in (PROVIDERS, IMAGE_PROVIDERS):
        for p in grupo:
            for m in p["models"]:
                assert not m.startswith(retirados), f"{p['id']}: modelo caducado {m!r}"


def test_hardcoded_default_models_are_not_retired():
    """Los defaults del código son peores que los del catálogo si caducan: se
    usan cuando la familia NO elige modelo, así que fallan sin que nadie los haya
    seleccionado."""
    import inspect

    from app.services import ai_providers, image_providers

    retirados = ("gpt-image-1\"", "imagen-3", "gemini-1.5", "gpt-4o")
    for modulo in (ai_providers, image_providers):
        fuente = inspect.getsource(modulo)
        for marca in retirados:
            assert marca not in fuente, f"{modulo.__name__}: default caducado {marca!r}"


def test_provider_labels_do_not_name_retired_models():
    """Las etiquetas también envejecen. «OpenAI (gpt-image-1)» seguía nombrando
    un modelo retirado aunque su lista de modelos ya estuviera actualizada: al
    usuario le llega la etiqueta, no la lista."""
    from app.services.ai_catalog import IMAGE_PROVIDERS, PROVIDERS

    retirados = ("gpt-4o", "gpt-image-1)", "imagen-3", "moonshot-v1", "gemini-1.5")
    for grupo in (PROVIDERS, IMAGE_PROVIDERS):
        for p in grupo:
            for marca in retirados:
                assert marca not in p["label"], f"{p['id']}: etiqueta con modelo caducado ({marca})"
