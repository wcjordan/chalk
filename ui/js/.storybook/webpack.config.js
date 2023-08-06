import path from 'path';
import webpack from 'webpack';

module.exports = ({ config }) => {
  config.module.rules.push({
    test: /LICENSE$/,
    include: /node_modules/,
    loader: 'file-loader',
  });
  config.module.rules.push({
    test: /.map$/,
    include: /node_modules/,
    loader: 'file-loader',
  });

  // Disable useDataLoader hook so Storybook doesn't try to hit the backend
  config.resolve.alias['expo-constants'] = require.resolve(
    '../__mocks__/expo-constants.js',
  );

  // Mock out useAuthRequest for login button
  config.resolve.alias['expo-auth-session/providers/google'] = require.resolve(
    '../__mocks__/expo-auth-session/providers/google.js',
  );

  // Swap Expo icons for react-native-vector-icons
  config.resolve.alias['react-native-vector-icons/MaterialCommunityIcons'] =
    require.resolve('@expo/vector-icons/MaterialCommunityIcons');

  config.resolve.fallback = {
    fs: false,
    constants: false,
    child_process: false,
    crypto: false,
    module: false,
    net: false,
    os: false,
    path: false,
    stream: false,
    v8: false,
    worker_threads: false,
  };

  config.plugins.push(
    new webpack.NormalModuleReplacementPlugin(/node:/, (resource) => {
      resource.request = resource.request.replace(/^node:/, '');
    }),
  );

  return config;
};
