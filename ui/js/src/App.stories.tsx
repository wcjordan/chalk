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
  todos: [],
  workspace: {
    uncommittedEdits: {},
  },
};

export default {
  title: 'App',
  component: App,
};
export const DefaultLayout: React.FC = () => <App {...defaultProps} />;

export const ListTodosLayout: React.FC = () => (
  <App
    {...defaultProps}
    todos={[
      stubTodo({
        id: 1,
        description: 'First todo',
      }),
      stubTodo({
        id: 2,
        description: '2nd todo',
      }),
    ]}
  />
);
