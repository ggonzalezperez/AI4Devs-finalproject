import { apiFetch } from "./client";
import type { TokenResponse } from "./auth";
import type { ChildProfile, KnowledgeNode } from "./nucleo";

export type Child = { id: number; name: string; birthdate: string; age: number; avatar: string; avatar_image_url: string | null };

export function listChildren() {
  return apiFetch<Child[]>("/children", { auth: true });
}

export function createChild(name: string, birthdate: string, pin: string, avatar: string) {
  return apiFetch<Child>("/children", {
    method: "POST",
    auth: true,
    body: { name, birthdate, pin, avatar },
  });
}

export function childLogin(childId: number, pin: string) {
  return apiFetch<TokenResponse>(`/children/${childId}/login`, {
    method: "POST",
    auth: true,
    body: { pin },
  });
}

/** Ficha de un hijo, leída por la FAMILIA. Los endpoints `/me/*` equivalentes
 *  exigen token de niño: son el espacio del niño, no el panel del adulto.
 *  El tipo de la ficha es el mismo que ve el niño, así que se reutiliza. */
export function getChildProfile(childId: number) {
  return apiFetch<ChildProfile>(`/children/${childId}/profile`, { auth: true });
}

export function getChildKnowledge(childId: number) {
  return apiFetch<KnowledgeNode[]>(`/children/${childId}/knowledge`, { auth: true });
}

export function generateChildAvatar(childId: number, description: string) {
  return apiFetch<Child>(`/children/${childId}/avatar/generate`, {
    method: "POST",
    auth: true,
    body: { description },
  });
}
