module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: ['@storybook/addon-links', '@storybook/addon-essentials'],

  webpackFinal: async (config) => {
    config.resolve.alias['expo-auth-session/providers/google'] =
      require.resolve('../__mocks__/expo-auth-session/providers/google.js');
    return config;
  },
};
