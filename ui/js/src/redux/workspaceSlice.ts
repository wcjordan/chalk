import { Platform } from 'react-native';
import { createSlice } from '@reduxjs/toolkit';

import { WorkContext, WorkspaceState } from './types';

// TODO (jordan) Improve to support or'd label groups
// Will be useful for adding Chalk + vague to Chalk Planning
export const workContexts: { [key: string]: WorkContext } = {
  inbox: {
    displayName: 'Inbox',
    labels: ['Unlabeled'],
  },
  chores: {
    displayName: 'Chores',
    labels: ['errand'],
  },
  quickFixes: {
    displayName: 'Quick Fixes',
    labels: ['5 minutes'],
  },
  chalkCoding: {
    displayName: 'Chalk Coding',
    labels: ['Chalk', '25 minutes'],
  },
  chalkPlanning: {
    displayName: 'Chalk Planning',
    labels: ['Chalk', '60 minutes'],
  },
};

const initialState: WorkspaceState = {
  csrfToken: null,
  labelTodoId: null,
  filterLabels: [],
  loggedIn: Platform.OS === 'web',
  editTodoId: null,
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
    setEditTodoId: (state, action) => {
      state.editTodoId = action.payload;
    },
    setLabelTodoId: (state, action) => {
      state.labelTodoId = action.payload;
    },
    setWorkContext: (state, action) => {
      const workContext = workContexts[action.payload];
      if (workContext) {
        state.filterLabels = Array.from(workContext.labels);
      }
    },
  },
});
