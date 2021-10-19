import React from 'react';
import { App } from './App';
import { Todo, TodoPatch } from './redux/types';

function stubTodo(patch: TodoPatch): Todo {
  return Object.assign(
    {
      archived: false,
      completed: false,
      created_at: null,
      description: `New todo`,
      label_set: [],
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
  todos: [
    stubTodo({
      id: 1,
      description: 'First todo',
    }),
    stubTodo({
      id: 2,
      description: '2nd todo',
    }),
  ],
  workspace: {
    labelTodoId: null,
    selectedLabels: {
      '5 minutes': true,
      work: true,
      home: true,
      'low-energy': true,
      mobile: true,
    },
  },
};

export default {
  title: 'App',
  component: App,
};
export const DefaultLayout: React.FC = () => (
  <App {...defaultProps} todos={[]} />
);

export const ListTodosLayout: React.FC = () => <App {...defaultProps} />;

const labelPickerWorkspace = Object.assign({}, defaultProps.workspace, {
  labelTodoId: 1,
});
export const LabelPickerLayout: React.FC = () => (
  <App {...defaultProps} workspace={labelPickerWorkspace} />
);
