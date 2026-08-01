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
    // Resyncs this tab's queue with another tab's persisted write, e.g. after
    // that tab flushed the queue while this tab held a stale in-memory copy.
    replaceQueue: (state, action: PayloadAction<OfflineOperation[]>) => {
      state.pendingOps = action.payload;
    },
  },
});

export default offlineQueueSlice;
