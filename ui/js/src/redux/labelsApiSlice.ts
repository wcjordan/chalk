import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { ApiState, ReduxState, Label } from './types';
import { getWsRoot, list } from './fetchApi';

const API_NAME = 'labelsApi';

// Exported for testing
export function getLabelsApi(): string {
  return `${getWsRoot()}api/todos/labels/`;
}

const initialState: ApiState<Label> = {
  entries: [],
  initialLoad: true,
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
  extraReducers: (builder) => {
    builder
      .addCase(listLabels.pending, (state) => {
        state.loading = true;
      })
      .addCase(listLabels.fulfilled, (state, action) => {
        state.initialLoad = false;
        state.loading = false;
        state.entries = action.payload;
      })
      .addCase(listLabels.rejected, (state, action) => {
        state.initialLoad = false;
        state.loading = false;
        console.warn(`Loading Labels failed. ${action.error.message}`);
      });
  },
});
