import React, { useCallback } from 'react';
import {
  GestureResponderEvent,
  NativeSyntheticEvent,
  StyleSheet,
  TextInputSubmitEditingEventData,
  TextStyle,
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
  todoItem: TextStyle;
  todoDescription: TextStyle;
  editTodoInput: TextStyle;
}

const styles = StyleSheet.create<Style>({
  todoItem: {
    display: 'flex',
    flexDirection: 'row',
    fontFamily: 'monospace',
    padding: 8,
    fontSize: 20,
    width: '100%',
    borderTopWidth: 1,
    borderTopColor: '#e0fbfc',
    // cursor: 'pointer',
  },
  todoDescription: {
    marginLeft: 9,
    flexGrow: 1,
  },
  editTodoInput: {
    borderWidth: 0,
    flexGrow: 1,
    marginLeft: 9,
    padding: 0,
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
        key="input"
        style={styles.editTodoInput}
        onChangeText={updateTodoCb}
        onSubmitEditing={commitTodo}
        selectTextOnFocus={true}
      />,
      <IconButton
        key="cancel"
        icon="ban"
        color={Colors.grey800}
        size={20}
        onPress={cancelEdit}
      />,
    ];
  } else {
    content = [
      <Text style={styles.todoDescription} key="description">
        {todo.description}
      </Text>,
      <IconButton
        key="delete"
        icon="trash"
        color={Colors.red500}
        size={20}
        onPress={archiveTodo}
      />,
    ];
    if (uncommittedEdit) {
      content.push(
        <IconButton
          key="warn"
          icon="exclamation-triangle"
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
    <Card onPress={beginEdit} testID={testId}>
      <Card.Content style={styles.todoItem}>
        <Checkbox.Android
          status={todo.completed ? 'checked' : 'unchecked'}
          onPress={toggleTodo}
        />
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
