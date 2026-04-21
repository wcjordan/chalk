module.exports = {
  preset: 'jest-expo/android',
  testEnvironment: 'jsdom',
  reporters: ['default', 'jest-junit'],
  setupFiles: [
    './src/jestSetup.js',
    './node_modules/@react-native-google-signin/google-signin/jest/build/jest/setup.js',
  ],
  testPathIgnorePatterns: [
    '<rootDir>/src/__snapshots__/',
    '<rootDir>/src/components/__snapshots__/',
  ],
};
