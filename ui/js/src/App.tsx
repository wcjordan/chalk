import _ from 'lodash';
import { connect, ConnectedProps } from 'react-redux';
import React from 'react';
import AddTodo from './components/AddTodo';
import { ReduxState } from './redux/types';
import TodoItem from './components/TodoItem';
import { createTodo } from './redux/reducers';
import './App.css';

export function App(props: ConnectedProps<typeof connector>) {
  const { todos } = props;
  const todoViews = _.map(todos, todo => (
    <TodoItem key={todo.id || ''} todo={todo} />
  ));
  return (
    <div className="App">
      <AddTodo addTodo={props.createTodo} />
      {todoViews}
    </div>
  );
}

const mapStateToProps = (state: ReduxState) => {
  return {
    todos: state.todosApi.entries,
  };
};
const mapDispatchToProps = { createTodo };
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
