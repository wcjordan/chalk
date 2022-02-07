import React from 'react';
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
  workspace: {
    filterLabels: ['5 minutes', 'work', 'home', 'low-energy', 'mobile'],
    labelTodoId: null,
    editId: 3,
  },
};

export default {
  title: 'Todo List',
  component: TodoList,
};
export const DefaultTodoList: React.FC = () => <TodoList {...defaultProps} />;

const labelPickerWorkspace = Object.assign({}, defaultProps.workspace, {
  labelTodoId: 3,
  editId: null,
});
export const LabelPickerOverlay: React.FC = () => (
  <TodoList {...defaultProps} workspace={labelPickerWorkspace} />
);
