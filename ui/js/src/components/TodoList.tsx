import React, { useMemo } from 'react';
import {
  Platform,
  StyleProp,
  StyleSheet,
  TouchableOpacity,
  View,
  ViewStyle,
} from 'react-native';
import DraggableFlatList, {
  RenderItemParams,
  ScaleDecorator,
} from 'react-native-draggable-flatlist';

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
  scrollView: ViewStyle;
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

  const renderItem = ({ item, drag, isActive }: RenderItemParams<Todo>) => {
    return (
      <ScaleDecorator>
        <TouchableOpacity onLongPress={drag} disabled={isActive}>
          <TodoItem
            editing={item.id === editTodoId}
            key={item.id || ''}
            labeling={item.id === labelTodoId}
            setEditTodoId={setEditTodoId}
            setLabelTodoId={setLabelTodoId}
            todo={item}
            updateTodo={updateTodo}
          />
        </TouchableOpacity>
      </ScaleDecorator>
    );
  };

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
    loadingPage = <LoadingPage />;
  }

  return (
    <React.Fragment>
      <View style={containerStyle}>
        <AddTodo createTodo={createTodo} />
        {workContextFilter}
        {labelFilter}
        <DraggableFlatList
          containerStyle={styles.scrollView}
          testID="todo-list"
          data={todos}
          onDragEnd={(data) => console.log(data)}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
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
