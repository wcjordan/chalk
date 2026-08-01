import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { CreateTodoOperation, ShortcutState } from './types';

// Store operations for optimistic updates
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
    addCreateTodoOperation: (state, action) => {
      state.operations.push({
        type: 'CREATE_TODO',
        payload: action.payload,
        generation: state.latestGeneration,
      });
    },
    // Removes a CREATE_TODO placeholder as soon as its real create call
    // resolves, rather than waiting for the next listTodos poll cycle to
    // clear it by generation — otherwise the placeholder and the newly
    // created (real) todo are both visible for up to 10s.
    removeCreateTodoOperation: (state, action: PayloadAction<number>) => {
      state.operations = state.operations.filter(
        (op) =>
          !(
            op.type === 'CREATE_TODO' &&
            (op.payload as CreateTodoOperation).tempId === action.payload
          ),
      );
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
