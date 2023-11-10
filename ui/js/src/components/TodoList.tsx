import React, { useCallback, useMemo } from 'react';
import { Platform, StyleProp, StyleSheet, View, ViewStyle } from 'react-native';
import DraggableFlatList, {
  RenderItemParams,
  OpacityDecorator,
} from 'react-native-draggable-flatlist';

import {
  Label,
  MoveTodoOperation,
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
  scrollView: ViewStyle;
  spacer: ViewStyle;
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
  scrollView: {
    flex: 1,
    minHeight: 20,
  },
  spacer: {
    flexGrow: 1,
  },
});

const TodoList: React.FC<Props> = function (props: Props) {
  const {
    activeWorkContext,
    createTodo,
    isLoading,
    labels,
    moveTodo,
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

  const handleReorder: (params: {
    data: Todo[];
    from: number;
    to: number;
  }) => void = useCallback(
    ({ from, to, data }) => {
      if (from === to) {
        return;
      }

      const beforeFlag = from > to;
      const position = beforeFlag ? 'before' : 'after';
      const relativeIdx = beforeFlag ? to + 1 : to - 1;
      moveTodo({
        todo_id: data[to].id,
        position,
        relative_id: data[relativeIdx].id,
      });
    },
    [moveTodo],
  );

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

  const renderItem = ({ item, drag, isActive }: RenderItemParams<Todo>) => (
    <OpacityDecorator activeOpacity={0.65}>
      <TodoItem
        editing={item.id === editTodoId}
        isDragging={isActive}
        key={item.id || ''}
        labeling={item.id === labelTodoId}
        setEditTodoId={setEditTodoId}
        setLabelTodoId={setLabelTodoId}
        startDrag={drag}
        todo={item}
        updateTodo={updateTodo}
      />
    </OpacityDecorator>
  );

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

  let loadingPage = null;
  if (isLoading) {
    loadingPage = (
      <React.Fragment>
        <LoadingPage />
        <View style={styles.spacer} key="spacer-after" />
      </React.Fragment>
    );
  }

  return (
    <React.Fragment>
      <View style={containerStyle}>
        <AddTodo createTodo={createTodo} />
        {workContextFilter}
        {labelFilter}
        <DraggableFlatList
          autoscrollSpeed={150}
          containerStyle={styles.scrollView}
          data={todos}
          onDragEnd={handleReorder}
          keyExtractor={(item) => String(item.id || '')}
          refreshing={isLoading}
          renderItem={renderItem}
          testID="todo-list"
        />
        {loadingPage}
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
  moveTodo: (operation: MoveTodoOperation) => void;
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
