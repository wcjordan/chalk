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
    return dispatch(workspaceSlice.actions.updateTodoUncommitted(todoPatch));
  }

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
