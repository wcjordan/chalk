import React from 'react';
import './TodoItem.css';

function TodoItem(props: Props) {
  let checkboxClasses = 'todo-checkbox';
  // if (props.todo.completed) {
  //   checkboxClasses += ' todo-active';
  // }

  return (
    <div className="todo-item">
      <div className={checkboxClasses} />
      <span className="todo-input">{props.todo.description}</span>
    </div>
  );
}

type Props = {
  todo: {
    description: string;
  };
};

export default TodoItem;
