import type { StorybookConfig } from '@storybook/react-native-web-vite';

const config: StorybookConfig = {
  stories: ['../src/**/*.mdx', '../src/**/*.stories.@(js|jsx|mjs|ts|tsx)'],

  addons: [
    '@storybook/addon-links',
    '@storybook/addon-docs'
  ],
  core: {
    builder: '@storybook/builder-vite'
  },
  framework: {
    name: '@storybook/react-native-web-vite',
    options: {
      modulesToTranspile: ['react-native-reanimated', 'react-native-draggable-flatlist'],
      pluginReactOptions: {
        babel: {
          presets: ['module:babel-preset-expo'],
        },
      },
    }
  }
};

export default config;
