import { API_BASE_URL } from "../api/init";

/**
 * Backend static files live at {origin}/uploads/...
 * Must match logic used in NewsThumbnailCarousel / HomeNewsSection so report photos
 * resolve correctly in dev (Vite proxy), production (separate frontend + API domains),
 * and for full URLs (e.g. Cloudinary).
 */
export function getUploadsBase(): string {
  if (import.meta.env.DEV && API_BASE_URL === "/api") {
    return "http://localhost:8000";
  }
  const stripped = API_BASE_URL.replace(/\/api\/?$/, "");
  if (stripped) return stripped;
  if (typeof window !== "undefined") return window.location.origin;
  return "";
}

/** Strip to relative path under uploads/ (no leading uploads/). */
function normalizeUploadRelativePath(filename: string): string {
  let clean = filename.trim();
  try {
    clean = decodeURIComponent(clean);
  } catch {
    /* ignore */
  }
  clean = clean.trim().replace(/\\/g, "/");
  clean = clean.replace(/^uploads[\\/]/i, "");
  return clean;
}

/**
 * Legacy backend saved files as `str(uuid4()) + originalFilename` (no separator).
 * New backend uses `uuid_filename`. Try both so old DB rows still resolve if the file exists.
 */
function uploadRelativePathVariants(relative: string): string[] {
  const variants = new Set<string>();
  if (!relative) return [];
  variants.add(relative);
  const m = relative.match(
    /^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(.+)$/i
  );
  if (m?.[2] && !m[2].startsWith("_")) {
    variants.add(`${m[1]}_${m[2]}`);
  }
  return [...variants];
}

/**
 * Resolve a stored report photo path or absolute URL to a browser-loadable src.
 */
export function resolveReportImageUrl(filename: string): string {
  const all = resolveReportImageUrlVariants(filename);
  return all[0] ?? "";
}

/**
 * All URLs to try for this photo (primary + legacy underscore variant).
 */
export function resolveReportImageUrlVariants(filename: string): string[] {
  if (!filename || typeof filename !== "string") return [];
  let clean = filename.trim();
  try {
    clean = decodeURIComponent(clean);
  } catch {
    /* ignore */
  }
  clean = clean.trim();
  if (!clean) return [];

  if (/^https?:\/\//i.test(clean)) return [clean];
  if (clean.startsWith("//")) return [`https:${clean}`];

  const relative = normalizeUploadRelativePath(clean);
  const paths = uploadRelativePathVariants(relative);
  const base = getUploadsBase();
  const baseNorm = base.replace(/\/$/, "");
  return paths.map((p) =>
    baseNorm ? `${baseNorm}/uploads/${p}` : `/uploads/${p}`
  );
}

/** Normalize API photos field: string (comma-separated) or string[]. */
export function normalizePhotoList(photos: unknown): string[] {
  if (photos == null) return [];
  if (Array.isArray(photos)) {
    return photos
      .map((p) => (typeof p === "string" ? p.trim() : String(p)))
      .filter(Boolean);
  }
  if (typeof photos === "string") {
    return photos
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  }
  return [];
}

/** Normalize captions to align with photo indices. */
export function normalizeCaptionList(captions: unknown): string[] {
  if (captions == null) return [];
  if (Array.isArray(captions)) {
    return captions.map((c) => (c == null ? "" : String(c)));
  }
  if (typeof captions === "string") {
    return captions.split(",").map((s) => s.trim());
  }
  return [];
}
