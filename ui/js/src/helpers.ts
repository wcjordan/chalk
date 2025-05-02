import Constants from 'expo-constants';
import { Platform } from 'react-native';

export const getEnvFlags = () => {
  const flags = Constants.expoConfig?.extra || {};

  if (Platform.OS === 'web' && flags.ENVIRONMENT !== 'test') {
    const hostname = document.location.hostname;
    if (hostname.startsWith('localhost') || hostname.startsWith('chalk-dev')) {
      flags.ENVIRONMENT = 'dev';
    } else if (hostname.startsWith('chalk-ci')) {
      flags.ENVIRONMENT = 'ci';
    }
  }
  return flags;
};
