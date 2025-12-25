export const stripLeadingRoman = (input?: string | null): string => {
  if (!input) {
    return "";
  }

  return input.replace(/^\s*(?:[IVXLCDM]+\.?\s*)+/i, "").trimStart();
};
