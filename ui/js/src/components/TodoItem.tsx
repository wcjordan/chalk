import React, { useCallback } from 'react';
import {
  GestureResponderEvent,
  NativeSyntheticEvent,
  Platform,
  StyleSheet,
  TextInputSubmitEditingEventData,
  TextStyle,
  View,
  ViewStyle,
} from 'react-native';
import {
  Card,
  Checkbox,
  Colors,
  IconButton,
  Text,
  TextInput,
} from 'react-native-paper';
import { Todo, TodoPatch } from '../redux/types';

interface Style {
  checkbox: ViewStyle;
  editTodoInput: TextStyle;
  spacer: ViewStyle;
  todoDescription: TextStyle;
  todoDescriptionText: TextStyle;
  todoItemCard: ViewStyle & { cursor?: string };
  todoItemContent: ViewStyle;
}

const todoItemCardStyle: ViewStyle & { cursor?: string } = {
  borderRadius: 0,
};
if (Platform.OS === 'web') {
  todoItemCardStyle['cursor'] = 'pointer';
}

const styles = StyleSheet.create<Style>({
  checkbox: {
    paddingTop: 4,
  },
  editTodoInput: {
    borderWidth: 0,
    flexGrow: 1,
    marginLeft: 9,
    padding: 0,
  },
  spacer: {
    flexGrow: 1,
  },
  todoDescription: {
    marginLeft: 9,
    flexGrow: 1,
    flexBasis: 0,
  },
  todoDescriptionText: {
    fontSize: 16,
  },
  todoItemCard: todoItemCardStyle,
  todoItemContent: {
    flexDirection: 'row',
    width: '100%',
  },
});

const TodoItem: React.FC<Props> = function (props: Props) {
  const { editing, todo, setTodoEditId, uncommittedEdit, updateTodo } = props;

  const updateTodoCb = useCallback(
    (text: string) => {
      updateTodo(
        {
          id: todo.id,
          description: text,
        },
        false,
      );
    },
    [updateTodo, todo.id],
  );

  const commitTodo = useCallback(
    (event: NativeSyntheticEvent<TextInputSubmitEditingEventData>) => {
      updateTodo({
        id: todo.id,
        description: event.nativeEvent.text,
      });
    },
    [updateTodo, todo.id],
  );

  const toggleTodo = useCallback(() => {
    updateTodo({
      id: todo.id,
      completed: !todo.completed,
    });
  }, [updateTodo, todo.id, todo.completed]);

  const archiveTodo = useCallback(
    (event: GestureResponderEvent) => {
      event.stopPropagation();
      updateTodo({
        id: todo.id,
        archived: true,
      });
    },
    [updateTodo, todo.id],
  );

  const beginEdit = useCallback(() => {
    if (editing) {
      return;
    }

    setTodoEditId(todo.id);
  }, [setTodoEditId, todo.id, editing]);

  const cancelEdit = useCallback(() => {
    if (!editing) {
      return;
    }

    setTodoEditId(null);
  }, [setTodoEditId, editing]);

  let content;
  if (editing) {
    content = [
      <TextInput
        defaultValue={uncommittedEdit || todo.description}
        dense={true}
        key="input"
        multiline={true}
        numberOfLines={4}
        onChangeText={updateTodoCb}
        onSubmitEditing={commitTodo}
        selectTextOnFocus={true}
        style={styles.editTodoInput}
      />,
      <IconButton
        key="cancel"
        icon="cancel"
        color={Colors.grey800}
        size={20}
        onPress={cancelEdit}
      />,
    ];
  } else {
    content = [
      <View key="description" style={styles.todoDescription}>
        <View style={styles.spacer} />
        <Text key="descriptionText" style={styles.todoDescriptionText}>
          {todo.description}
        </Text>
        <View style={styles.spacer} />
      </View>,
      <IconButton
        key="delete"
        icon="trash-can-outline"
        color={Colors.red500}
        size={20}
        onPress={archiveTodo}
      />,
    ];
    if (uncommittedEdit) {
      content.push(
        <IconButton
          key="warn"
          icon="alert-outline"
          color={Colors.orange300}
          size={20}
        />,
        // title={`Uncommitted edit: ${uncommittedEdit}`}
        // TODO w/ onLongPress
      );
    }
  }

  const testId = `todo-${todo.completed ? 'checked' : 'unchecked'}-${todo.id}`;
  return (
    <Card onPress={beginEdit} testID={testId} style={styles.todoItemCard}>
      <Card.Content style={styles.todoItemContent}>
        <View style={styles.checkbox}>
          <Checkbox.Android
            status={todo.completed ? 'checked' : 'unchecked'}
            onPress={toggleTodo}
          />
        </View>
        {content}
      </Card.Content>
    </Card>
  );
};

type Props = {
  editing: boolean;
  todo: Todo;
  updateTodo: (todoPatch: TodoPatch, commitEdit?: boolean) => void;
  setTodoEditId: (id: number | null) => void;
  uncommittedEdit: string | undefined;
};

export default TodoItem;
