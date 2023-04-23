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
  addNotification,
  completeAuthentication,
  createTodo,
  dismissNotification,
  setEditTodoId,
  setLabelTodoId,
  setWorkContext,
  toggleLabel,
  updateTodo,
  updateTodoLabels,
} from './redux/reducers';
import {
  selectActiveWorkContext,
  selectFilteredTodos,
  selectSelectedPickerLabels,
} from './selectors';
import { workContexts } from './redux/workspaceSlice';

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
  const activeWorkContext = useSelector(selectActiveWorkContext);
  return (
    <AppLayout
      {...props}
      activeWorkContext={activeWorkContext}
      filteredTodos={filteredTodos}
      selectedPickerLabels={selectedPickerLabels}
    />
  );
};

export const AppLayout: React.FC<LayoutProps> = function (props: LayoutProps) {
  const {
    activeWorkContext,
    addNotification,
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
    content = (
      <Login
        addNotification={addNotification}
        completeAuthentication={completeAuthentication}
      />
    );
  } else {
    content = (
      <TodoList
        activeWorkContext={activeWorkContext}
        todos={filteredTodos}
        workContexts={workContexts}
        workspace={workspace}
        {...otherProps}
      />
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
  activeWorkContext: string | undefined;
  addNotification: (text: string) => void;
  completeAuthentication: (token: string) => void;
  createTodo: (description: string) => void;
  dismissNotification: () => void;
  filteredTodos: Todo[];
  labels: Label[];
  notificationQueue: string[];
  selectedPickerLabels: { [label: string]: boolean };
  setEditTodoId: (id: number | null) => void;
  setLabelTodoId: (id: number | null) => void;
  setWorkContext: (workContext: string) => void;
  toggleLabel: (label: string) => void;
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
  addNotification,
  completeAuthentication,
  createTodo,
  dismissNotification,
  setEditTodoId,
  setLabelTodoId,
  setWorkContext,
  toggleLabel,
  updateTodo,
  updateTodoLabels,
};
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
