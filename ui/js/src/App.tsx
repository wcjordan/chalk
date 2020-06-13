import _ from 'lodash';
import React from 'react';
import { connect } from 'react-redux';
import { Todo, ReduxState } from './redux/types';
import './App.css';

export function App(props: Props) {
  const { todos } = props;
  const todoViews = _.map(todos, todo => (
    <div>{todo.description}</div>
  ));
  return (
    <div className="App">
      {todoViews}
    </div>
  );
}

type Props = {
  todos: Todo[];
};

const mapStateToProps = (state: ReduxState) => {
  return {
    todos: state.todosApi.entries,
  };
};
const mapDispatchToProps = { };
export default connect(mapStateToProps, mapDispatchToProps)(App);
