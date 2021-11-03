import _ from 'lodash';
import { connect, ConnectedProps, useSelector } from 'react-redux';
import React from 'react';
import {
  Platform,
  ScrollView,
  StatusBar,
  StyleProp,
  StyleSheet,
  View,
  ViewStyle,
} from 'react-native';
import AddTodo from './components/AddTodo';
import LabelFilter from './components/LabelFilter';
import LabelPicker from './components/LabelPicker';
import {
  Label,
  ReduxState,
  Todo,
  TodoPatch,
  WorkspaceState,
} from './redux/types';
import TodoItem from './components/TodoItem';
import {
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
  containerMobile: ViewStyle;
  containerWeb: ViewStyle;
}
interface TopStyle {
  top: ViewStyle;
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
  containerMobile: {
    height: '100%',
    width: '100%',
  },
  containerWeb: {
    height: '100%',
    width: '66%',
    marginHorizontal: 'auto',
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
    createTodo,
    labels,
    filterByLabels,
    filteredTodos,
    selectedPickerLabels,
    setTodoEditId,
    setTodoLabelingId,
    updateTodo,
    updateTodoLabels,
    workspace,
  } = props;
  const { editId, filterLabels, labelTodoId } = workspace;

  // TODO (jordan) look into memoizing
  const labelNames = labels.map((label) => label.name);

  const todoViews = _.map(filteredTodos, (todo) => (
    <TodoItem
      setTodoLabelingId={setTodoLabelingId}
      editing={todo.id === editId}
      key={todo.id || ''}
      setTodoEditId={setTodoEditId}
      todo={todo}
      updateTodo={updateTodo}
    />
  ));

  let containerStyle: StyleProp<ViewStyle> =
    Platform.OS === 'web' ? styles.containerWeb : styles.containerMobile;
  if (Platform.OS === 'web') {
    const topStyle = StyleSheet.create<TopStyle>({
      top: {
        paddingTop: 20,
      },
    }).top;
    containerStyle = StyleSheet.compose(containerStyle, topStyle);
  }

  return (
    <View style={styles.root}>
      <StatusBar
        animated={true}
        backgroundColor={BG_COLOR}
        barStyle={'light-content'}
      />
      <View style={containerStyle}>
        <AddTodo createTodo={createTodo} />
        <LabelFilter
          labels={labelNames}
          selectedLabels={filterLabels}
          filterByLabels={filterByLabels}
        />
        <ScrollView testID="todo-list">{todoViews}</ScrollView>
      </View>
      <LabelPicker
        labels={labelNames}
        selectedLabels={selectedPickerLabels}
        setTodoLabelingId={setTodoLabelingId}
        updateTodoLabels={updateTodoLabels}
        visible={labelTodoId !== null}
      />
    </View>
  );
};

type LayoutProps = {
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
  createTodo,
  filterByLabels,
  setTodoEditId,
  setTodoLabelingId,
  updateTodo,
  updateTodoLabels,
};
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
