import type { ReactNode } from "react";
import { assetUrl } from "../api/client";

/**
 * Set de avatares diseñado para Chispa. Estilo plano y amable, dentro de la
 * identidad (coral/teal/ámbar), sobre una baldosa redondeada con un tinte suave.
 * Cada avatar es SVG (nítido a cualquier tamaño) y autocontenido.
 *
 * Temas que gustan a los niños: animales, espacio y deportes.
 */

export type AvatarId =
  | "fox"
  | "cat"
  | "panda"
  | "owl"
  | "frog"
  | "lion"
  | "rocket"
  | "ball"
  | "dino";

type AvatarDef = { id: AvatarId; label: string; bg: string; art: ReactNode };

const DARK = "#08433e";

const DEFS: Record<AvatarId, AvatarDef> = {
  fox: {
    id: "fox",
    label: "Zorro",
    bg: "#ffe8de",
    art: (
      <g>
        <polygon points="18,16 27,27 13,30" fill="#ff7a59" />
        <polygon points="46,16 37,27 51,30" fill="#ff7a59" />
        <circle cx="32" cy="34" r="15" fill="#ff7a59" />
        <polygon points="22,37 42,37 32,52" fill="#fff" />
        <circle cx="26" cy="32" r="2.4" fill={DARK} />
        <circle cx="38" cy="32" r="2.4" fill={DARK} />
        <circle cx="32" cy="42" r="2.6" fill={DARK} />
      </g>
    ),
  },
  cat: {
    id: "cat",
    label: "Gato",
    bg: "#e6f2f0",
    art: (
      <g>
        <polygon points="18,16 25,29 12,28" fill="#0e837b" />
        <polygon points="46,16 39,29 52,28" fill="#0e837b" />
        <circle cx="32" cy="34" r="15" fill="#0e837b" />
        <circle cx="26" cy="32" r="2.4" fill="#fff" />
        <circle cx="38" cy="32" r="2.4" fill="#fff" />
        <circle cx="32" cy="38" r="2.2" fill="#ff7a59" />
        <g stroke="#fff" strokeWidth="1.4" strokeLinecap="round">
          <line x1="31" y1="39" x2="21" y2="41" />
          <line x1="33" y1="39" x2="43" y2="41" />
        </g>
      </g>
    ),
  },
  panda: {
    id: "panda",
    label: "Panda",
    bg: "#eef1f0",
    art: (
      <g>
        <circle cx="21" cy="23" r="6" fill={DARK} />
        <circle cx="43" cy="23" r="6" fill={DARK} />
        <circle cx="32" cy="35" r="15" fill="#fff" />
        <ellipse cx="25" cy="33" rx="4" ry="5.2" fill={DARK} />
        <ellipse cx="39" cy="33" rx="4" ry="5.2" fill={DARK} />
        <circle cx="25" cy="33" r="1.5" fill="#fff" />
        <circle cx="39" cy="33" r="1.5" fill="#fff" />
        <circle cx="32" cy="41" r="2" fill={DARK} />
      </g>
    ),
  },
  owl: {
    id: "owl",
    label: "Búho",
    bg: "#f3ecdd",
    art: (
      <g>
        <polygon points="20,18 27,11 29,21" fill="#0e5b56" />
        <polygon points="44,18 37,11 35,21" fill="#0e5b56" />
        <ellipse cx="32" cy="37" rx="15" ry="16" fill="#0e5b56" />
        <circle cx="25" cy="33" r="6" fill="#fff" />
        <circle cx="39" cy="33" r="6" fill="#fff" />
        <circle cx="25" cy="33" r="2.4" fill={DARK} />
        <circle cx="39" cy="33" r="2.4" fill={DARK} />
        <polygon points="29,38 35,38 32,44" fill="#e0892f" />
      </g>
    ),
  },
  frog: {
    id: "frog",
    label: "Rana",
    bg: "#e7f3e2",
    art: (
      <g>
        <ellipse cx="32" cy="37" rx="16" ry="12" fill="#2aa06a" />
        <circle cx="22" cy="23" r="7" fill="#2aa06a" />
        <circle cx="42" cy="23" r="7" fill="#2aa06a" />
        <circle cx="22" cy="22" r="3" fill="#fff" />
        <circle cx="42" cy="22" r="3" fill="#fff" />
        <circle cx="22" cy="23" r="1.4" fill={DARK} />
        <circle cx="42" cy="23" r="1.4" fill={DARK} />
        <path d="M24 40 q8 6 16 0" stroke={DARK} strokeWidth="1.8" fill="none" strokeLinecap="round" />
      </g>
    ),
  },
  lion: {
    id: "lion",
    label: "León",
    bg: "#fbefd9",
    art: (
      <g>
        <g fill="#e0892f">
          <circle cx="32" cy="15" r="4" />
          <circle cx="20" cy="22" r="4" />
          <circle cx="44" cy="22" r="4" />
          <circle cx="16" cy="34" r="4" />
          <circle cx="48" cy="34" r="4" />
          <circle cx="20" cy="46" r="4" />
          <circle cx="44" cy="46" r="4" />
          <circle cx="32" cy="50" r="4" />
        </g>
        <circle cx="32" cy="34" r="15" fill="#e0892f" />
        <circle cx="32" cy="34" r="11" fill="#ffd28a" />
        <circle cx="27" cy="32" r="2" fill={DARK} />
        <circle cx="37" cy="32" r="2" fill={DARK} />
        <polygon points="30,37 34,37 32,40" fill="#a86326" />
        <path d="M32 40 v2.5" stroke="#a86326" strokeWidth="1.4" strokeLinecap="round" />
      </g>
    ),
  },
  rocket: {
    id: "rocket",
    label: "Cohete",
    bg: "#e9eef6",
    art: (
      <g>
        <path d="M23 40 l-7 8 8 -2 z" fill="#ff7a59" />
        <path d="M41 40 l7 8 -8 -2 z" fill="#ff7a59" />
        <path d="M32 9 c8 6 9 19 9 29 v3 H23 v-3 c0-10 1-23 9-29 z" fill="#fff" stroke="#0e837b" strokeWidth="2" />
        <circle cx="32" cy="25" r="5" fill="#0e837b" />
        <path d="M27 44 q5 9 10 0 z" fill="#e0892f" />
      </g>
    ),
  },
  ball: {
    id: "ball",
    label: "Balón",
    bg: "#eaf0ef",
    art: (
      <g>
        <circle cx="32" cy="33" r="16" fill="#fff" stroke={DARK} strokeWidth="1.5" />
        <polygon points="32,24 40,30 37,39 27,39 24,30" fill={DARK} />
        <g stroke={DARK} strokeWidth="1.5" strokeLinecap="round">
          <line x1="32" y1="24" x2="32" y2="18" />
          <line x1="40" y1="30" x2="46" y2="27" />
          <line x1="37" y1="39" x2="40" y2="46" />
          <line x1="27" y1="39" x2="24" y2="46" />
          <line x1="24" y1="30" x2="18" y2="27" />
        </g>
      </g>
    ),
  },
  dino: {
    id: "dino",
    label: "Dino",
    bg: "#e7f3e2",
    art: (
      <g>
        <g fill="#1f8a5a">
          <polygon points="18,30 22,21 26,30" />
          <polygon points="26,28 30,18 34,28" />
          <polygon points="34,28 38,20 42,29" />
        </g>
        <ellipse cx="33" cy="37" rx="15" ry="12" fill="#2aa06a" />
        <circle cx="40" cy="34" r="3.4" fill="#fff" />
        <circle cx="41" cy="34" r="1.6" fill={DARK} />
        <circle cx="46" cy="39" r="1" fill={DARK} />
        <path d="M40 43 q4 3 7 0" stroke={DARK} strokeWidth="1.4" fill="none" strokeLinecap="round" />
      </g>
    ),
  },
};

