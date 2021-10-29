import React from 'react';
import { AppLayout } from './App';
import { Todo, TodoPatch } from './redux/types';

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
  ],
  workspace: {
    filterLabels: ['5 minutes', 'work', 'home', 'low-energy', 'mobile'],
    labelTodoId: null,
  },
};

export default {
  title: 'App Layout',
  component: AppLayout,
};
export const DefaultLayout: React.FC = () => (
  <AppLayout {...defaultProps} todos={[]} />
);

export const ListTodosLayout: React.FC = () => <AppLayout {...defaultProps} />;

const labelPickerWorkspace = Object.assign({}, defaultProps.workspace, {
  labelTodoId: 1,
});
export const LabelPickerLayout: React.FC = () => (
  <AppLayout {...defaultProps} workspace={labelPickerWorkspace} />
);
