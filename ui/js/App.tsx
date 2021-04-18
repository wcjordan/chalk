import Constants from 'expo-constants';
import { Provider } from 'react-redux';
import React from 'react';
import * as Sentry from 'sentry-expo';
import App from './src/App';
import store from './src/redux/store';

Sentry.init({
  dsn: Constants.manifest.extra.SENTRY_DSN,
  enableInExpoDevelopment: true,
  environment: Constants.manifest.extra.ENVIRONMENT,
  debug: Constants.manifest.extra.DEBUG == 'true',
});

const TopApp: React.FC = function () {
  return (
    <Provider store={store}>
      <App />
    </Provider>
  );
};
export default TopApp;
