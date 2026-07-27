import { Platform } from 'react-native';
import type { Storage } from 'redux-persist/es/types';

// eslint-disable-next-line @typescript-eslint/no-require-imports
const webStorage: Storage = require('redux-persist/lib/storage').default;
// eslint-disable-next-line @typescript-eslint/no-require-imports
const nativeStorage: Storage = require('@react-native-async-storage/async-storage').default;

const storage: Storage = Platform.OS === 'web' ? webStorage : nativeStorage;

export default storage;
