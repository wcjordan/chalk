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
  IconButton,
  Text,
  TextInput,
} from 'react-native-paper';
import { setEditTodoId, setLabelTodoId, updateTodo } from '../redux/reducers';
import { Todo } from '../redux/types';
import { useAppDispatch } from '../hooks';
import LabelChip from './LabelChip';

interface Style {
  activeCard: ViewStyle & { cursor?: string };
  card: ViewStyle & { cursor?: string };
  cardContent: ViewStyle;
  cardPadding: ViewStyle;
  editTodoInput: TextStyle;
  iconButton: ViewStyle;
  spacer: ViewStyle;
  todoDescription: TextStyle;
  todoDescriptionText: TextStyle;
  todoLabelsContent: ViewStyle;
}

const cardStyle: ViewStyle & { cursor?: string } = {
  borderRadius: 0,
  borderColor: '#0000001f',
};
if (Platform.OS === 'web') {
  cardStyle['cursor'] = 'pointer';
}
const activeCardStyle = Object.assign({}, cardStyle, {
  borderColor: '#a3d5ffff',
  borderLeftWidth: 12,
});

const styles = StyleSheet.create<Style>({
  activeCard: activeCardStyle,
  card: cardStyle,
  cardContent: {
    flexDirection: 'row',
    width: '100%',
  },
  cardPadding: {
    paddingBottom: 8,
    paddingLeft: 8,
    paddingRight: 8,
    paddingTop: 8,
  },
  editTodoInput: {
    borderWidth: 0,
    flexShrink: 1,
    marginLeft: 9,
    padding: 0,
    width: '100%',
  },
  iconButton: {
    margin: 0,
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
    fontFamily: 'sans-serif',
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
    isDragging,
    labeling,
    startDrag,
    todo,
  } = props;
  const dispatch = useAppDispatch();
  const [editingValue, setEditingValue] = useState<string | null>(null);

  const commitTodo = useCallback(() => {
    if (!editingValue) {
      return;
    }

    dispatch(updateTodo({
      id: todo.id,
      description: editingValue,
    }));
    setEditingValue(null);
  }, [todo.id, editingValue]);

  const toggleTodo = useCallback(() => {
    dispatch(updateTodo({
      id: todo.id,
      completed: !todo.completed,
    }));
  }, [todo.id, todo.completed]);

  const archiveTodo = useCallback(
    (event: GestureResponderEvent) => {
      event.stopPropagation();
      dispatch(updateTodo({
        id: todo.id,
        archived: true,
      }));
    },
    [todo.id],
  );

  const labelTodo = useCallback(
    (event: GestureResponderEvent) => {
      event.stopPropagation();
      dispatch(setLabelTodoId(todo.id));
    },
    [todo.id],
  );

  const beginEdit = useCallback(() => {
    if (editing) {
      return;
    }

    dispatch(setEditTodoId(todo.id));
  }, [todo.id, editing]);

  const cancelEdit = useCallback(() => {
    if (!editing) {
      return;
    }

    setEditingValue(null);
    dispatch(setEditTodoId(null));
  }, [editing]);

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
        iconColor="#424242"
        size={20}
        style={styles.iconButton}
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
        iconColor="#a3d5ffff"
        icon="tag-plus"
        key="label"
        onPress={labelTodo}
        size={20}
        style={styles.iconButton}
        testID="label-todo"
      />,
      <IconButton
        iconColor="#f44336"
        icon="delete-outline"
        key="delete"
        onPress={archiveTodo}
        size={20}
        style={styles.iconButton}
        testID="delete-todo"
      />,
    ];
    if (editingValue !== null) {
      content.push(
        // TODO figure out showing accessibility label on hover & long press
        <IconButton
          accessibilityLabel={`Uncommitted edit: ${editingValue}`}
          iconColor="#ffb74d"
          icon="alert-outline"
          key="warn"
          style={styles.iconButton}
          size={20}
        />,
      );
    }
  }

  let labelContent = null;
  if (todo.labels.length) {
    const chips = todo.labels.map((label) => (
      <LabelChip key={label} label={label} slimStyle={true} />
    ));
    labelContent = (
      <View style={styles.todoLabelsContent} testID="todo-labels">
        {chips}
      </View>
    );
  }

  return (
    <Card
      disabled={isDragging}
      mode="outlined"
      onLongPress={startDrag}
      onPress={beginEdit}
      style={labeling ? styles.activeCard : styles.card}
    >
      <Card.Content style={styles.cardPadding}>
        <View style={styles.cardContent}>
          <View>
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
  isDragging: boolean;
  labeling: boolean;
  startDrag: () => void;
  todo: Todo;
};

export default TodoItem;
