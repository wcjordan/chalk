import React, { KeyboardEvent, useCallback, useEffect, useRef } from 'react';
import { Todo, TodoPatch } from '../redux/types';
import './TodoItem.css';

function TodoItem(props: Props) {
  const { editing, todo, editTodo, updateTodo } = props;
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

        updateTodo({
          id: todo.id,
          description: event.currentTarget.value,
        });
      }
    },
    [updateTodo, todo.id],
  );

  const editTodoCb = useCallback(() => {
    if (editing) {
      return;
    }

    editTodo(todo.id);
  }, [editTodo, todo.id, editing]);

  let checkboxClasses = 'todo-checkbox';
  // if (todo.completed) {
  //   checkboxClasses += ' todo-active';
  // }

  let content;
  let itemClasses = 'todo-item';
  if (editing) {
    itemClasses += ' todo-edit';
    content = (
      <input
        ref={editInput}
        className="edit-todo-input"
        onKeyPress={updateTodoCb}
        defaultValue={todo.description}
      />
    );
  } else {
    content = <span className="todo-description">{todo.description}</span>;
  }

  return (
    <div className={itemClasses} onClick={editTodoCb}>
      <div className={checkboxClasses} />
      {content}
    </div>
  );
}

type Props = {
  editing: boolean;
  todo: Todo;
  updateTodo: (patch: TodoPatch) => void;
  editTodo: (id: number) => void;
};

export default TodoItem;
