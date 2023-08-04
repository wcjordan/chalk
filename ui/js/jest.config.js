module.exports = {
  preset: 'jest-expo/android',
  testEnvironment: 'jsdom',

  setupFiles: [
    './node_modules/@react-native-google-signin/google-signin/jest/build/setup.js',
  ],
};
