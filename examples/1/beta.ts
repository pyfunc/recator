// Example 1: duplicate block (escapeHtml)
export const sanitize = (s: string): string => {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

export function demoBeta(input: string) {
  return sanitize(input);
}
