import React from 'react';
import AddTodo from './AddTodo';

export default {
  title: 'Add Todo',
  component: AddTodo,
};

const defaultProps = {
  addTodo: () => null,
};

export const DefaultAddTodo = () => <AddTodo {...defaultProps} />;
