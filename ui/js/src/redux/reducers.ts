import { createAsyncThunk } from '@reduxjs/toolkit';
import { ApiState, ReduxState, Todo } from './types';
import createApiReducer from './reducers/createApiReducer';
import getRequestOpts from './getRequestOptions';

const API_NAME = 'todosApi';
const TODOS_API = 'api/todos/todos/';

export const createTodo = createAsyncThunk<
  Todo,
  string,
  {
    state: ReduxState;
  }
>(`${API_NAME}/create`, async (todoTitle: string) => {
  // TODO persist todo - see createApiReducer for example
  const newTodo = {
    id: null,
    created_at: Date.now(),
    description: todoTitle,
  };

  const requestOpts = getRequestOpts('POST');
  requestOpts.body = JSON.stringify(newTodo);
  const response = await fetch(TODOS_API, requestOpts);
  return await response.json();
});

interface CreateTodoAction {
  payload: Todo;
}

const otherExtraReducers = {
  [createTodo.fulfilled.type]: (
    state: ApiState<Todo>,
    action: CreateTodoAction,
  ) => {
    state.entries.push(action.payload);
  },
};

const { fetchThunk: fetchTodos, reducer: todosReducer } = createApiReducer<
  Todo
>(API_NAME, TODOS_API, state => state.todosApi, otherExtraReducers);

export { fetchTodos };
export default {
  todosApi: todosReducer,
};
