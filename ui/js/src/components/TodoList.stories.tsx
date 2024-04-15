import _ from 'lodash';
import React from 'react';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Todo, TodoPatch } from '../redux/types';
import { FILTER_STATUS } from '../redux/types';
import { setupStore } from '../redux/store';
import TodoList from './TodoList';

function stubTodo(patch: TodoPatch): Todo {
  return Object.assign(
    {
      archived: false,
      completed: false,
      created_at: null,
      description: `New todo`,
      labels: ['low-energy', 'vague', 'work', 'home', 'mobile', '5 minutes'],
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
      stubTodo({
        id: 3,
        description: '3rd todo',
      }),
      stubTodo({
        id: 4,
        description: '4th todo',
      }),
      stubTodo({
        id: 5,
        description: '5th todo',
      }),
      stubTodo({
        id: 6,
        description: '6th todo',
      }),
    ],
  },
  workspace: {
    editTodoId: 3,
    filterLabels: {
      '5 minutes': FILTER_STATUS.Active,
      work: FILTER_STATUS.Active,
      home: FILTER_STATUS.Active,
      'low-energy': FILTER_STATUS.Active,
      mobile: FILTER_STATUS.Active,
    },
    labelTodoId: null,
  },
};

const wrapper = (component, stateOverrides={}) => {
  const initialState = _.mergeWith({}, defaultState, stateOverrides, (objValue, srcValue) => {
    if (_.isArray(objValue)) {
      return srcValue;
    }
    return undefined;
  });
  return (
    <SafeAreaProvider>
      <Provider store={setupStore(initialState)}>
        {component}
      </Provider>
    </SafeAreaProvider>
  );
};

export default {
  title: 'Todo List',
  component: TodoList,
};
export const DefaultTodoList: React.FC = () =>
  wrapper(<TodoList />);

export const LabelPickerOverlay: React.FC = () =>
  wrapper(<TodoList />, {
    workspace: {
      editTodoId: null,
      labelTodoId: 3,
    },
  });

export const LoadingIndicator: React.FC = () =>
  wrapper(
    <TodoList />, {
      todosApi: {
        initialLoad: true,
        entries: [stubTodo({ id: 1, description: 'New todo' })],
      },
    }
  );
