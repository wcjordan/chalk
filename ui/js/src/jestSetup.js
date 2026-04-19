const { TextEncoder, TextDecoder } = require('util');
const { URLSearchParams, URL } = require('url');

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
global.URLSearchParams = URLSearchParams;
global.URL = URL;
