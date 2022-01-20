import { connect, ConnectedProps, useSelector } from 'react-redux';
import React from 'react';
import { StatusBar, StyleSheet, View, ViewStyle } from 'react-native';

import ErrorBar from './components/ErrorBar';
import Login from './components/Login';
import TodoList from './components/TodoList';
import {
  Label,
  ReduxState,
  Todo,
  TodoPatch,
  WorkspaceState,
} from './redux/types';
import {
  completeAuthentication,
  createTodo,
  dismissNotification,
  filterByLabels,
  setTodoEditId,
  setTodoLabelingId,
  updateTodo,
  updateTodoLabels,
} from './redux/reducers';
import { selectFilteredTodos, selectSelectedPickerLabels } from './selectors';

interface Style {
  root: ViewStyle;
}

// --columbia-blue: #d9f0ffff;
// --baby-blue-eyes: #a3d5ffff;
// --light-sky-blue: #83c9f4ff;
// --oxford-blue: #061a40ff;
// --usafa-blue: #0353a4ff;

const BG_COLOR = '#061a40ff';
const styles = StyleSheet.create<Style>({
  root: {
    height: '100%',
    width: '100%',
    backgroundColor: BG_COLOR,
  },
});

const App: React.FC<ConnectedProps<typeof connector>> = function (
  props: ConnectedProps<typeof connector>,
) {
  const selectedPickerLabels = useSelector(selectSelectedPickerLabels);
  const filteredTodos = useSelector(selectFilteredTodos);
  return (
    <AppLayout
      {...props}
      filteredTodos={filteredTodos}
      selectedPickerLabels={selectedPickerLabels}
    />
  );
};

export const AppLayout: React.FC<LayoutProps> = function (props: LayoutProps) {
  const {
    completeAuthentication,
    dismissNotification,
    filteredTodos,
    notificationQueue,
    workspace,
    ...otherProps
  } = props;
  const { loggedIn } = workspace;

  let content: JSX.Element | null = null;
  if (!loggedIn) {
    content = <Login completeAuthentication={completeAuthentication} />;
  } else {
    content = (
      <TodoList todos={filteredTodos} workspace={workspace} {...otherProps} />
    );
  }

  const notificationText =
    notificationQueue.length > 0 ? notificationQueue[0] : null;
  return (
    <View style={styles.root}>
      <StatusBar
        animated={true}
        backgroundColor={BG_COLOR}
        barStyle={'light-content'}
      />
      {content}
      <ErrorBar
        key={notificationText}
        text={notificationText}
        dismissNotification={dismissNotification}
      />
    </View>
  );
};

type LayoutProps = {
  completeAuthentication: (token: string) => void;
  createTodo: (description: string) => void;
  dismissNotification: () => void;
  filterByLabels: (labels: string[]) => void;
  filteredTodos: Todo[];
  labels: Label[];
  notificationQueue: string[];
  selectedPickerLabels: { [label: string]: boolean };
  setTodoEditId: (id: number | null) => void;
  setTodoLabelingId: (id: number | null) => void;
  updateTodo: (todoPatch: TodoPatch) => void;
  updateTodoLabels: (labels: string[]) => void;
  workspace: WorkspaceState;
};

const mapStateToProps = (state: ReduxState) => {
  return {
    labels: state.labelsApi.entries,
    workspace: state.workspace,
    notificationQueue: state.notifications.notificationQueue,
  };
};
const mapDispatchToProps = {
  completeAuthentication,
  createTodo,
  dismissNotification,
  filterByLabels,
  setTodoEditId,
  setTodoLabelingId,
  updateTodo,
  updateTodoLabels,
};
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
