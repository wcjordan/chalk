import React, { KeyboardEvent, useCallback, useEffect, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBan } from '@fortawesome/free-solid-svg-icons';
import { Todo } from '../redux/types';
import './TodoItem.css';

function TodoItem(props: Props) {
  const { editing, todo, setTodoEditId, updateTodo } = props;
  const editInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing && editInput.current) {
      editInput.current.select();
    }
  }, [editing]);

  const updateTodoCb = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter') {
        event.preventDefault();

        updateTodo(todo.id, event.currentTarget.value);
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
        key="input"
        ref={editInput}
        className="edit-todo-input"
        onKeyPress={updateTodoCb}
        defaultValue={todo.description}
      />,
      <FontAwesomeIcon
        key="cancel"
        icon={faBan}
        size="lg"
        onClick={cancelEdit}
      />,
    ];
  } else {
    content = <span className="todo-description">{todo.description}</span>;
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
  updateTodo: (id: number, description: string) => void;
  setTodoEditId: (id: number | null) => void;
};

export default TodoItem;
