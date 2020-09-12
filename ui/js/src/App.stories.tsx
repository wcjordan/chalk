import React from 'react';
import { App } from './App';

export default {
  title: 'App',
  component: App,
};

const defaultProps = {
  todos: [],
  createTodo: () => null,
};
export const DefaultLayout = () => <App {...defaultProps} />;
