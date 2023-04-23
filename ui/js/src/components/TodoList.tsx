import _ from 'lodash';
import React, { useMemo } from 'react';
import {
  Platform,
  ScrollView,
  StyleProp,
  StyleSheet,
  View,
  ViewStyle,
} from 'react-native';

import {
  Label,
  FilterState,
  Todo,
  TodoPatch,
  WorkContext,
  WorkspaceState,
} from '../redux/types';
import { useDataLoader } from '../hooks';
import AddTodo from './AddTodo';
import LabelFilter from './LabelFilter';
import LabelPicker from './LabelPicker';
import TodoItem from './TodoItem';
import WorkContextFilter from './WorkContextFilter';

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
    activeWorkContext,
    createTodo,
    labels,
    filterByLabels,
    selectedPickerLabels,
    setEditTodoId,
    setLabelTodoId,
    setWorkContext,
    todos,
    updateTodo,
    updateTodoLabels,
    workContexts,
    workspace,
  } = props;
  const { editTodoId, filterLabels, labelTodoId } = workspace;

  useDataLoader();

  const labelNames = useMemo(() => labels.map((label) => label.name), [labels]);
  const todoViews = _.map(todos, (todo) => (
    <TodoItem
      editing={todo.id === editTodoId}
      key={todo.id || ''}
      labeling={todo.id === labelTodoId}
      setEditTodoId={setEditTodoId}
      setLabelTodoId={setLabelTodoId}
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
    containerStyle = [containerStyle, topStyle];
  }

  return (
    <React.Fragment>
      <View style={containerStyle}>
        <AddTodo createTodo={createTodo} />
        <WorkContextFilter
          activeWorkContext={activeWorkContext}
          setWorkContext={setWorkContext}
          workContexts={workContexts}
        />
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
        setLabelTodoId={setLabelTodoId}
        updateTodoLabels={updateTodoLabels}
        visible={labelTodoId !== null}
      />
    </React.Fragment>
  );
};

type Props = {
  activeWorkContext: string | undefined;
  createTodo: (description: string) => void;
  filterByLabels: (labels: FilterState) => void;
  labels: Label[];
  selectedPickerLabels: { [label: string]: boolean };
  setEditTodoId: (id: number | null) => void;
  setLabelTodoId: (id: number | null) => void;
  setWorkContext: (workContext: string) => void;
  todos: Todo[];
  updateTodo: (todoPatch: TodoPatch) => void;
  updateTodoLabels: (labels: string[]) => void;
  workContexts: { [key: string]: WorkContext };
  workspace: WorkspaceState;
};

export default TodoList;
