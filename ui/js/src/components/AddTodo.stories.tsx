import React from 'react';
import AddTodo from './AddTodo';

export default {
  title: 'Add Todo',
  component: AddTodo,
};

const defaultProps = {
  createTodo: () => null,
};

export const DefaultAddTodo = () => <AddTodo {...defaultProps} />;
