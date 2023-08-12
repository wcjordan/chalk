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
  Todo,
  TodoPatch,
  WorkContext,
  WorkspaceState,
} from '../redux/types';
import { useDataLoader } from '../hooks';
import AddTodo from './AddTodo';
import LabelFilter from './LabelFilter';
import LabelPicker from './LabelPicker';
import LoadingPage from './LoadingPage';
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
    isLoading,
    labels,
    selectedPickerLabels,
    setEditTodoId,
    setLabelTodoId,
    setWorkContext,
    showCompletedTodos,
    showLabelFilter,
    todos,
    toggleLabel,
    toggleShowCompletedTodos,
    toggleShowLabelFilter,
    updateTodo,
    updateTodoLabels,
    workContexts,
    workspace,
  } = props;
  const { editTodoId, filterLabels, labelTodoId } = workspace;

  useDataLoader();
  const labelNames = useMemo(() => labels.map((label) => label.name), [labels]);

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

  if (isLoading) {
    return (
      <View style={containerStyle}>
        <LoadingPage />
      </View>
    );
  }

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

  let labelFilter = null;
  let workContextFilter = null;
  if (showLabelFilter) {
    labelFilter = (
      <LabelFilter
        labels={labelNames}
        selectedLabels={filterLabels}
        showCompletedTodos={showCompletedTodos}
        showLabelFilter={showLabelFilter}
        toggleLabel={toggleLabel}
        toggleShowCompletedTodos={toggleShowCompletedTodos}
        toggleShowLabelFilter={toggleShowLabelFilter}
      />
    );
  } else {
    workContextFilter = (
      <WorkContextFilter
        activeWorkContext={activeWorkContext}
        isFiltered={Object.keys(filterLabels).length > 0}
        setWorkContext={setWorkContext}
        showCompletedTodos={showCompletedTodos}
        showLabelFilter={showLabelFilter}
        toggleShowCompletedTodos={toggleShowCompletedTodos}
        toggleShowLabelFilter={toggleShowLabelFilter}
        workContexts={workContexts}
      />
    );
  }

  return (
    <React.Fragment>
      <View style={containerStyle}>
        <AddTodo createTodo={createTodo} />
        {workContextFilter}
        {labelFilter}
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
  isLoading: boolean;
  labels: Label[];
  selectedPickerLabels: { [label: string]: boolean };
  setEditTodoId: (id: number | null) => void;
  setLabelTodoId: (id: number | null) => void;
  setWorkContext: (workContext: string) => void;
  showCompletedTodos: boolean;
  showLabelFilter: boolean;
  todos: Todo[];
  toggleLabel: (label: string) => void;
  toggleShowCompletedTodos: () => void;
  toggleShowLabelFilter: () => void;
  updateTodo: (todoPatch: TodoPatch) => void;
  updateTodoLabels: (labels: string[]) => void;
  workContexts: { [key: string]: WorkContext };
  workspace: WorkspaceState;
};

export default TodoList;
