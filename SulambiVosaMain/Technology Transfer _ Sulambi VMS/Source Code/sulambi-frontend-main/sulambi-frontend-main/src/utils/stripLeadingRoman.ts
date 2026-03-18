/**
 * Remove leading roman numerals (e.g. "I. ", "IV ", "XII.") from a label.
 *
 * Must be defensive: some API fields can be non-strings (number/null/etc).
 */
export const stripLeadingRoman = (input?: unknown): string => {
  if (input === null || input === undefined) return "";

  let s: string;
  try {
    s = typeof input === "string" ? input : String(input);
  } catch {
    return "";
  }

  if (!s) return "";
  return s.replace(/^\s*(?:[IVXLCDM]+\.?\s*)+/i, "").trimStart();
};
