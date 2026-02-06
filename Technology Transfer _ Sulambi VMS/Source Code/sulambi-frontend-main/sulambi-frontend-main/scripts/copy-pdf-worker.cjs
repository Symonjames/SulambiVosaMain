/**
 * Copy PDF.js worker from node_modules to public so it is served from same origin.
 * Fixes "Failed to fetch dynamically imported module" when loading worker from unpkg in production (CORS/CSP).
 */
const fs = require("fs");
const path = require("path");

const src = path.join(__dirname, "..", "node_modules", "pdfjs-dist", "build", "pdf.worker.min.mjs");
const destDir = path.join(__dirname, "..", "public");
const dest = path.join(destDir, "pdf.worker.min.mjs");

if (!fs.existsSync(src)) {
  console.warn("[copy-pdf-worker] Worker not found at", src, "- run npm install");
  process.exit(0);
}

if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
}

fs.copyFileSync(src, dest);
console.log("[copy-pdf-worker] Copied pdf.worker.min.mjs to public/");
