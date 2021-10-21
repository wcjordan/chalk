import React from 'react';
import TodoItem from './TodoItem';

const defaultTodo = {
  archived: false,
  completed: false,
  created_at: null,
  description: 'Default Todo',
  label_set: ['errand', '5min', 'low-effort'],
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

export const NoLabelsTodo: React.FC = () => (
  <TodoItem
    {...defaultProps}
    todo={Object.assign({}, defaultTodo, {
      description: 'No Labels Todo',
      label_set: [],
    })}
  />
);

export const WrappedLabelsTodo: React.FC = () => (
  <TodoItem
    {...defaultProps}
    todo={Object.assign({}, defaultTodo, {
      description: 'Wrapped Labels Todo',
      label_set: [
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
  />
);
