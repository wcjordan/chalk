import { connect, ConnectedProps, useSelector } from 'react-redux';
import React from 'react';
import { StatusBar, StyleSheet, View, ViewStyle } from 'react-native';

import TodoList from './components/TodoList';
import Login from './components/Login';
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
  const { completeAuthentication, workspace } = props;
  const { loggedIn } = workspace;

  let content: JSX.Element | null = null;
  if (!loggedIn) {
    content = <Login completeAuthentication={completeAuthentication} />;
  } else {
    content = <TodoList {...props} />;
  }

  return (
    <View style={styles.root}>
      <StatusBar
        animated={true}
        backgroundColor={BG_COLOR}
        barStyle={'light-content'}
      />
      {content}
    </View>
  );
};

type LayoutProps = {
  completeAuthentication: (token: string) => void;
  createTodo: (description: string) => void;
  filterByLabels: (labels: string[]) => void;
  filteredTodos: Todo[];
  labels: Label[];
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
  };
};
const mapDispatchToProps = {
  completeAuthentication,
  createTodo,
  filterByLabels,
  setTodoEditId,
  setTodoLabelingId,
  updateTodo,
  updateTodoLabels,
};
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
