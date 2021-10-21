import { ThunkAction } from 'redux-thunk';
import { Action, createSlice } from '@reduxjs/toolkit';
import { ReduxState, TodoPatch, WorkspaceState } from './types';
import labelsApiSlice, { listLabels } from './labelsApiSlice';
import todosApiSlice, {
  createTodo,
  listTodos,
  updateTodo as updateTodoApi,
} from './todosApiSlice';

type AppThunk = ThunkAction<void, ReduxState, unknown, Action<string>>;

const initialWorkspace: WorkspaceState = {
  editId: null,
  labelTodoId: null,
};
const workspaceSlice = createSlice({
  name: 'workspace',
  initialState: initialWorkspace,
  reducers: {
    setTodoLabelingId: (state, action) => {
      state.labelTodoId = action.payload;
    },
    setTodoEditId: (state, action) => {
      state.editId = action.payload;
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

export const updateTodoLabels =
  (label_set: string[]): AppThunk =>
  (dispatch, getState) => {
    const todoId = getState().workspace.labelTodoId;
    if (todoId === null) {
      throw new Error('Unable to edit a todo w/ null ID');
    }

    return dispatch(
      updateTodoApi({
        id: todoId,
        label_set,
      }),
    );
  };

export const setTodoEditId = workspaceSlice.actions.setTodoEditId;
export const setTodoLabelingId = workspaceSlice.actions.setTodoLabelingId;
export { createTodo, listLabels, listTodos };
export default {
  labelsApi: labelsApiSlice.reducer,
  todosApi: todosApiSlice.reducer,
  workspace: workspaceSlice.reducer,
};
