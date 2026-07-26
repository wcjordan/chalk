import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { OfflineOperation } from './types';

interface OfflineQueueState {
  pendingOps: OfflineOperation[];
}

const initialState: OfflineQueueState = {
  pendingOps: [],
};

const offlineQueueSlice = createSlice({
  name: 'offlineQueue',
  initialState,
  reducers: {
    enqueueOp: (state, action: PayloadAction<OfflineOperation>) => {
      state.pendingOps.push(action.payload);
    },
    dequeueOpByIndex: (state, action: PayloadAction<number>) => {
      state.pendingOps.splice(action.payload, 1);
    },
    clearQueue: (state) => {
      state.pendingOps = [];
    },
  },
});

export default offlineQueueSlice;
