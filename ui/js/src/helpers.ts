import Constants from 'expo-constants';

export const getEnvFlags = () => {
  if (Constants.manifest) {
    return Constants.manifest.extra;
  }
  return Constants.manifest2.extra.expoClient.extra;
};
