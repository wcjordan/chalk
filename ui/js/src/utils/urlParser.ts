/**
 * Represents a segment of text - either plain text or a URL
 */
export interface TextSegment {
  type: 'text' | 'url';
  content: string;
}

/**
 * Regular expression to match HTTP and HTTPS URLs
 * Matches:
 * - http:// or https://
 * - Domain name with optional port
 * - Optional path, query string, and fragment
 */
const URL_REGEX = /(https?:\/\/[^\s]+)/g;

/**
 * Parses text and identifies URLs within it
 * Returns an array of text segments, each marked as either 'text' or 'url'
 *
 * @param text - The text to parse
 * @returns Array of text segments
 *
 * @example
 * parseTextWithUrls('Check https://example.com for info')
 * // Returns:
 * // [
 * //   { type: 'text', content: 'Check ' },
 * //   { type: 'url', content: 'https://example.com' },
 * //   { type: 'text', content: ' for info' }
 * // ]
 */
export function parseTextWithUrls(text: string): TextSegment[] {
  if (!text) {
    return [];
  }

  const segments: TextSegment[] = [];
  let lastIndex = 0;

  // Find all URL matches
  const matches = text.matchAll(URL_REGEX);

  for (const match of matches) {
    let url = match[0];
    if (').!,?;'.includes(url[url.length - 1])) {
      // If the URL ends with punctuation, we should exclude it from the URL
      url = url.slice(0, -1);
    }
    const startIndex = match.index!;

    // Add text before the URL (if any)
    if (startIndex > lastIndex) {
      segments.push({
        type: 'text',
        content: text.substring(lastIndex, startIndex),
      });
    }

    // Add the URL
    segments.push({
      type: 'url',
      content: url,
    });

    lastIndex = startIndex + url.length;
  }

  // Add remaining text after the last URL (if any)
  if (lastIndex < text.length) {
    segments.push({
      type: 'text',
      content: text.substring(lastIndex),
    });
  }

  return segments;
}
