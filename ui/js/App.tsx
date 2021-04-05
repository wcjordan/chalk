import Constants from 'expo-constants';
import { Provider } from 'react-redux';
import React from 'react';
import * as Sentry from 'sentry-expo';
import { Integrations } from "@sentry/tracing";
import App from './src/App';
import store from './src/redux/store';

Sentry.init({
  dsn: Constants.manifest.extra.SENTRY_DSN,
  enableInExpoDevelopment: true,
  environment: document.location.hostname.split('.')[0],
  debug: Constants.manifest.extra.DEBUG == 'true',
  integrations: [new Integrations.BrowserTracing()],
  tracesSampleRate: 1.0,
});

const TopApp: React.FC = function () {
  return (
    <Provider store={store}>
      <App />
    </Provider>
  );
};
export default Sentry.withProfiler(TopApp);
