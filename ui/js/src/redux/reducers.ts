import { Todo } from './types';
import createApiReducer from './reducers/createApiReducer';

const { fetchThunk: fetchTodos, reducer: todosReducer } = createApiReducer<
  Todo
>('todosApi', 'api/todos/todos/', state => state.todosApi);

export { fetchTodos };
export default {
  todosApi: todosReducer,
};
