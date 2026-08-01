import { combineReducers, configureStore } from '@reduxjs/toolkit';
import { rootReducerConfig } from './reducers';

const rootReducer = combineReducers(rootReducerConfig);

function buildMiddlewareOptions() {
  if (process.env.NODE_ENV === 'test') {
    return {};
  }
  const { FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } =
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    require('redux-persist');
  return {
    serializableCheck: {
      ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
    },
  };
}

export function setupStore(preloadedState?: Partial<RootState>) {
  return configureStore({
    reducer: rootReducer,
    preloadedState,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware(buildMiddlewareOptions()),
  });
}

export function createPersistor(store: AppStore) {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { persistStore } = require('redux-persist');
  return persistStore(store);
}

export type RootState = ReturnType<typeof rootReducer>;
export type AppStore = ReturnType<typeof setupStore>;
export type AppDispatch = AppStore['dispatch'];
