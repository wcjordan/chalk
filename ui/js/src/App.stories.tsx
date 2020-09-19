import React from 'react';
import { App } from './App';

export default {
  title: 'App',
  component: App,
};

const defaultProps = {
  createTodo: () => null,
  todos: [],
  workspace: {},
};
export const DefaultLayout = () => <App {...defaultProps} />;
