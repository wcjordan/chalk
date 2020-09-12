import React from 'react';
import TodoItem from './TodoItem';

export default {
  title: 'Todo Item',
  component: TodoItem,
};

const defaultProps = {
  todo: {
    description: 'Default Todo',
    // completed: false,
  },
};

export const DefaultTodo = () => <TodoItem {...defaultProps} />;

const checkedProps = {
  todo: {
    description: 'Checked Todo',
    // completed: true,
  },
};

export const CheckedTodo = () => <TodoItem {...checkedProps} />;
