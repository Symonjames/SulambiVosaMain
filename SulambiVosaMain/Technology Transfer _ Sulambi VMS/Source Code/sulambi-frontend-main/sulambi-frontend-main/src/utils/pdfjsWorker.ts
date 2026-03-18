/**
 * PDF.js Worker Configuration
 * This file must be imported BEFORE any react-pdf components are used.
 * Worker is copied to public/ at build time (see scripts/copy-pdf-worker.cjs)
 * so it is served from same origin and avoids CORS/CSP failures in production.
 */

import { pdfjs } from "react-pdf";

// Same-origin worker (copied from node_modules/pdfjs-dist/build to public/ by prebuild)
// Using same origin avoids "Failed to fetch dynamically imported module" on Render/production
const workerUrl = "/pdf.worker.min.mjs";

pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;

// This file is imported for side effects only (worker configuration)
// No exports needed

