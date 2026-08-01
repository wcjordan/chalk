import { Platform } from 'react-native';
import type { Storage } from 'redux-persist/es/types';

// Only require the storage backend for the current platform: `redux-persist`'s
// web storage module runs a synchronous `window.localStorage` feature check at
// import time, which logs "redux-persist failed to create sync storage" if
// merely imported on native (no `localStorage` global), even when unused.
const storage: Storage =
  Platform.OS === 'web'
    ? // eslint-disable-next-line @typescript-eslint/no-require-imports
      require('redux-persist/lib/storage').default
    : // eslint-disable-next-line @typescript-eslint/no-require-imports
      require('@react-native-async-storage/async-storage').default;

export default storage;
