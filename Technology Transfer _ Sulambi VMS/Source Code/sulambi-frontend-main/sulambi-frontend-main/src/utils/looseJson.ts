/**
 * Parse JSON that might be stored in "almost JSON" formats.
 *
 * In this project, some DB fields were historically saved as Python-style repr
 * (single quotes, True/False/None). Production data may still contain those.
 * This helper tries JSON.parse first, then normalizes common Python literals.
 */
export function looseJsonParse<T>(input: unknown, fallback: T): T {
  if (input === null || input === undefined) return fallback;
  if (typeof input !== "string") return input as T;

  const s = input.trim();
  if (!s) return fallback;

  // 1) Strict JSON
  try {
    return JSON.parse(s) as T;
  } catch {
    // fallthrough
  }

  // 2) Normalize common Python literals and single-quoted strings
  // - True/False/None -> true/false/null
  // - '...' -> "..."
  let normalized = s
    .replace(/\bTrue\b/g, "true")
    .replace(/\bFalse\b/g, "false")
    .replace(/\bNone\b/g, "null");

  // Replace single-quoted strings with double-quoted strings.
  // This is a best-effort conversion for our stored checkbox objects/arrays.
  normalized = normalized.replace(
    /'([^'\\]*(?:\\.[^'\\]*)*)'/g,
    (_m, inner: string) => `"${String(inner).replace(/"/g, '\\"')}"`
  );

  try {
    return JSON.parse(normalized) as T;
  } catch {
    return fallback;
  }
}

export function toJsonString(input: unknown, fallback: string = ""): string {
  if (input === null || input === undefined) return fallback;
  if (typeof input === "string") return input;
  try {
    return JSON.stringify(input);
  } catch {
    return fallback;
  }
}

