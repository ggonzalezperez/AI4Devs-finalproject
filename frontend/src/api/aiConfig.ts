import { apiFetch } from "./client";

export type AIConfig = {
  tier: string;
  provider: string;
  model: string | null;
  base_url: string | null;
  has_api_key: boolean;
  monthly_quota: number;
  used_count: number;
  image_provider: string;
  image_model: string | null;
  image_base_url: string | null;
  image_enabled: boolean;
  has_image_api_key: boolean;
};

export type Provider = {
  id: string;
  label: string;
  tier: string;
  needs_key: boolean;
  needs_base_url: boolean;
  enabled: boolean;
  models: string[];
};

export type OllamaModel = {
  id: string;
  label: string;
  min_vram_gb: number;
  min_ram_gb: number;
  speed: string;
};

export type Catalog = {
  providers: Provider[];
  ollama_models: OllamaModel[];
  default_local_model: string;
  image_providers: Provider[];
};

export type Recommendation = {
  can_run_local: boolean;
  fits: string[];
  recommended: string;
  note: string;
};

export type AIConfigUpdate = {
  tier: string;
  provider: string;
  model?: string | null;
  base_url?: string | null;
  api_key?: string | null;
  image_provider?: string;
  image_model?: string | null;
  image_base_url?: string | null;
  image_api_key?: string | null;
  image_enabled?: boolean;
};

export function getAIConfig() {
  return apiFetch<AIConfig>("/family/ai-config", { auth: true });
}

export function putAIConfig(payload: AIConfigUpdate) {
  return apiFetch<AIConfig>("/family/ai-config", { method: "PUT", auth: true, body: payload });
}

export function getCatalog() {
  return apiFetch<Catalog>("/family/ai-config/catalog", { auth: true });
}

export function recommendHardware(vram_gb: number, ram_gb: number) {
  return apiFetch<Recommendation>("/family/ai-config/recommend", {
    method: "POST",
    auth: true,
    body: { vram_gb, ram_gb },
  });
}
