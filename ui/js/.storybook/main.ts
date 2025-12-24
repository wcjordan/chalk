import type { StorybookConfig } from '@storybook/react-native-web-vite';

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(js|jsx|mjs|ts|tsx)'],

  addons: ['@storybook/addon-links', '@storybook/addon-docs'],
  framework: {
    name: '@storybook/react-native-web-vite',
    options: {
      pluginReactOptions: {
        babel: {
          plugins: [
            '@babel/plugin-proposal-export-namespace-from',
            [
              'react-native-worklets/plugin',
              {
                disableSourceMaps: true,
              },
            ],
          ],
        },
      },
    },
  },
  async viteFinal(config) {
    return {
      ...config,
      optimizeDeps: {
        force: true,
        exclude: [
          ...(config.optimizeDeps?.exclude ?? []),
          'react-native-draggable-flatlist',
        ],
        include: [
          ...(config.optimizeDeps?.include ?? []),
          'react-native-draggable-flatlist > react-native-reanimated',
          'hoist-non-react-statics',
          'invariant',
        ],
      },
      resolve: {
        ...(config.resolve ?? {}),
        alias: {
          ...(config.resolve?.alias ?? {}),
          // react-native-paper requires all 3 of these in a try catch.
          // Aliasing them all to the one used suppressed some warnings in Storybook
          '@react-native-vector-icons/material-design-icons':
            '@expo/vector-icons/MaterialCommunityIcons',
          'react-native-vector-icons/MaterialCommunityIcons':
            '@expo/vector-icons/MaterialCommunityIcons',

          'expo-constants': '../__mocks__/expo-constants.js',
        },
      },
    };
  },
};

export default config;
