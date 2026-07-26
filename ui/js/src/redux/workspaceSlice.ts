import { Platform } from 'react-native';
import { createSlice } from '@reduxjs/toolkit';

import {
  FILTER_STATUS,
  FilterState,
  WorkContext,
  WorkspaceState,
} from './types';

// TODO (jordan) Improve to support or'd label groups
// Will be useful for adding Chalk + vague to Chalk Planning

// Backlogged and snoozed todos are hidden from work contexts by default;
// merge this in for any context that shouldn't override that default.
const withDefaultInversions = (labels: FilterState): FilterState => ({
  backlog: FILTER_STATUS.Inverted,
  snoozed: FILTER_STATUS.Inverted,
  ...labels,
});

export const workContexts: { [key: string]: WorkContext } = {
  inbox: {
    displayName: 'Inbox',
    labels: {
      Unlabeled: FILTER_STATUS.Active,
      snoozed: FILTER_STATUS.Inverted,
    },
  },
  urgent: {
    displayName: 'Urgent',
    labels: withDefaultInversions({
      urgent: FILTER_STATUS.Active,
    }),
  },
  quickFixes: {
    displayName: 'Quick Fixes',
    labels: withDefaultInversions({
      '5 minutes': FILTER_STATUS.Active,
    }),
  },
  upNext: {
    displayName: 'Up Next',
    labels: withDefaultInversions({
      'up next': FILTER_STATUS.Active,
    }),
  },
  work: {
    displayName: 'Work',
    labels: withDefaultInversions({
      work: FILTER_STATUS.Active,
    }),
  },
  shopping: {
    displayName: 'Shopping',
    labels: withDefaultInversions({
      Shopping: FILTER_STATUS.Active,
    }),
  },
  chalkPlanning: {
    displayName: 'Chalk Planning',
    labels: withDefaultInversions({
      Chalk: FILTER_STATUS.Active,
      vague: FILTER_STATUS.Active,
    }),
  },
  snoozed: {
    displayName: 'Snoozed',
    labels: {
      snoozed: FILTER_STATUS.Active,
    },
  },
};

const initialState: WorkspaceState = {
  csrfToken: null,
  editTodoId: null,
  filterLabels: {
    Unlabeled: FILTER_STATUS.Active,
    snoozed: FILTER_STATUS.Inverted,
  },
  labelTodoId: null,
  loggedIn: Platform.OS === 'web',
  showCompletedTodos: false,
  showLabelFilter: false,
  snoozeTodoId: null,
};
export const workspaceSlice = createSlice({
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
      const newLabels: FilterState = {};

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
    setSnoozeTodoId: (state, action) => {
      state.snoozeTodoId = action.payload;
    },
  },
});
