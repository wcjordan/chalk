import { parseTextWithUrls } from './urlParser';

describe('parseTextWithUrls', () => {
  it('should return empty array for empty string', () => {
    const result = parseTextWithUrls('');
    expect(result).toEqual([]);
  });

  it('should return text segment for plain text with no URLs', () => {
    const result = parseTextWithUrls('Just some plain text');
    expect(result).toEqual([{ type: 'text', content: 'Just some plain text' }]);
  });

  it('should handle text with only a URL', () => {
    const result = parseTextWithUrls('https://example.com');
    expect(result).toEqual([{ type: 'url', content: 'https://example.com' }]);
  });

  it('should not match incomplete URLs', () => {
    const result = parseTextWithUrls('Visit example.com or www.example.com');
    expect(result).toEqual([
      { type: 'text', content: 'Visit example.com or www.example.com' },
    ]);
  });

  test.each([
    ['should detect a single HTTP URL', 'Check http://example.com for info'],
    ['should detect a single HTTPS URL', 'Check https://example.com for info'],
    [
      'should detect URL at the start of text',
      'https://example.com is the link',
    ],
    ['should detect URL at the end of text', 'Click here: https://example.com'],
    [
      'should detect multiple URLs',
      'Visit https://example.com or http://test.com for more',
    ],
    ['should handle URLs with paths', 'See https://example.com/path/to/page'],
    [
      'should handle URLs with query strings',
      'Check https://example.com/search?q=test&page=1',
    ],
    [
      'should handle URLs with fragments',
      'Read https://example.com/docs#section-1',
    ],
    [
      'should handle URLs with ports',
      'Connect to https://example.com:8080/api',
    ],
    [
      'should handle consecutive URLs separated by spaces',
      'https://first.com https://second.com',
    ],
    [
      'should handle multiline text with URLs',
      'First line with https://example.com\nSecond line with http://test.com',
    ],
    [
      'should handle URLs followed by punctuation',
      'Check https://example.com. Also see https://test.com!',
    ],
  ])('%s', (_, input) => {
    expect(parseTextWithUrls(input)).toMatchSnapshot();
  });
});

export {};
