import { configureStore } from '@reduxjs/toolkit';
import * as Sentry from 'sentry-expo';
import rootReducer, { listTodos } from './reducers';

const sentryReduxEnhancer = Sentry.createReduxEnhancer({
  // Optionally pass options
});

const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(sentryReduxEnhancer),
});

// TODO dispose
window.setInterval(() => store.dispatch(listTodos()), 3000);

export default store;
