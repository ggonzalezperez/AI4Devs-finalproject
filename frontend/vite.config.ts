import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

// Raíz del repositorio (la carpeta que contiene backend/ y frontend/).
// TDD Guard guarda ahí los resultados de los tests, en .claude/tdd-guard/data/,
// y el frontend vive en un subdirectorio, así que hay que indicárselo.
// Se calcula en tiempo de ejecución para no commitear rutas de una máquina concreta.
const projectRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  plugins: [react()],
  // En producción es nginx quien enruta /api al backend. En `npm run dev` no hay
  // nginx, así que el servidor de Vite hace el mismo papel: sin esto, el cliente
  // pediría /api/... al propio Vite y recibiría el index.html del SPA.
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (ruta) => ruta.replace(/^\/api/, ""),
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/vitest.setup.ts",
    reporters: ["default", ["tdd-guard-vitest", { projectRoot }]],
  },
});
