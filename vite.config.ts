import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";

export default defineConfig({
  // Relative asset paths so the static build also works from GitHub Pages under /OPTIONS/.
  base: "./",
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    // The pricing API (FastAPI on :8000, reusing the legacy engines) — same-origin for the browser.
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
