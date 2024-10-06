import React, { memo, useCallback } from 'react';
import { Platform, StyleProp, StyleSheet, View, ViewStyle } from 'react-native';
import DraggableFlatList, {
  RenderItemParams,
  OpacityDecorator,
} from 'react-native-draggable-flatlist';
import {
  selectActiveWorkContext,
  selectFilteredTodos,
  selectIsLoading,
  selectLabelNames,
  selectSelectedPickerLabels,
} from '../selectors';
import { useAppDispatch, useAppSelector, useDataLoader } from '../hooks';
import { Todo } from '../redux/types';
import { moveTodo } from '../redux/reducers';
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

const TodoList: React.FC = memo(function () {
  const dispatch = useAppDispatch()
  useDataLoader();
  const {
    editTodoId,
    filterLabels,
    labelTodoId,
    showCompletedTodos,
    showLabelFilter,
  } = useAppSelector((state) => state.workspace);
  const activeWorkContext = useAppSelector(selectActiveWorkContext);
  const isLoading = useAppSelector(selectIsLoading);
  const labelNames = useAppSelector(selectLabelNames);
  const selectedPickerLabels = useAppSelector(selectSelectedPickerLabels);
  const filteredTodos = useAppSelector(selectFilteredTodos);

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
      dispatch(moveTodo({
        todo_id: data[to].id,
        position,
        relative_id: data[relativeIdx].id,
      }));
    },
    [],
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

  const renderItem = useCallback(({ item, drag, isActive }: RenderItemParams<Todo>) => (
    <OpacityDecorator activeOpacity={0.65}>
      <TodoItem
        editing={item.id === editTodoId}
        isDragging={isActive}
        key={item.id || ''}
        labeling={item.id === labelTodoId}
        startDrag={drag}
        todo={item}
      />
    </OpacityDecorator>
  ), [editTodoId, labelTodoId]);

  let labelFilter = null;
  let workContextFilter = null;
  if (showLabelFilter) {
    labelFilter = <LabelFilter />;
  } else {
    workContextFilter = (
      <WorkContextFilter
        activeWorkContext={activeWorkContext}
        isFiltered={Object.keys(filterLabels).length > 0}
        showCompletedTodos={showCompletedTodos}
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

  let draggableList = null;
  if (filteredTodos.length > 0) {
    draggableList = (
      <DraggableFlatList
        activationDistance={Platform.OS === 'web' ? 10 : null}
        autoscrollSpeed={Platform.OS === 'web' ? 50 : 150}
        containerStyle={styles.scrollView}
        data={filteredTodos}
        onDragEnd={handleReorder}
        keyExtractor={(item) => String(item.id || '')}
        refreshing={isLoading}
        renderItem={renderItem}
        testID="todo-list"
        windowSize={Platform.OS === 'web' ? 3 : null}
      />
    );
  }
  return (
    <React.Fragment>
      <View style={containerStyle}>
        <AddTodo />
        {workContextFilter}
        {labelFilter}
        {draggableList}
        {loadingPage}
      </View>
      <LabelPicker
        labels={labelNames}
        selectedLabels={selectedPickerLabels}
        visible={labelTodoId !== null}
      />
    </React.Fragment>
  );
});

export default TodoList;
