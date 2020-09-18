import React, { KeyboardEvent, useCallback } from 'react';
import './AddTodo.css';

function AddTodo(props: Props) {
  const { createTodo } = props;
  const addTodo = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter') {
        event.preventDefault();

        createTodo(event.currentTarget.value);
      }
    },
    [createTodo],
  );

  return (
    <div className="add-todo">
      <div className="add-todo-icon" />
      <input
        className="add-todo-input"
        placeholder="Add a new todo..."
        onKeyPress={addTodo}
      />
    </div>
  );
}

type Props = {
  createTodo: (description: string) => void;
};

export default AddTodo;
