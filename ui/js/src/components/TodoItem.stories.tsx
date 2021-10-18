import React from 'react';
import TodoItem from './TodoItem';

const defaultTodo = {
  archived: false,
  completed: false,
  created_at: null,
  description: 'Default Todo',
};
const defaultProps = {
  editing: false,
  todo: defaultTodo,
};

export default {
  title: 'Todo Item',
  component: TodoItem,
};
export const DefaultTodo: React.FC = () => <TodoItem {...defaultProps} />;

export const CheckedTodo: React.FC = () => (
  <TodoItem
    {...defaultProps}
    todo={Object.assign({}, defaultTodo, {
      completed: true,
      description: 'Checked Todo',
    })}
  />
);

export const EditingTodo: React.FC = () => (
  <TodoItem
    {...defaultProps}
    editing={true}
    todo={Object.assign({}, defaultTodo, {
      description: 'Editing Todo',
    })}
  />
);
