import React, { useCallback } from 'react';
import {
  GestureResponderEvent,
  NativeSyntheticEvent,
  StyleProp,
  StyleSheet,
  Text,
  TextInput,
  TextInputSubmitEditingEventData,
  TextStyle,
  TouchableHighlight,
} from 'react-native';
import {
  FontAwesomeIcon,
  FontAwesomeIconStyle,
} from '@fortawesome/react-native-fontawesome';
import {
  faBan,
  faExclamationTriangle,
  faTrash,
} from '@fortawesome/free-solid-svg-icons';
import { faCheckCircle, faCircle } from '@fortawesome/free-regular-svg-icons';
import { Todo, TodoPatch } from '../redux/types';

interface Style {
  todoItem: TextStyle;
  todoEdit: TextStyle;
  todoDescription: TextStyle;
  editTodoInput: TextStyle;
  iconMargin: FontAwesomeIconStyle;
  iconCheck: FontAwesomeIconStyle;
  iconCancel: FontAwesomeIconStyle;
  iconDelete: FontAwesomeIconStyle;
  iconWarn: FontAwesomeIconStyle;
}

const styles = StyleSheet.create<Style>({
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
    // cursor: 'pointer',
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
    backgroundColor: 'transparent',
    borderWidth: 0,
    // color: 'inherit',
    flexGrow: 1,
    // fontFamily: 'inherit',
    // fontSize: 'inherit',
    // lineHeight: 'inherit',
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
    (event: GestureResponderEvent) => {
      event.stopPropagation();
      updateTodo({
        id: todo.id,
        completed: !todo.completed,
      });
    },
    [updateTodo, todo.id, todo.completed],
  );

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
  let itemStyle: StyleProp<TextStyle> = styles.todoItem;
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
      <TouchableHighlight key="cancel" onPress={cancelEdit}>
        <FontAwesomeIcon
          icon={faBan}
          style={[styles.iconMargin, styles.iconCancel]}
          size={16}
        />
      </TouchableHighlight>,
    ];
  } else {
    content = [
      <Text style={styles.todoDescription} key="description">
        {todo.description}
      </Text>,
      <TouchableHighlight key="archive" onPress={archiveTodo}>
        <FontAwesomeIcon
          icon={faTrash}
          style={[styles.iconMargin, styles.iconDelete]}
          size={16}
        />
      </TouchableHighlight>,
    ];
    if (uncommittedEdit) {
      content.push(
        <FontAwesomeIcon
          icon={faExclamationTriangle}
          key="warn"
          style={[styles.iconMargin, styles.iconWarn]}
          size={16}
          // title={`Uncommitted edit: ${uncommittedEdit}`}
        />,
      );
    }
  }

  const checkboxIcon = todo.completed ? faCheckCircle : faCircle;
  const testId = `todo-${todo.completed ? 'checked' : 'unchecked'}-${todo.id}`;
  return (
    <Text style={itemStyle} onPress={beginEdit} nativeID={testId}>
      <TouchableHighlight key="checkbox" onPress={toggleTodo}>
        <FontAwesomeIcon
          icon={checkboxIcon}
          style={[styles.iconMargin, styles.iconCheck]}
          size={16}
        />
      </TouchableHighlight>
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
