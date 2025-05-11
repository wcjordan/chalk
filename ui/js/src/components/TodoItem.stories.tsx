import React from 'react';
import { Provider } from 'react-redux';
import { setupStore } from '../redux/store';
import TodoItem from './TodoItem';

const wrapper = (component) => (
  <Provider store={setupStore()}>{component}</Provider>
);

const defaultTodo = {
  archived: false,
  completed: false,
  created_at: null,
  description: 'Default Todo',
  labels: ['errand', '5min', 'low-effort'],
};
const defaultProps = {
  editing: false,
  todo: defaultTodo,
};

export default {
  title: 'Todo Item',
  component: TodoItem,
};
export const DefaultTodo: React.FC = () =>
  wrapper(<TodoItem {...defaultProps} />);

export const CheckedTodo: React.FC = () =>
  wrapper(
    <TodoItem
      {...defaultProps}
      todo={Object.assign({}, defaultTodo, {
        completed: true,
        description: 'Checked Todo',
      })}
    />,
  );

export const EditingTodo: React.FC = () =>
  wrapper(
    <TodoItem
      {...defaultProps}
      editing={true}
      todo={Object.assign({}, defaultTodo, {
        description: 'Editing Todo',
      })}
    />,
  );

export const NoLabelsTodo: React.FC = () =>
  wrapper(
    <TodoItem
      {...defaultProps}
      todo={Object.assign({}, defaultTodo, {
        description: 'No Labels Todo',
        labels: [],
      })}
    />,
  );

export const WrappedLabelsTodo: React.FC = () =>
  wrapper(
    <TodoItem
      {...defaultProps}
      todo={Object.assign({}, defaultTodo, {
        description: 'Wrapped Labels Todo',
        labels: [
          'low-energy',
          'high-energy',
          'vague',
          'work',
          'home',
          'errand',
          'mobile',
          'desktop',
          'email',
          'urgent',
          '5 minutes',
          '25 minutes',
          '60 minutes',
        ],
      })}
    />,
  );
