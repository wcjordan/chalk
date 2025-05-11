import _ from 'lodash';
import React from 'react';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { FILTER_STATUS, Todo, TodoPatch } from './redux/types';
import App from './App';
import { setupStore } from './redux/store';

function stubTodo(patch: TodoPatch): Todo {
  return Object.assign(
    {
      archived: false,
      completed: false,
      created_at: null,
      description: `New todo`,
      labels: [
        'low-energy',
        'high-energy',
        'vague',
        'work',
        'home',
        'errand',
        'mobile',
        'desktop',
        'email',
        'urgent',
        '5 minutes',
        '25 minutes',
        '60 minutes',
      ],
    },
    patch,
  );
}

const defaultState = {
  labelsApi: {
    entries: [
      { name: 'low-energy' },
      { name: 'high-energy' },
      { name: 'vague' },
      { name: 'work' },
      { name: 'home' },
      { name: 'errand' },
      { name: 'mobile' },
      { name: 'desktop' },
      { name: 'email' },
      { name: 'urgent' },
      { name: '5 minutes' },
      { name: '25 minutes' },
      { name: '60 minutes' },
    ],
  },
  notifications: {
    notificationQueue: [],
  },
  todosApi: {
    entries: [
      stubTodo({
        id: 1,
        description: 'First todo',
      }),
      stubTodo({
        id: 2,
        description: '2nd todo',
      }),
    ],
  },
  workspace: {
    csrfToken: null,
    filterLabels: {
      '5 minutes': FILTER_STATUS.Active,
      work: FILTER_STATUS.Active,
      home: FILTER_STATUS.Active,
      'low-energy': FILTER_STATUS.Active,
      mobile: FILTER_STATUS.Active,
    },
    labelTodoId: null,
    loggedIn: true,
  },
};

const wrapper = (component, stateOverrides = {}) => {
  const initialState = _.mergeWith(
    {},
    defaultState,
    stateOverrides,
    (objValue, srcValue) => {
      if (_.isArray(objValue)) {
        return srcValue;
      }
      return undefined;
    },
  );
  return (
    <SafeAreaProvider>
      <Provider store={setupStore(initialState)}>{component}</Provider>
    </SafeAreaProvider>
  );
};

export default {
  title: 'App Layout',
  component: App,
};
export const DefaultLayout: React.FC = () =>
  wrapper(<App />, {
    todosApi: {
      entries: [],
    },
  });

export const ListTodosLayout: React.FC = () => wrapper(<App />);

export const LabelPickerLayout: React.FC = () =>
  wrapper(<App />, {
    workspace: {
      labelTodoId: 1,
    },
  });

export const NotificationLayout: React.FC = () =>
  wrapper(<App />, {
    notifications: {
      notificationQueue: ['Error logging in...'],
    },
  });
