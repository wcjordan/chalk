module.exports = {
  presets: ['module:babel-preset-expo'],
  env: {
    production: {
      plugins: [
        'react-native-paper/babel',
      ],
    },
  },
};