# Estándares de frontend — Chispa ✨

> Cuelga de [estándares base](base.md). Stack real: **React 18 · TypeScript 5.5 `strict` · Vite 5 ·
> React Router 6 · Vitest · Testing Library**. Sin librería de estado global, sin framework de CSS.

---

## 1. Estructura

```
src/
├── api/          Cliente HTTP tipado. Una función por endpoint. Cero JSX.
├── auth/         SessionContext: quién está autenticado y de qué tipo.
├── components/   Piezas reutilizables sin conocimiento de dominio (Button, ScreenCard, Avatar…).
├── i18n/         Contexto de idioma y catálogo de traducciones.
├── routes/       ProtectedRoute y guardas de navegación.
├── screens/      Una pantalla = una ruta. Aquí vive la composición y el estado de pantalla.
└── styles/       theme.css: tokens de diseño en variables CSS.
```

Regla de reparto: si una pieza conoce el dominio de Chispa (islas, lecciones, exploradores), es una
**pantalla** o va bajo `screens/`. Si solo conoce props genéricas, es un **componente**.

## 2. Dos sesiones independientes

El mismo dispositivo (la tablet de casa) sostiene dos sesiones a la vez, y confundirlas es el error
más caro del frontend:

| Sesión | Clave en `localStorage` | Se pasa como |
|---|---|---|
| Familia (adulto) | `chispa_token` | `auth: true` |
| Niño | `chispa_child_token` | `auth: "child"` |

- Toda llamada declara explícitamente cuál usa: `apiFetch<T>(path, { auth: "child" })`.
- Un 401 **por token** limpia solo esa sesión y redirige a su punto de entrada. Un 401 por PIN o
  credenciales incorrectas **no** cierra sesión: si un niño falla el PIN tres veces, el padre no
  puede acabar deslogueado. Esta distinción está en `handleExpiredSession` y hay que respetarla.

## 3. Cliente de API

- Todo pasa por `apiFetch<T>`. Nunca un `fetch` suelto en una pantalla.
- Los errores llegan como `ApiError` con `status` y mensaje. Las pantallas deciden qué mostrar.
- Un módulo por área en `api/` (`auth.ts`, `children.ts`, `nucleo.ts`, `stories.ts`,
  `aiConfig.ts`), con tipos exportados junto a la función que los devuelve.
- La URL base sale de `VITE_API_URL`, con `http://localhost:8000` por defecto. Nunca una URL
  escrita a mano en una pantalla: rompería el acceso por LAN.

## 4. Textos e i18n

- **Ningún texto visible se escribe directamente en el JSX.** Siempre `t("clave")`.
- El catálogo vive en `i18n/translations.ts`, con español e inglés en paralelo. Una clave sin su par
  en el otro idioma es un fallo.
- Claves con prefijo de ámbito: `lesson.funFact`, `addExplorer.pinHint`, `validation.pinMismatch`.
- El idioma activo gobierna también la voz: lectura (`SpeakButton`) y dictado (`MicButton`).

## 5. Interfaz para niños

Quien usa estas pantallas tiene entre 3 y 12 años, y parte no sabe leer todavía.

- **Objetivos táctiles grandes.** Nada de controles de 24 px.
- **Una acción principal por pantalla**, visualmente dominante.
- Tokens de color y tipografía desde `styles/theme.css` (Fredoka para titulares, Mulish para texto).
  No colores literales en los componentes salvo matices puntuales sobre un token existente.
- **Contraste AA** como mínimo en toda pantalla del niño.
- Animaciones sujetas a `prefers-reduced-motion`.
- El niño **nunca ve un error técnico**. Ante un fallo, o mensaje amable
  ("Esta la vemos con un adulto 🛟") o silencio con degradación, como en `StoryLibrary.create`.

## 6. Tests

- Vitest + Testing Library. Un `.test.tsx` junto al fichero que prueba.
- **Probar comportamiento visible, no implementación.** Consultar por rol y texto accesible
  (`getByRole`, `getByLabelText`), no por clases CSS ni por estructura del DOM.
- `apiFetch` se mockea; los tests no tocan la red.
- Toda pantalla con formulario prueba al menos: el camino feliz, un error de validación en cliente y
  el tratamiento de un `ApiError` del servidor.
- `npm run lint` (`tsc --noEmit`) limpio antes de commitear. Sin `any`, sin `@ts-ignore`.

## 7. Estado

- `useState` y `useEffect` bastan para el estado de pantalla. No se introduce Redux, Zustand ni
  similar sin una ADR que lo justifique.
- El único estado verdaderamente compartido es la sesión (`SessionContext`) y el idioma
  (`I18nContext`). Si aparece un tercero, discutirlo antes de añadirlo.
- Limpiar siempre los efectos: `clearTimeout` en el `return` del `useEffect`. Hay precedente de bug
  por no hacerlo (`ChangePassword`).
