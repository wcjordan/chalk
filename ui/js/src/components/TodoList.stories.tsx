import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Todo, TodoPatch } from '../redux/types';
import { FILTER_STATUS } from '../redux/types';
import { workContexts } from '../redux/workspaceSlice';
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

const defaultProps = {
  labels: [
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
  selectedPickerLabels: {
    '5 minutes': true,
    work: true,
    home: true,
    'low-energy': true,
    mobile: true,
  },
  todos: [
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
  workContexts,
  workspace: {
    editTodoId: 3,
    filterLabels: {
      '5 minutes': FILTER_STATUS.Active,
      work: FILTER_STATUS.Inverted,
      home: FILTER_STATUS.Active,
      'low-energy': FILTER_STATUS.Active,
      mobile: FILTER_STATUS.Active,
    },
    labelTodoId: null,
  },
};

const wrapper = (component) => <SafeAreaProvider>{component}</SafeAreaProvider>;

export default {
  title: 'Todo List',
  component: TodoList,
};
export const DefaultTodoList: React.FC = () =>
  wrapper(<TodoList {...defaultProps} />);

const labelPickerWorkspace = Object.assign({}, defaultProps.workspace, {
  editTodoId: null,
  labelTodoId: 3,
});
export const LabelPickerOverlay: React.FC = () =>
  wrapper(<TodoList {...defaultProps} workspace={labelPickerWorkspace} />);

export const LoadingIndicator: React.FC = () =>
  wrapper(
    <TodoList
      {...defaultProps}
      isLoading={true}
      todos={[stubTodo({ id: 1, description: 'New todo' })]}
    />,
  );
