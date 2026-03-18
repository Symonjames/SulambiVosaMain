/**
 * Public origin used when generating shareable links (QR codes, copy links, etc.).
 *
 * If you generate QR codes locally but want them to point to your deployed site,
 * set `VITE_PUBLIC_APP_URL` (e.g. "https://www.sulambi-vosa.com").
 */
export function getPublicOrigin(): string {
  const raw = (import.meta as any)?.env?.VITE_PUBLIC_APP_URL as string | undefined;
  const fromEnv = (raw || "").trim().replace(/\/+$/, "");
  if (fromEnv) return fromEnv;

  if (typeof window !== "undefined" && window.location?.origin) {
    return window.location.origin;
  }
  return "";
}

