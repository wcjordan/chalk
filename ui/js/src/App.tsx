import _ from 'lodash';
import { connect, ConnectedProps } from 'react-redux';
import React from 'react';
import AddTodo from './components/AddTodo';
import { ReduxState } from './redux/types';
import TodoItem from './components/TodoItem';
import { createTodo, updateTodo, setTodoEditId } from './redux/reducers';
import './App.css';

export function App(props: ConnectedProps<typeof connector>) {
  const { createTodo, setTodoEditId, todos, updateTodo, workspace } = props;
  const { editId, uncommittedEdits } = workspace;
  const todoViews = _.map(
    _.filter(todos, todo => !todo.archived),
    todo => (
      <TodoItem
        editing={todo.id === editId}
        key={todo.id || ''}
        setTodoEditId={setTodoEditId}
        todo={todo}
        uncommittedEdit={uncommittedEdits[todo.id]}
        updateTodo={updateTodo}
      />
    ),
  );

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
    workspace: state.workspace,
  };
};
const mapDispatchToProps = { createTodo, setTodoEditId, updateTodo };
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
