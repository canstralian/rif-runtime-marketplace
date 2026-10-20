import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages project sites are hosted below /<repository-name>/.
export default defineConfig({
  plugins: [react()],
  base: "/rif-runtime-marketplace/",
  build: { outDir: "dist" },
});
