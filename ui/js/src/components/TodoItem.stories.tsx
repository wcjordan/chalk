import React from 'react';
import TodoItem from './TodoItem';

beforeAll(function() {
  // Stub Math.random so aria-labelledby is deterministic for font-awesome
  jest.spyOn(global.Math, 'random').mockImplementation(() => 0.5);
});

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
export const DefaultTodo = () => <TodoItem {...defaultProps} />;

export const CheckedTodo = () => (
  <TodoItem
    {...defaultProps}
    todo={Object.assign({}, defaultTodo, {
      completed: true,
      description: 'Checked Todo',
    })}
  />
);

export const EditingTodo = () => (
  <TodoItem
    {...defaultProps}
    editing={true}
    todo={Object.assign({}, defaultTodo, {
      description: 'Editing Todo',
    })}
  />
);

export const UncommittedEditTodo = () => (
  <TodoItem
    {...defaultProps}
    todo={Object.assign({}, defaultTodo, {
      description: 'Uncommitted Edit Todo',
    })}
    uncommittedEdit="Uncommitted edit..."
  />
);

export const EditingUncommittedTodo = () => (
  <TodoItem
    {...defaultProps}
    editing={true}
    todo={Object.assign({}, defaultTodo, {
      description: 'Editing Todo',
    })}
    uncommittedEdit="Uncommitted edit..."
  />
);
