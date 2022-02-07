import { Platform } from 'react-native';
import { createSlice } from '@reduxjs/toolkit';

import { WorkspaceState } from './types';

const initialState: WorkspaceState = {
  csrfToken: null,
  editId: null,
  labelTodoId: null,
  filterLabels: [],
  loggedIn: Platform.OS === 'web',
};
export default createSlice({
  name: 'workspace',
  initialState,
  reducers: {
    filterByLabels: (state, action) => {
      state.filterLabels = Array.from(action.payload);
    },
    logIn: (state, action) => {
      state.loggedIn = action.payload.loggedIn;
      state.csrfToken = action.payload.csrfToken;
    },
    setTodoLabelingId: (state, action) => {
      state.labelTodoId = action.payload;
    },
    setTodoEditId: (state, action) => {
      state.editId = action.payload;
    },
  },
});
