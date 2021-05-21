const { withUnimodules } = require('@expo/webpack-config/addons');

module.exports = ({ config }) => {
  return withUnimodules(config);
};
