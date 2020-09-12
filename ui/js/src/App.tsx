import _ from 'lodash';
import { connect } from 'react-redux';
import React from 'react';
import AddTodo from './components/AddTodo';
import { Todo, ReduxState } from './redux/types';
import TodoItem from './components/TodoItem';
import { createTodo } from './redux/reducers';
import './App.css';

export function App(props: Props) {
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

type Props = {
  createTodo: Function;
  todos: Todo[];
};

const mapStateToProps = (state: ReduxState) => {
  return {
    todos: state.todosApi.entries,
  };
};
const mapDispatchToProps = { createTodo };
export default connect(mapStateToProps, mapDispatchToProps)(App);
