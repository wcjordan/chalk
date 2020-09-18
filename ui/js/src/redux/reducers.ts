import { createSlice } from '@reduxjs/toolkit';
import { AppThunk, WorkspaceState } from './types';
import todosApiSlice, {
  createTodo,
  listTodos,
  updateTodo as updateTodoApi,
} from './todosApiSlice';

const initialWorkspace: WorkspaceState = {
  editId: null,
};
const workspaceSlice = createSlice({
  name: 'workspace',
  initialState: initialWorkspace,
  reducers: {
    setTodoEditId: (state, action) => {
      state.editId = action.payload;
      return state;
    },
  },
});

export const updateTodo = (
  id: number,
  description: string,
): AppThunk => dispatch => {
  dispatch(workspaceSlice.actions.setTodoEditId(null));
  dispatch(updateTodoApi({ id, description }));
};

export const setTodoEditId = workspaceSlice.actions.setTodoEditId;
export { createTodo, listTodos };
export default {
  todosApi: todosApiSlice.reducer,
  workspace: workspaceSlice.reducer,
};
