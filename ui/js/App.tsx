import Constants from 'expo-constants';
import { Provider as ReduxProvider } from 'react-redux';
import React from 'react';
import { DefaultTheme, Provider as PaperProvider } from 'react-native-paper';
import { FontAwesome5 } from '@expo/vector-icons';
import * as Sentry from 'sentry-expo';
import App from './src/App';
import store from './src/redux/store';

Sentry.init({
  dsn: Constants.manifest.extra.SENTRY_DSN,
  enableInExpoDevelopment: true,
  environment: Constants.manifest.extra.ENVIRONMENT,
  debug: Constants.manifest.extra.DEBUG == 'true',
});

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    // primary: 'green',
    // accent: 'yellow',
  },
};

const Icon = (props) => <FontAwesome5 {...props} />;

const TopApp: React.FC = function () {
  return (
    <ReduxProvider store={store}>
      <PaperProvider
        theme={theme}
        settings={{
          icon: Icon,
        }}
      >
        <App />
      </PaperProvider>
    </ReduxProvider>
  );
};
export default TopApp;
