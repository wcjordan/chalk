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
      plugins: [
        ...(config.plugins ?? []),
        {
          // expo-modules-core ships raw TypeScript source as its entry point.
          // ts-declarations/global.ts uses plain `import { X }` (not `import type`)
          // from files that only contain `declare class` — no runtime exports.
          // Rolldown and the browser both reject this. Rewrite those four imports
          // to `import type` so they're erased before bundling/serving.
          // enforce: 'pre' ensures this runs before the Babel/esbuild TypeScript
          // transform, which would otherwise process the file first.
          name: 'fix-expo-modules-core-ts-declarations',
          enforce: 'pre' as const,
          transform(code: string, id: string) {
            if (!id.includes('expo-modules-core/src/ts-declarations/global')) {
              return;
            }
            return {
              code: code
                .replace(
                  "import { EventEmitter } from './EventEmitter'",
                  "import type { EventEmitter } from './EventEmitter'",
                )
                .replace(
                  "import { NativeModule } from './NativeModule'",
                  "import type { NativeModule } from './NativeModule'",
                )
                .replace(
                  "import { SharedObject } from './SharedObject'",
                  "import type { SharedObject } from './SharedObject'",
                )
                .replace(
                  "import { SharedRef } from './SharedRef'",
                  "import type { SharedRef } from './SharedRef'",
                ),
              map: null,
            };
          },
        },
      ],
      optimizeDeps: {
        force: true,
        exclude: [
          ...(config.optimizeDeps?.exclude ?? []),
          'react-native-draggable-flatlist',
          'expo-modules-core',
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
