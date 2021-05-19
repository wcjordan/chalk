import color from 'color';
import Constants from 'expo-constants';
import React from 'react';
import { DefaultTheme, Provider as PaperProvider } from 'react-native-paper';
import { Provider as ReduxProvider } from 'react-redux';
import * as Sentry from 'sentry-expo';
import App from './src/App';
import store from './src/redux/store';

Sentry.init({
  dsn: Constants.manifest.extra.SENTRY_DSN,
  enableInExpoDevelopment: true,
  environment: Constants.manifest.extra.ENVIRONMENT,
  debug: Constants.manifest.extra.DEBUG == 'true',
});

// https://callstack.github.io/react-native-paper/theming.html
const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#99b6ff',
    accent: '#4caf50',
    surface: '#ffffff',
    background: '#edf0f7',
    text: '#2d3752',
    disabled: color('#2d3752').alpha(0.26).rgb().string(),
    placeholder: color('#2d3752').alpha(0.54).rgb().string(),
    backdrop: color('#2d3752').alpha(0.5).rgb().string(),
    // error: '#CF6679',
    // onSurface: '#000000',
    // notification: pinkA100,
  },
};

const TopApp: React.FC = function () {
  return (
    <ReduxProvider store={store}>
      <PaperProvider theme={theme}>
        <App />
      </PaperProvider>
    </ReduxProvider>
  );
};
export default TopApp;
