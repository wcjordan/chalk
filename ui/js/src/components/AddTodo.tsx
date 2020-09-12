import React, { Component, KeyboardEvent } from 'react';
import './AddTodo.css';

type Props = {
  addTodo: Function;
};

class AddTodo extends Component<Props> {
  render() {
    return (
      <div className="add-todo">
        <div className="add-todo-icon" />
        <input
          className="add-todo-input"
          placeholder="Add a new todo..."
          onKeyPress={this.addTodo}
        />
      </div>
    );
  }

  addTodo = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.props.addTodo(event.currentTarget.value);
    }
  };
}

export default AddTodo;
