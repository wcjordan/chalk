import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { ApiState, ReduxState, Label } from './types';
import { getWsRoot, list } from './fetchApi';

const API_NAME = 'labelsApi';

// Exported for testing
export function getLabelsApi(): string {
  return `${getWsRoot()}api/todos/labels/`;
}

interface ErrorAction {
  error: Error;
}

interface LabelListAction {
  payload: Array<Label>;
}

const initialState: ApiState<Label> = {
  entries: [],
  loading: false,
};

export const listLabels = createAsyncThunk<
  Label[],
  void,
  { state: ReduxState }
>(`${API_NAME}/list`, async () => list<Label>(getLabelsApi()), {
  condition: (_unused, { getState }) => {
    return !getState().labelsApi.loading;
  },
});

export default createSlice({
  name: API_NAME,
  initialState,
  reducers: {},
  extraReducers: {
    [listLabels.pending.type]: (state) => {
      state.loading = true;
    },
    [listLabels.fulfilled.type]: (state, action: LabelListAction) => {
      state.loading = false;
      state.entries = action.payload;
    },
    [listLabels.rejected.type]: (state, action: ErrorAction) => {
      state.loading = false;
      console.warn(`Loading Labels failed. ${action.error.message}`);
    },
  },
});
