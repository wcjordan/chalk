import _ from 'lodash';
import { connect, ConnectedProps } from 'react-redux';
import React from 'react';
import AddTodo from './components/AddTodo';
import { ReduxState } from './redux/types';
import TodoItem from './components/TodoItem';
import { createTodo, updateTodo, setTodoEditId } from './redux/reducers';
import './App.css';

export function App(props: ConnectedProps<typeof connector>) {
  const { createTodo, editId, setTodoEditId, todos, updateTodo } = props;
  const todoViews = _.map(todos, todo => (
    <TodoItem
      key={todo.id || ''}
      editing={todo.id === editId}
      todo={todo}
      updateTodo={updateTodo}
      setTodoEditId={setTodoEditId}
    />
  ));

  return (
    <div className="App">
      <AddTodo createTodo={createTodo} />
      {todoViews}
    </div>
  );
}

const mapStateToProps = (state: ReduxState) => {
  return {
    todos: state.todosApi.entries,
    editId: state.workspace.editId,
  };
};
const mapDispatchToProps = { createTodo, setTodoEditId, updateTodo };
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
