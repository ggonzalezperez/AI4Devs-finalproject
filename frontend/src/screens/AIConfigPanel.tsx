import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getAIConfig,
  getCatalog,
  putAIConfig,
  recommendHardware,
  type AIConfig,
  type Catalog,
  type Recommendation,
} from "../api/aiConfig";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function AIConfigPanel() {
  const { t } = useI18n();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [provider, setProvider] = useState("stub");
  const [model, setModel] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [hasKey, setHasKey] = useState(false);
  const [imageProvider, setImageProvider] = useState("none");
  const [imageModel, setImageModel] = useState("");
  const [imageBaseUrl, setImageBaseUrl] = useState("");
  const [imageApiKey, setImageApiKey] = useState("");
  const [imageEnabled, setImageEnabled] = useState(false);
  const [hasImageKey, setHasImageKey] = useState(false);
  const [vram, setVram] = useState("");
  const [ram, setRam] = useState("");
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getCatalog().then(setCatalog).catch(() => undefined);
    getAIConfig()
      .then((c: AIConfig) => {
        setProvider(c.provider);
        setModel(c.model ?? "");
        setBaseUrl(c.base_url ?? "");
        setHasKey(c.has_api_key);
        setImageProvider(c.image_provider);
        setImageModel(c.image_model ?? "");
        setImageBaseUrl(c.image_base_url ?? "");
        setImageEnabled(c.image_enabled);
        setHasImageKey(c.has_image_api_key);
      })
      .catch(() => undefined);
  }, []);

  if (!catalog) {
    return (
      <ScreenCard>
        <p>…</p>
      </ScreenCard>
    );
  }

  const providers = catalog.providers;
  const current = providers.find((p) => p.id === provider);
  const tier = current?.tier ?? "free";
  const modelOptions =
    provider === "ollama" ? catalog.ollama_models.map((m) => m.id) : current?.models ?? [];

  const imageProviders = catalog.image_providers ?? [];
  const currentImg = imageProviders.find((p) => p.id === imageProvider);
  const imgModelOptions = currentImg?.models ?? [];

  async function save() {
    setError("");
    setSaved(false);
    try {
      const cfg = await putAIConfig({
        tier,
        provider,
        model: model || null,
        base_url: provider === "ollama" ? baseUrl || null : null,
        api_key: apiKey ? apiKey : undefined,
        image_provider: imageProvider,
        image_model: imageModel || null,
        image_base_url: currentImg?.needs_base_url ? imageBaseUrl || null : null,
        image_api_key: imageApiKey ? imageApiKey : undefined,
        image_enabled: imageEnabled,
      });
      setHasKey(cfg.has_api_key);
      setApiKey("");
      setHasImageKey(cfg.has_image_api_key);
      setImageApiKey("");
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("aiPanel.error"));
    }
  }

  async function doRecommend() {
    try {
      setRec(await recommendHardware(Number(vram) || 0, Number(ram) || 0));
    } catch {
      /* ignore */
    }
  }

  return (
    <ScreenCard>
      <Link to="/familia/explorar">←</Link>
      <h1>{t("aiPanel.title")}</h1>
      <p style={{ color: "#0a5a53", fontWeight: 600 }}>{t("aiPanel.subtitle")}</p>

      <div style={{ background: "rgba(255,255,255,.6)", borderRadius: 14, padding: "12px 14px", fontSize: 13, color: "#0a5a53", lineHeight: 1.5 }}>
        <div style={{ fontWeight: 700, marginBottom: 4 }}>{t("aiPanel.intro")}</div>
        <div>{t("aiPanel.tierFree")}</div>
        <div>{t("aiPanel.tierByok")}</div>
        <div>{t("aiPanel.tierManaged")}</div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 16, padding: 16 }}>
        <label>
          {t("aiPanel.provider")}
          <select
            value={provider}
            onChange={(e) => {
              setProvider(e.target.value);
              setModel("");
            }}
          >
            {providers.map((p) => (
              <option key={p.id} value={p.id} disabled={!p.enabled}>
                {p.label} ({p.tier}){p.enabled ? "" : ` — ${t("aiPanel.soon")}`}
              </option>
            ))}
          </select>
        </label>
        <p style={{ margin: "2px 0 0", fontSize: 12, color: "#0a5a53" }}>
          {provider === "ollama" ? t("aiPanel.localHelp") : current?.needs_key ? t("aiPanel.byokHelp") : t("aiPanel.freeHelp")}
        </p>

        {modelOptions.length > 0 && (
          <label>
            {t("aiPanel.model")}
            <select value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="">—</option>
              {modelOptions.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </label>
        )}

        {current?.needs_base_url && (
          <label>
            {t("aiPanel.baseUrl")}
            <input
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="http://localhost:11434"
            />
          </label>
        )}

        {current?.needs_key && (
          <>
            <label>
              {t("aiPanel.apiKey")}
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={hasKey ? t("aiPanel.apiKeySaved") : "sk-..."}
              />
            </label>
            <small style={{ color: "#0a5a53" }}>{t("aiPanel.keyNote")}</small>
          </>
        )}

        {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
        {saved && <p style={{ color: "var(--green)", fontWeight: 700, margin: 0 }}>{t("aiPanel.saved")} ✓</p>}
        <Button onClick={() => void save()}>{t("aiPanel.save")}</Button>
      </div>

      <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 16, padding: 16 }}>
        <strong>{t("aiPanel.imgTitle")}</strong>
        <small style={{ color: "#0a5a53" }}>{t("aiPanel.imgHelp")}</small>
        <label style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
          <input type="checkbox" checked={imageEnabled} onChange={(e) => setImageEnabled(e.target.checked)} />
          {t("aiPanel.imgEnable")}
        </label>
        <label>
          {t("aiPanel.provider")}
          <select value={imageProvider} onChange={(e) => { setImageProvider(e.target.value); setImageModel(""); }}>
            {imageProviders.map((p) => (
              <option key={p.id} value={p.id} disabled={!p.enabled}>
                {p.label}{p.enabled ? "" : ` — ${t("aiPanel.soon")}`}
              </option>
            ))}
          </select>
        </label>
        {imgModelOptions.length > 0 && (
          <label>
            {t("aiPanel.model")}
            <select value={imageModel} onChange={(e) => setImageModel(e.target.value)}>
              <option value="">—</option>
              {imgModelOptions.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </label>
        )}
        {currentImg?.needs_base_url && (
          <label>
            {t("aiPanel.baseUrl")}
            <input value={imageBaseUrl} onChange={(e) => setImageBaseUrl(e.target.value)} placeholder="http://localhost:7860" />
          </label>
        )}
        {currentImg?.needs_key && (
          <>
            <label>
              {t("aiPanel.apiKey")}
              <input
                type="password"
                value={imageApiKey}
                onChange={(e) => setImageApiKey(e.target.value)}
                placeholder={hasImageKey ? t("aiPanel.apiKeySaved") : "hf_... / sk-..."}
              />
            </label>
            <small style={{ color: "#0a5a53" }}>{t("aiPanel.keyNote")}</small>
          </>
        )}
        {imageProvider !== "none" && !currentImg?.needs_key && !currentImg?.needs_base_url && (
          <small style={{ color: "var(--green)", fontWeight: 700 }}>{t("aiPanel.imgNoSetup")}</small>
        )}
        {/* Se deriva del render, no del guardado: así avisa también al ABRIR una
            configuración que ya estaba así, que es como el fallo pasó inadvertido.
            `status` y no `alert`: es información sobre el estado, no un error del
            adulto, y `alert` está reservado aquí a los fallos de guardado. */}
        {imageProvider !== "none" && !imageEnabled && (
          <small role="status" style={{ color: "#8a5a00", fontWeight: 700 }}>
            {t("aiPanel.imgDisabledWarning")}
          </small>
        )}
        {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
        {saved && <p style={{ color: "var(--green)", fontWeight: 700, margin: 0 }}>{t("aiPanel.saved")} ✓</p>}
        <Button onClick={() => void save()}>{t("aiPanel.save")}</Button>
      </div>

      <div style={{ marginTop: 14, background: "#fff", borderRadius: 16, padding: 16 }}>
        <strong>{t("aiPanel.hardware")}</strong>
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <input
            aria-label={t("aiPanel.vram")}
            value={vram}
            onChange={(e) => setVram(e.target.value)}
            placeholder={t("aiPanel.vram")}
            inputMode="numeric"
          />
          <input
            aria-label={t("aiPanel.ram")}
            value={ram}
            onChange={(e) => setRam(e.target.value)}
            placeholder={t("aiPanel.ram")}
            inputMode="numeric"
          />
          <button onClick={() => void doRecommend()}>{t("aiPanel.recommend")}</button>
        </div>
        {rec && (
          <div style={{ marginTop: 8 }}>
            <div>
              {t("aiPanel.recommended")}: <strong>{rec.recommended}</strong>
            </div>
            <div style={{ fontSize: 13, color: "#0a5a53" }}>{rec.note}</div>
            <button
              onClick={() => {
                setProvider("ollama");
                setModel(rec.recommended);
              }}
              style={{ marginTop: 6, padding: "8px 12px" }}
            >
              {t("aiPanel.useThis")}
            </button>
          </div>
        )}
      </div>
    </ScreenCard>
  );
}
