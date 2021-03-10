const { defaults: tsjPreset } = require('ts-jest/presets');

module.exports = {
  ...tsjPreset,
  preset: 'react-native-web',
  transform: {
    ...tsjPreset.transform,
    '\\.js$': '<rootDir>/node_modules/react-native/jest/preprocessor.js',
  },
  transformIgnorePatterns: [
    'node_modules/(?!(@fortawesome|react-native-svg-web)/)',
    '\\.pnp\\.[^\\/]+$',
  ],
  globals: {
    'ts-jest': {
      babelConfig: true,
      diagnostics: {
        exclude: ['node_modules', '**/*.stories.tsx', '**/*.test.ts'],
      },
      isolatedModules: true,
    },
  },
  moduleNameMapper: {
    'react-native-svg(.*)$': '<rootDir>/node_modules/react-native-svg-web$1',
  },
};
