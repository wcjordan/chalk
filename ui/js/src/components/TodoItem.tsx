import React, { KeyboardEvent, useCallback, useEffect, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faBan,
  faExclamationTriangle,
} from '@fortawesome/free-solid-svg-icons';
import { Todo } from '../redux/types';
import './TodoItem.css';

function TodoItem(props: Props) {
  const { editing, todo, setTodoEditId, uncommittedEdit, updateTodo } = props;
  const editInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing && editInput.current) {
      editInput.current.select();
    }
  }, [editing]);

  const updateTodoCb = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      updateTodo(todo.id, event.currentTarget.value, false);
    },
    [updateTodo, todo.id],
  );

  const commitTodo = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        updateTodo(todo.id, event.currentTarget.value, true);
      }
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

  let checkboxClasses = 'todo-checkbox';
  // if (todo.completed) {
  //   checkboxClasses += ' todo-active';
  // }

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
    ];
    if (uncommittedEdit) {
      content.push(
        <FontAwesomeIcon key="warn" icon={faExclamationTriangle} size="xs" />,
      );
    }
  }

  return (
    <div className={itemClasses} onClick={beginEdit}>
      <div className={checkboxClasses} />
      {content}
    </div>
  );
}

type Props = {
  editing: boolean;
  todo: Todo;
  updateTodo: (id: number, description: string, commitEdit: boolean) => void;
  setTodoEditId: (id: number | null) => void;
  uncommittedEdit: string | undefined;
};

export default TodoItem;
