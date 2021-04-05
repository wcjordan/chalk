import { configureStore } from '@reduxjs/toolkit';
import { createReduxEnhancer } from 'sentry-expo';
import rootReducer from './reducers';

const sentryReduxEnhancer = createReduxEnhancer({
  // Optionally pass options
});

const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(sentryReduxEnhancer),
});
const getStore = () => store;
export default getStore;
