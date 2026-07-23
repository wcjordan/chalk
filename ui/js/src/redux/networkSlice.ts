import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import {
  listTodos as listTodosApi,
} from './todosApiSlice';

interface NetworkState {
  isOnline: boolean;
  consecutiveNetworkFailures: number;
}

const initialState: NetworkState = {
  isOnline: true,
  consecutiveNetworkFailures: 0,
};

const networkSlice = createSlice({
  name: 'network',
  initialState,
  reducers: {
    setOnlineStatus: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
      if (action.payload === true) {
        state.consecutiveNetworkFailures = 0;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(listTodosApi.fulfilled, (state) => {
        state.consecutiveNetworkFailures = 0;
        state.isOnline = true;
      })
      .addCase(listTodosApi.rejected, (state, action) => {
        if (action.error.name === 'TypeError') {
          state.consecutiveNetworkFailures += 1;
          if (state.consecutiveNetworkFailures >= 2) {
            state.isOnline = false;
          }
        }
      });
  },
});

export const { setOnlineStatus } = networkSlice.actions;
export default networkSlice;
