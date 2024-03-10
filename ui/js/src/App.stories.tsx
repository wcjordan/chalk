import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { FILTER_STATUS, Todo, TodoPatch } from './redux/types';
import App from './App';

function stubTodo(patch: TodoPatch): Todo {
  return Object.assign(
    {
      archived: false,
      completed: false,
      created_at: null,
      description: `New todo`,
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
    },
    patch,
  );
}

const defaultProps = {
  labels: [
    { name: 'low-energy' },
    { name: 'high-energy' },
    { name: 'vague' },
    { name: 'work' },
    { name: 'home' },
    { name: 'errand' },
    { name: 'mobile' },
    { name: 'desktop' },
    { name: 'email' },
    { name: 'urgent' },
    { name: '5 minutes' },
    { name: '25 minutes' },
    { name: '60 minutes' },
  ],
  notificationQueue: [],
  selectedPickerLabels: {
    '5 minutes': true,
    work: true,
    home: true,
    'low-energy': true,
    mobile: true,
  },
  todos: [
    stubTodo({
      id: 1,
      description: 'First todo',
    }),
    stubTodo({
      id: 2,
      description: '2nd todo',
    }),
  ],
  workspace: {
    csrfToken: null,
    filterLabels: {
      '5 minutes': FILTER_STATUS.Active,
      work: FILTER_STATUS.Inverted,
      home: FILTER_STATUS.Active,
      'low-energy': FILTER_STATUS.Active,
      mobile: FILTER_STATUS.Active,
    },
    labelTodoId: null,
    loggedIn: true,
  },
};

const wrapper = (app) => <SafeAreaProvider>{app}</SafeAreaProvider>;

export default {
  title: 'App Layout',
  component: App,
};
export const DefaultLayout: React.FC = () =>
  wrapper(<App {...defaultProps} todos={[]} />);

export const ListTodosLayout: React.FC = () =>
  wrapper(<App {...defaultProps} />);

const labelPickerWorkspace = Object.assign({}, defaultProps.workspace, {
  labelTodoId: 1,
});
export const LabelPickerLayout: React.FC = () =>
  wrapper(<App {...defaultProps} workspace={labelPickerWorkspace} />);

export const NotificationLayout: React.FC = () =>
  wrapper(
    <App {...defaultProps} notificationQueue={['Error logging in...']} />,
  );
