import Constants from 'expo-constants';
import { Platform } from 'react-native';

declare const window: any; // eslint-disable-line @typescript-eslint/no-explicit-any

export const getEnvFlags = () => {
  const flags = Constants.expoConfig?.extra || {};

  // If running in a browser, set the environment based on the hostname
  // This is because we wan't to build a single container w/ prod artifacts
  // and use it for the dev & ci use cases that don't use the Expo web server
  if (Platform.OS === 'web' && flags.ENVIRONMENT !== 'test') {
    if (window.IS_STORYBOOK === true) {
      flags.ENVIRONMENT = 'test';
    }
    const hostname = document.location.hostname;
    if (hostname.startsWith('localhost') || hostname.startsWith('chalk-dev')) {
      flags.ENVIRONMENT = 'DEV';
    } else if (hostname.startsWith('chalk-ci')) {
      flags.ENVIRONMENT = 'CI';
    }
  }
  return flags;
};
