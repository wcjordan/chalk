import { ThunkAction } from 'redux-thunk';
import { Action, createSlice } from '@reduxjs/toolkit';
import { ReduxState, TodoPatch, WorkspaceState } from './types';
import todosApiSlice, {
  createTodo,
  listTodos,
  updateTodo as updateTodoApi,
} from './todosApiSlice';

type AppThunk = ThunkAction<void, ReduxState, unknown, Action<string>>;

const initialWorkspace: WorkspaceState = {
  editId: null,
};
const workspaceSlice = createSlice({
  name: 'workspace',
  initialState: initialWorkspace,
  reducers: {
    setTodoEditId: (state, action) => {
      const editId = action.payload;
      state.editId = editId;
    },
  },
});

export const updateTodo =
  (todoPatch: TodoPatch): AppThunk =>
  (dispatch) => {
    return Promise.all([
      dispatch(workspaceSlice.actions.setTodoEditId(null)),
      dispatch(updateTodoApi(todoPatch)),
    ]);
  };

export const setTodoEditId = workspaceSlice.actions.setTodoEditId;
export { createTodo, listTodos };
export default {
  todosApi: todosApiSlice.reducer,
  workspace: workspaceSlice.reducer,
};
