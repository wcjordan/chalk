import React from 'react';
import { Provider } from 'react-redux';
import { setupStore } from '../redux/store';
import AddTodo from './AddTodo';

const wrapper = (component) => (
  <Provider store={setupStore()}>{component}</Provider>
);

export default {
  title: 'Add Todo',
  component: AddTodo,
};
export const DefaultAddTodo: React.FC = () => wrapper(<AddTodo />);
