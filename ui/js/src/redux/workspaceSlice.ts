import { Platform } from 'react-native';
import { createSlice } from '@reduxjs/toolkit';

import { FILTER_STATUS, WorkContext, WorkspaceState } from './types';

// TODO (jordan) Improve to support or'd label groups
// Will be useful for adding Chalk + vague to Chalk Planning
export const workContexts: { [key: string]: WorkContext } = {
  inbox: {
    displayName: 'Inbox',
    labels: {
      Unlabeled: FILTER_STATUS.Active,
    },
  },
  urgent: {
    displayName: 'Urgent',
    labels: {
      urgent: FILTER_STATUS.Active,
    },
  },
  chores: {
    displayName: 'Chores',
    labels: {
      errand: FILTER_STATUS.Active,
    },
  },
  quickFixes: {
    displayName: 'Quick Fixes',
    labels: {
      '5 minutes': FILTER_STATUS.Active,
    },
  },
  chalkCoding: {
    displayName: 'Chalk Coding',
    labels: {
      Chalk: FILTER_STATUS.Active,
      '25 minutes': FILTER_STATUS.Active,
    },
  },
  chalkPlanning: {
    displayName: 'Chalk Planning',
    labels: {
      Chalk: FILTER_STATUS.Active,
      '60 minutes': FILTER_STATUS.Active,
    },
  },
};

const initialState: WorkspaceState = {
  csrfToken: null,
  labelTodoId: null,
  filterLabels: {
    Unlabeled: FILTER_STATUS.Active,
  },
  loggedIn: Platform.OS === 'web',
  editTodoId: null,
};
export default createSlice({
  name: 'workspace',
  initialState,
  reducers: {
    filterByLabels: (state, action) => {
      state.filterLabels = Object.assign({}, action.payload);
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
        state.filterLabels = Object.assign({}, workContext.labels);
      }
    },
  },
});
