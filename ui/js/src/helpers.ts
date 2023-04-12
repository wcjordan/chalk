import Constants from 'expo-constants';

export const getEnvFlags = () => {
  return Constants.expoConfig?.extra || {};
};
