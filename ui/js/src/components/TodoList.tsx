import _ from 'lodash';
import React from 'react';
import {
  Platform,
  ScrollView,
  StyleProp,
  StyleSheet,
  View,
  ViewStyle,
} from 'react-native';

import { Label, Todo, TodoPatch, WorkspaceState } from '../redux/types';
import { useDataLoader } from '../hooks';
import AddTodo from './AddTodo';
import LabelFilter from './LabelFilter';
import LabelPicker from './LabelPicker';
import TodoItem from './TodoItem';

interface Style {
  containerMobile: ViewStyle;
  containerWeb: ViewStyle;
}
interface TopStyle {
  top: ViewStyle;
}

const styles = StyleSheet.create<Style>({
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

const TodoList: React.FC<Props> = function (props: Props) {
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

  useDataLoader();

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
    <React.Fragment>
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
    </React.Fragment>
  );
};

type Props = {
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

export default TodoList;
