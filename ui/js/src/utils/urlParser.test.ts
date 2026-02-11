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

  it('should detect a single HTTP URL', () => {
    const result = parseTextWithUrls('Check http://example.com for info');
    expect(result).toMatchSnapshot();
  });

  it('should detect a single HTTPS URL', () => {
    const result = parseTextWithUrls('Check https://example.com for info');
    expect(result).toMatchSnapshot();
  });

  it('should detect URL at the start of text', () => {
    const result = parseTextWithUrls('https://example.com is the link');
    expect(result).toMatchSnapshot();
  });

  it('should detect URL at the end of text', () => {
    const result = parseTextWithUrls('Click here: https://example.com');
    expect(result).toMatchSnapshot();
  });

  it('should detect multiple URLs', () => {
    const result = parseTextWithUrls(
      'Visit https://example.com or http://test.com for more',
    );
    expect(result).toMatchSnapshot();
  });

  it('should handle URLs with paths', () => {
    const result = parseTextWithUrls('See https://example.com/path/to/page');
    expect(result).toMatchSnapshot();
  });

  it('should handle URLs with query strings', () => {
    const result = parseTextWithUrls(
      'Check https://example.com/search?q=test&page=1',
    );
    expect(result).toMatchSnapshot();
  });

  it('should handle URLs with fragments', () => {
    const result = parseTextWithUrls('Read https://example.com/docs#section-1');
    expect(result).toMatchSnapshot();
  });

  it('should handle URLs with ports', () => {
    const result = parseTextWithUrls('Connect to https://example.com:8080/api');
    expect(result).toMatchSnapshot();
  });

  it('should handle text with only a URL', () => {
    const result = parseTextWithUrls('https://example.com');
    expect(result).toEqual([{ type: 'url', content: 'https://example.com' }]);
  });

  it('should handle consecutive URLs separated by spaces', () => {
    const result = parseTextWithUrls('https://first.com https://second.com');
    expect(result).toMatchSnapshot();
  });

  it('should not match incomplete URLs', () => {
    const result = parseTextWithUrls('Visit example.com or www.example.com');
    expect(result).toEqual([
      { type: 'text', content: 'Visit example.com or www.example.com' },
    ]);
  });

  it('should handle multiline text with URLs', () => {
    const result = parseTextWithUrls(
      'First line with https://example.com\nSecond line with http://test.com',
    );
    expect(result).toMatchSnapshot();
  });

  it('should handle URLs followed by punctuation', () => {
    const result = parseTextWithUrls(
      'Check https://example.com. Also see https://test.com!',
    );
    expect(result).toMatchSnapshot();
  });
});

export {};
