import { Provider } from 'react-redux';
import React from 'react';
import App from './src/App';
import store from './src/redux/store';

const TopApp: React.FC = function () {
  return (
    <Provider store={store}>
      <App />
    </Provider>
  );
};
export default TopApp;