export const AVATAR_IDS: AvatarId[] = [
  "fox",
  "cat",
  "panda",
  "owl",
  "frog",
  "lion",
  "rocket",
  "ball",
  "dino",
];

export const DEFAULT_AVATAR: AvatarId = "fox";

export function isAvatarId(value: string): value is AvatarId {
  return Object.prototype.hasOwnProperty.call(DEFS, value);
}

export function avatarLabel(id: string): string {
  return isAvatarId(id) ? DEFS[id].label : DEFS[DEFAULT_AVATAR].label;
}

export function Avatar({
  id,
  size = 48,
  title,
  imageUrl,
}: {
  id?: string | null;
  size?: number;
  title?: string;
  imageUrl?: string | null;
}) {
  if (imageUrl) {
    return (
      <img
        src={assetUrl(imageUrl)}
        alt={title ?? "avatar"}
        width={size}
        height={size}
        style={{ display: "block", flexShrink: 0, borderRadius: 14, objectFit: "cover" }}
      />
    );
  }
  const def = id && isAvatarId(id) ? DEFS[id] : DEFS[DEFAULT_AVATAR];
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      role="img"
      aria-label={title ?? def.label}
      style={{ display: "block", flexShrink: 0 }}
    >
      <rect x="2" y="2" width="60" height="60" rx="18" fill={def.bg} />
      {def.art}
    </svg>
  );
}
