import { apiFetch } from "./client";

export type Story = { id: number; title: string; body: string; status: string };

// --- Niño (auth: "child") ---
export function createStory() {
  return apiFetch<Story>("/me/stories", { method: "POST", auth: "child" });
}

export function getMyStories() {
  return apiFetch<Story[]>("/me/stories", { auth: "child" });
}

export function getMyStory(id: number) {
  return apiFetch<Story>(`/me/stories/${id}`, { auth: "child" });
}

// --- Familia (auth: true) ---
export function getFamilyStories(statusFilter?: string) {
  const q = statusFilter ? `?status_filter=${statusFilter}` : "";
  return apiFetch<Story[]>(`/family/stories${q}`, { auth: true });
}

export function reviewStory(
  id: number,
  action: "approve" | "reject",
  title?: string,
  body?: string,
) {
  const payload: Record<string, unknown> = { action };
  if (title !== undefined) payload.title = title;
  if (body !== undefined) payload.body = body;
  return apiFetch<Story>(`/family/stories/${id}`, { method: "PUT", auth: true, body: payload });
}
