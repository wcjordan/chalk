import type { StorybookConfig } from '@storybook/react-native-web-vite';

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(js|jsx|mjs|ts|tsx)'],

  addons: [
    '@storybook/addon-links',
    '@storybook/addon-docs'
  ],
  framework: {
    name: '@storybook/react-native-web-vite',
    options: {
      pluginReactOptions: {
        babel: {
          plugins: [
            "@babel/plugin-proposal-export-namespace-from",
            ["react-native-reanimated/plugin", { disableSourceMaps: true }],
          ],
        },
      },
    }
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
        ]
      },
    };
  },
};

export default config;
