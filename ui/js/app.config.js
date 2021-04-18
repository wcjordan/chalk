export default {
  name: 'chalk',
  slug: 'chalk',
  version: '0.1.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  splash: {
    image: './assets/splash.png',
    resizeMode: 'contain',
    backgroundColor: '#ffffff',
  },
  updates: {
    fallbackToCacheTimeout: 0,
  },
  assetBundlePatterns: ['**/*'],
  ios: {
    supportsTablet: true,
  },
  web: {
    favicon: './assets/favicon.png',
  },
  hooks: {
    postPublish: [
      {
        file: 'sentry-expo/upload-sourcemaps',
        config: {
          organization: 'flipperkid',
          project: 'chalk-react-native',
          authToken: process.env.SENTRY_TOKEN,
        },
      },
    ],
  },
  extra: {
    SENTRY_DSN: process.env.SENTRY_DSN,
    DEBUG: process.env.DEBUG,
    ENVIRONMENT: process.env.ENVIRONMENT,
  },
};
