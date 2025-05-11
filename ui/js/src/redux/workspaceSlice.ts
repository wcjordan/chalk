import { Platform } from 'react-native';
import { createSlice } from '@reduxjs/toolkit';

import { FILTER_STATUS, FilterState, WorkContext, WorkspaceState } from './types';

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
      backlog: FILTER_STATUS.Inverted,
    },
  },
  quickFixes: {
    displayName: 'Quick Fixes',
    labels: {
      '5 minutes': FILTER_STATUS.Active,
      backlog: FILTER_STATUS.Inverted,
    },
  },
  upNext: {
    displayName: 'Up Next',
    labels: {
      backlog: FILTER_STATUS.Inverted,
      'up next': FILTER_STATUS.Active,
    },
  },
  work: {
    displayName: 'Work',
    labels: {
      backlog: FILTER_STATUS.Inverted,
      work: FILTER_STATUS.Active,
    },
  },
  shopping: {
    displayName: 'Shopping',
    labels: {
      backlog: FILTER_STATUS.Inverted,
      Shopping: FILTER_STATUS.Active,
    },
  },
  chalkPlanning: {
    displayName: 'Chalk Planning',
    labels: {
      Chalk: FILTER_STATUS.Active,
      backlog: FILTER_STATUS.Inverted,
      vague: FILTER_STATUS.Active,
    },
  },
};

const initialState: WorkspaceState = {
  csrfToken: null,
  editTodoId: null,
  filterLabels: {
    Unlabeled: FILTER_STATUS.Active,
  },
  labelTodoId: null,
  loggedIn: Platform.OS === 'web',
  showCompletedTodos: false,
  showLabelFilter: false,
};
export default createSlice({
  name: 'workspace',
  initialState,
  reducers: {
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
    setFilters: (state, action) => {
      const { activeLabels = [], invertedLabels = [] } = action.payload;
      const newLabels : FilterState = {};

      // Set active labels
      activeLabels.forEach((label: string) => {
        newLabels[label] = FILTER_STATUS.Active;
      });

      // Set inverted labels
      invertedLabels.forEach((label: string) => {
        newLabels[label] = FILTER_STATUS.Inverted;
      });

      state.filterLabels = newLabels;
    },
    toggleLabel: (state, action) => {
      const newLabels = Object.assign({}, state.filterLabels);
      const toggledLabel = action.payload;

      // Remove the Unlabeled label when enabling another label
      // This is a small feature because no todo can be both Unlabeled and match a label
      if (toggledLabel !== 'Unlabeled') {
        delete newLabels['Unlabeled'];
      }

      const prevStatus = newLabels[toggledLabel];
      if (prevStatus === FILTER_STATUS.Active) {
        // Invert existing item
        newLabels[toggledLabel] = FILTER_STATUS.Inverted;
      } else if (prevStatus === FILTER_STATUS.Inverted) {
        // Delete inverted item
        delete newLabels[toggledLabel];
      } else {
        newLabels[toggledLabel] = FILTER_STATUS.Active;
      }

      state.filterLabels = newLabels;
    },
    toggleShowCompletedTodos: (state) => {
      state.showCompletedTodos = !state.showCompletedTodos;
    },
    toggleShowLabelFilter: (state) => {
      state.showLabelFilter = !state.showLabelFilter;
    },
  },
});
