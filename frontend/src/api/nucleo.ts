import { apiFetch } from "./client";

export type ChildProfile = { name: string; age: number; islands: number; avatar: string; avatar_image_url: string | null };

export function getProfile() {
  return apiFetch<ChildProfile>("/me/profile", { auth: "child" });
}

export type Lesson = {
  id: number;
  curiosity: string;
  subject: string;
  concept: string;
  title: string;
  body: string;
  fun_fact: string;
  answered: boolean;
  quiz: { question: string; options: string[] };
  follow_ups: string[];
  image_url: string | null;
};

export type Suggestion = { curiosity: string; emoji: string };
export type AnswerResult = { correct: boolean; explanation: string; concept: string };
export type KnowledgeNode = { id: number; concept: string; subject: string; mastery: number; root_lesson_id: number | null };

export function createLesson(curiosity: string, subject?: string) {
  return apiFetch<Lesson>("/lessons", { method: "POST", auth: "child", body: { curiosity, subject } });
}

export function getLesson(id: number) {
  return apiFetch<Lesson>(`/lessons/${id}`, { auth: "child" });
}

export function getThread(lessonId: number) {
  return apiFetch<Lesson[]>(`/lessons/${lessonId}/thread`, { auth: "child" });
}

export function askInLesson(lessonId: number, curiosity: string) {
  return apiFetch<Lesson>(`/lessons/${lessonId}/ask`, {
    method: "POST",
    auth: "child",
    body: { curiosity },
  });
}

export function answerLesson(id: number, choiceIndex: number) {
  return apiFetch<AnswerResult>(`/lessons/${id}/answer`, {
    method: "POST",
    auth: "child",
    body: { choice_index: choiceIndex },
  });
}

export function getSuggestions() {
  return apiFetch<Suggestion[]>("/me/suggestions", { auth: "child" });
}

export function getKnowledge() {
  return apiFetch<KnowledgeNode[]>("/me/knowledge", { auth: "child" });
}
