const IS_DEV = process.env.ENVIRONMENT === 'dev';

export default {
  name: IS_DEV ? 'chalk (dev)' : 'chalk',
  slug: 'chalk',
  version: '0.1.3',
  orientation: 'portrait',
  icon: './assets/icon.png',
  scheme: 'chalk',
  android: {
    package: IS_DEV ? 'com.flipperkid.chalk.dev' : 'com.flipperkid.chalk',
    versionCode: 1,
  },
  runtimeVersion: {
    policy: 'sdkVersion',
  },
  splash: {
    image: './assets/splash.png',
    resizeMode: 'contain',
    backgroundColor: '#ffffff',
  },
  updates: {
    fallbackToCacheTimeout: 0,
    url: 'https://u.expo.dev/b52e213a-3078-4069-84b0-331d55010927',
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
    DEBUG: process.env.DEBUG,
    ENVIRONMENT: process.env.ENVIRONMENT,
    OAUTH_CLIENT_ID: process.env.OAUTH_CLIENT_ID,
    SENTRY_DSN: process.env.SENTRY_DSN,
    eas: {
      projectId: 'b52e213a-3078-4069-84b0-331d55010927',
    },
  },
  plugins: ['@react-native-google-signin/google-signin', 'sentry-expo'],
};
