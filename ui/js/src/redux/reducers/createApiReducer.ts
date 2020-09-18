import _ from 'lodash';
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { ApiState, ReduxState } from '../types';
import getRequestOpts from '../getRequestOptions';

interface SliceGetter<T> {
  (state: ReduxState): ApiState<T>;
}

export default function createApiReducer<
  T extends { id: number },
  U extends { id: number }
>(
  apiName: string,
  apiUri: string,
  getSlice: SliceGetter<T>,
  otherExtraReducers: object,
) {
  const initialState: ApiState<T> = {
    entries: [],
    loading: false,
  };

  const fetchThunk = createAsyncThunk<T[], void, { state: ReduxState }>(
    `${apiName}/fetch`,
    async (_unused, thunkAPI) => {
      const response = await fetch(apiUri, getRequestOpts('GET'));

      if (!response.ok) {
        return thunkAPI.rejectWithValue(
          `${response.status} ${response.statusText}`,
        );
      }
      return await response.json();
    },
    {
      condition: (_unused, { getState }) => {
        return !getSlice(getState()).loading;
      },
    },
  );

  const updateThunk = createAsyncThunk<T, U, { state: ReduxState }>(
    `${apiName}/update`,
    async (entryPatch, thunkAPI) => {
      const requestOpts = getRequestOpts('PATCH');
      requestOpts.body = JSON.stringify(entryPatch);
      const response = await fetch(`${apiUri}${entryPatch.id}/`, requestOpts);

      if (!response.ok) {
        return thunkAPI.rejectWithValue(
          `${response.status} ${response.statusText}`,
        );
      }
      return await response.json();
    },
  );

  const apiSlice = createSlice({
    name: apiName,
    initialState,
    reducers: {},
    extraReducers: {
      ...otherExtraReducers,
      [fetchThunk.pending.type]: state => {
        state.loading = true;
      },
      [fetchThunk.fulfilled.type]: (state, action) => {
        state.loading = false;
        state.entries = action.payload;
      },
      [fetchThunk.rejected.type]: (state, action) => {
        state.loading = false;
        console.log(`Loading ${apiName} failed. ${action.payload}`);
      },
      [updateThunk.fulfilled.type]: (state, action) => {
        const updatedEntry = action.payload;
        const existingEntry = _.find(
          state.entries,
          entry => entry.id === updatedEntry.id,
        );
        Object.assign(existingEntry, updatedEntry);
      },
      [updateThunk.rejected.type]: (_unused, action) => {
        console.log(`Updating ${apiName} failed. ${action.payload}`);
      },
    },
  });

  return {
    actions: apiSlice.actions,
    fetchThunk,
    updateThunk,
    reducer: apiSlice.reducer,
  };
}
