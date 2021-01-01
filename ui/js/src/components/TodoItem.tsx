import React, { MouseEvent, useCallback } from 'react';
import {
  NativeSyntheticEvent,
  StyleProp,
  StyleSheet,
  Text,
  TextInput,
  TextInputSubmitEditingEventData,
  View,
  ViewStyle,
} from 'react-native';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import {
  faBan,
  faExclamationTriangle,
  faTrash,
} from '@fortawesome/free-solid-svg-icons';
import { faCheckCircle, faCircle } from '@fortawesome/free-regular-svg-icons';
import { Todo, TodoPatch } from '../redux/types';

const styles = StyleSheet.create({
  todoItem: {
    backgroundColor: '#3d5a80',
    color: '#e0fbfc',
    display: 'flex',
    fontFamily: 'monospace',
    padding: 8,
    fontSize: 20,
    width: '100%',
    borderTopWidth: 1,
    borderTopColor: '#e0fbfc',
    cursor: 'pointer',
  },
  todoEdit: {
    backgroundColor: '#98c1d9',
    color: '#e0fbfc',
  },
  todoDescription: {
    marginLeft: 9,
    flexGrow: 1,
  },
  editTodoInput: {
    backgroundColor: 'inherit',
    border: 'none',
    color: 'inherit',
    flexGrow: 1,
    fontFamily: 'inherit',
    fontSize: 'inherit',
    lineHeight: 'inherit',
    marginLeft: 9,
    padding: 0,
  },
  iconMargin: {
    marginVertical: 'auto',
  },
  iconCheck: {
    color: '#e0fbfc',
  },
  iconCancel: {
    color: '#3d5a80',
  },
  iconDelete: {
    color: 'red',
    paddingRight: 1,
    // visibility: 'hidden',
  },
  iconWarn: {
    color: '#f7b6a6',
    paddingLeft: 5,
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

  const toggleTodo = useCallback(
    (event: MouseEvent) => {
      event.stopPropagation();
      updateTodo({
        id: todo.id,
        completed: !todo.completed,
      });
    },
    [updateTodo, todo.id, todo.completed],
  );

  const archiveTodo = useCallback(
    (event: MouseEvent) => {
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
  let itemStyle: StyleProp<ViewStyle> = styles.todoItem;
  if (editing) {
    itemStyle = StyleSheet.compose(itemStyle, styles.todoEdit);
    content = [
      // TODO remove input outline on focus
      <TextInput
        defaultValue={uncommittedEdit || todo.description}
        key="input"
        style={styles.editTodoInput}
        selectionColor="#3d5a80"
        onChangeText={updateTodoCb}
        onSubmitEditing={commitTodo}
        selectTextOnFocus={true}
      />,
      <FontAwesomeIcon
        icon={faBan}
        key="cancel"
        style={StyleSheet.compose(styles.iconMargin, styles.iconCancel)}
        onClick={cancelEdit}
        size={16}
      />,
    ];
  } else {
    content = [
      <Text style={styles.todoDescription} key="description">
        {todo.description}
      </Text>,
      <FontAwesomeIcon
        icon={faTrash}
        key="archive"
        style={StyleSheet.compose(styles.iconMargin, styles.iconDelete)}
        onClick={archiveTodo}
        size={16}
      />,
    ];
    if (uncommittedEdit) {
      content.push(
        <FontAwesomeIcon
          icon={faExclamationTriangle}
          key="warn"
          style={StyleSheet.compose(styles.iconMargin, styles.iconWarn)}
          size={16}
          title={`Uncommitted edit: ${uncommittedEdit}`}
        />,
      );
    }
  }

  const checkboxIcon = todo.completed ? faCheckCircle : faCircle;
  return (
    <Text style={itemStyle} onPress={beginEdit}>
      <FontAwesomeIcon
        icon={checkboxIcon}
        key="checkbox"
        style={StyleSheet.compose(styles.iconMargin, styles.iconCheck)}
        onClick={toggleTodo}
        size={16}
      />
      {content}
    </Text>
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
