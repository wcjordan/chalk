import { createSlice } from '@reduxjs/toolkit';

import { ShortcutState } from './types';

const initialState: ShortcutState = {
  operations: [],
  latestGeneration: 0,
};
export default createSlice({
  name: 'shortcuts',
  initialState,
  reducers: {
    addEditTodoOperation: (state, action) => {
      state.operations.push({
        type: 'EDIT_TODO',
        payload: action.payload,
        generation: state.latestGeneration,
      });
    },
    addMoveTodoOperation: (state, action) => {
      state.operations.push({
        type: 'MOVE_TODO',
        payload: action.payload,
        generation: state.latestGeneration,
      });
    },
    incrementGenerations: (state) => {
      state.latestGeneration = state.latestGeneration + 1;
    },
    clearOperationsUpThroughGeneration: (state, action) => {
      state.operations = state.operations.filter(
        (op) => op.generation > action.payload,
      );
    },
  },
});
