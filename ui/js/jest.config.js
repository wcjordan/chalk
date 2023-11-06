module.exports = {
  preset: 'jest-expo/android',
  testEnvironment: 'jsdom',

  reporters: ['default', 'jest-junit'],
  setupFiles: [
    './node_modules/@react-native-google-signin/google-signin/jest/build/setup.js',
  ],
};
