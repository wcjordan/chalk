import { createSlice } from '@reduxjs/toolkit';
import { AppThunk, TodoPatch, WorkspaceState } from './types';
import todosApiSlice, {
  createTodo,
  listTodos,
  updateTodo as updateTodoApi,
} from './todosApiSlice';

const initialWorkspace: WorkspaceState = {
  editId: null,
  uncommittedEdits: {},
};
const workspaceSlice = createSlice({
  name: 'workspace',
  initialState: initialWorkspace,
  reducers: {
    setTodoEditId: (state, action) => {
      const editId = action.payload;
      if (editId === null && state.editId !== null) {
        // If cancelling an edit, clear the uncommitted value.
        delete state.uncommittedEdits[state.editId];
      }
      state.editId = editId;
    },
    updateTodoUncommitted: (state, action) => {
      const { id, description } = action.payload;
      state.uncommittedEdits[id] = description;
    },
  },
});

export const updateTodo = (
  todoPatch: TodoPatch,
  commitEdit: boolean = true,
): AppThunk => dispatch => {
  if (!commitEdit) {
    dispatch(workspaceSlice.actions.updateTodoUncommitted(todoPatch));
    return;
  }

  dispatch(workspaceSlice.actions.setTodoEditId(null));
  dispatch(updateTodoApi(todoPatch));
};

export const setTodoEditId = workspaceSlice.actions.setTodoEditId;
export { createTodo, listTodos };
export default {
  todosApi: todosApiSlice.reducer,
  workspace: workspaceSlice.reducer,
};
