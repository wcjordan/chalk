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
import LabelChip from './LabelChip';

interface Style {
  activeCard: ViewStyle & { cursor?: string };
  card: ViewStyle & { cursor?: string };
  cardContent: ViewStyle;
  checkbox: ViewStyle;
  editTodoInput: TextStyle;
  spacer: ViewStyle;
  todoDescription: TextStyle;
  todoDescriptionText: TextStyle;
  todoLabelsContent: ViewStyle;
}

const cardStyle: ViewStyle & { cursor?: string } = {
  borderRadius: 0,
};
if (Platform.OS === 'web') {
  cardStyle['cursor'] = 'pointer';
}
const activeCardStyle = Object.assign(
  {
    borderColor: '#a3d5ffff',
    borderLeftWidth: 12,
  },
  cardStyle,
);

const styles = StyleSheet.create<Style>({
  activeCard: activeCardStyle,
  card: cardStyle,
  cardContent: {
    flexDirection: 'row',
    width: '100%',
  },
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
  todoLabelsContent: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
});

const TodoItem: React.FC<Props> = function (props: Props) {
  const {
    editing,
    labeling,
    todo,
    setTodoEditId,
    setTodoLabelingId,
    updateTodo,
  } = props;
  const [editingValue, setEditingValue] = useState<string | null>(null);

  const commitTodo = useCallback(() => {
    if (!editingValue) {
      return;
    }

    updateTodo({
      id: todo.id,
      description: editingValue,
    });
    setEditingValue(null);
  }, [updateTodo, todo.id, editingValue]);

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

  const labelTodo = useCallback(
    (event: GestureResponderEvent) => {
      event.stopPropagation();
      setTodoLabelingId(todo.id);
    },
    [setTodoLabelingId, todo.id],
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

    setEditingValue(null);
    setTodoEditId(null);
  }, [setTodoEditId, editing]);

  let content;
  if (editing) {
    const textValue = editingValue == null ? todo.description : editingValue;
    content = [
      <TextInput
        blurOnSubmit={true}
        dense={true}
        key="input"
        multiline={true}
        numberOfLines={4}
        onChangeText={setEditingValue}
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
        color="#a3d5ffff"
        icon="tag-plus"
        key="label"
        onPress={labelTodo}
        size={20}
        testID="label-todo"
      />,
      <IconButton
        color={Colors.red500}
        icon="delete-outline"
        key="delete"
        onPress={archiveTodo}
        size={20}
        testID="delete-todo"
      />,
    ];
    if (editingValue !== null) {
      content.push(
        <IconButton
          color={Colors.orange300}
          icon="alert-outline"
          key="warn"
          size={20}
        />,
        // title={`Uncommitted edit: ${editingValue}`}
        // TODO w/ onLongPress
      );
    }
  }

  let labelContent = null;
  if (todo.labels.length) {
    const chips = todo.labels.map((label) => (
      <LabelChip key={label} label={label} selected={false} />
    ));
    labelContent = (
      <View style={styles.todoLabelsContent} testID="todo-labels">
        {chips}
      </View>
    );
  }

  return (
    <Card
      onPress={beginEdit}
      style={labeling ? styles.activeCard : styles.card}
      mode="outlined"
    >
      <Card.Content>
        <View style={styles.cardContent}>
          <View style={styles.checkbox}>
            <Checkbox.Android
              status={todo.completed ? 'checked' : 'unchecked'}
              onPress={toggleTodo}
              testID="complete-todo"
            />
          </View>
          {content}
        </View>
        {labelContent}
      </Card.Content>
    </Card>
  );
};

type Props = {
  editing: boolean;
  labeling: boolean;
  setTodoEditId: (id: number | null) => void;
  setTodoLabelingId: (id: number | null) => void;
  todo: Todo;
  updateTodo: (todoPatch: TodoPatch, commitEdit?: boolean) => void;
};

export default TodoItem;
