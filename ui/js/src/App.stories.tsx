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
    },
    patch,
  );
}

const defaultProps = {
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
    labelPickerVisible: false,
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
  labelPickerVisible: true,
});
export const LabelPickerLayout: React.FC = () => (
  <App {...defaultProps} workspace={labelPickerWorkspace} />
);
