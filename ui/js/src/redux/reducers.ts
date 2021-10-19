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

const DEFAULT_SELECTED_LABELS = {
  '5 minutes': true,
  work: true,
  home: true,
  'low-energy': true,
  mobile: true,
};

const initialWorkspace: WorkspaceState = {
  editId: null,
  labelTodoId: null,
  selectedLabels: DEFAULT_SELECTED_LABELS, //{},
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

export const setTodoEditId = workspaceSlice.actions.setTodoEditId;
export const setTodoLabelingId = workspaceSlice.actions.setTodoLabelingId;
export { createTodo, listLabels, listTodos };
export default {
  labelsApi: labelsApiSlice.reducer,
  todosApi: todosApiSlice.reducer,
  workspace: workspaceSlice.reducer,
};
