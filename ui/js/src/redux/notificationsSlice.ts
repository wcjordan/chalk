import { createSlice } from '@reduxjs/toolkit';

import { NotificationsState } from './types';

const initialState: NotificationsState = {
  notificationQueue: [],
};
export default createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    addNotification: (state, action) => {
      state.notificationQueue.push(action.payload);
    },
    dismissNotification: (state) => {
      state.notificationQueue.shift();
    },
  },
});
