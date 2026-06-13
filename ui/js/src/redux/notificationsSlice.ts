import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { Notification, NotificationsState } from './types';

const initialState: NotificationsState = {
  notificationQueue: [],
};
export default createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    addNotification: (state, action: PayloadAction<Notification>) => {
      state.notificationQueue.push(action.payload);
    },
    dismissNotification: (state) => {
      state.notificationQueue.shift();
    },
  },
});
