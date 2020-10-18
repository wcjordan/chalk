import React, {
  KeyboardEvent,
  MouseEvent,
  useCallback,
  useEffect,
  useRef,
} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faBan,
  faExclamationTriangle,
  faTrash,
} from '@fortawesome/free-solid-svg-icons';
import { faCheckCircle, faCircle } from '@fortawesome/free-regular-svg-icons';
import { Todo, TodoPatch } from '../redux/types';
import './TodoItem.css';

const TodoItem: React.FC<Props> = function (props: Props) {
  const { editing, todo, setTodoEditId, uncommittedEdit, updateTodo } = props;
  const editInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing && editInput.current) {
      editInput.current.select();
    }
  }, [editing]);

  const updateTodoCb = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      updateTodo(
        {
          id: todo.id,
          description: event.currentTarget.value,
        },
        false,
      );
    },
    [updateTodo, todo.id],
  );

  const commitTodo = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter') {
        updateTodo({
          id: todo.id,
          description: event.currentTarget.value,
        });
      }
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
  let itemClasses = 'todo-item';
  if (editing) {
    itemClasses += ' todo-edit';
    content = [
      <input
        className="edit-todo-input"
        defaultValue={uncommittedEdit || todo.description}
        key="input"
        onInput={updateTodoCb}
        onKeyPress={commitTodo}
        ref={editInput}
      />,
      <FontAwesomeIcon
        icon={faBan}
        key="cancel"
        onClick={cancelEdit}
        size="sm"
      />,
    ];
  } else {
    content = [
      <span key="description" className="todo-description">
        {todo.description}
      </span>,
      <FontAwesomeIcon
        icon={faTrash}
        key="archive"
        onClick={archiveTodo}
        size="sm"
      />,
    ];
    if (uncommittedEdit) {
      content.push(
        <FontAwesomeIcon
          icon={faExclamationTriangle}
          key="warn"
          size="xs"
          title={`Uncommitted edit: ${uncommittedEdit}`}
        />,
      );
    }
  }

  const checkboxIcon = todo.completed ? faCheckCircle : faCircle;
  return (
    <div className={itemClasses} onClick={beginEdit}>
      <FontAwesomeIcon
        icon={checkboxIcon}
        key="checkbox"
        onClick={toggleTodo}
        size="sm"
      />
      {content}
    </div>
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
