import React, { useCallback, useState } from 'react';
import {
  GestureResponderEvent,
  Platform,
  StyleSheet,
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
    flexShrink: 1,
    marginLeft: 9,
    padding: 0,
    width: '100%',
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
  const { editing, todo, setTodoEditId, updateTodo } = props;
  const [textValue, setTextValue] = useState(todo.description);

  const commitTodo = useCallback(() => {
    updateTodo({
      id: todo.id,
      description: textValue,
    });
  }, [updateTodo, todo.id, textValue]);

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

    setTextValue(todo.description);
    setTodoEditId(null);
  }, [setTodoEditId, editing]);

  let content;
  if (editing) {
    content = [
      <TextInput
        blurOnSubmit={true}
        dense={true}
        key="input"
        multiline={true}
        numberOfLines={4}
        onChangeText={setTextValue}
        onSubmitEditing={commitTodo}
        selectTextOnFocus={true}
        style={styles.editTodoInput}
        value={textValue}
      />,
      <IconButton
        key="cancel"
        icon="cancel"
        color={Colors.grey800}
        size={20}
        onPress={cancelEdit}
        testID="cancel-edit"
      />,
    ];
  } else {
    content = [
      <View key="description" style={styles.todoDescription}>
        <View style={styles.spacer} />
        <Text
          key="descriptionText"
          testID="description-text"
          style={styles.todoDescriptionText}
        >
          {todo.description}
        </Text>
        <View style={styles.spacer} />
      </View>,
      <IconButton
        color={Colors.red500}
        icon="trash-can-outline"
        key="delete"
        onPress={archiveTodo}
        size={20}
        testID="delete-todo"
      />,
    ];
    if (textValue !== todo.description) {
      content.push(
        <IconButton
          color={Colors.orange300}
          icon="alert-outline"
          key="warn"
          size={20}
        />,
        // title={`Uncommitted edit: ${textValue}`}
        // TODO w/ onLongPress
      );
    }
  }

  return (
    <Card onPress={beginEdit} style={styles.todoItemCard}>
      <Card.Content style={styles.todoItemContent}>
        <View style={styles.checkbox}>
          <Checkbox.Android
            status={todo.completed ? 'checked' : 'unchecked'}
            onPress={toggleTodo}
            testID="complete-todo"
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
};

export default TodoItem;
