import '../__mocks__/matchMediaMock';
import shortcutSlice from './shortcutSlice';

describe('shortcut reducer', function () {
  it('should return the initial state', function () {
    expect(shortcutSlice.reducer(undefined, {})).toEqual({
      latestGeneration: 0,
      operations: [],
    });
  });

  describe('shortcuts/removeCreateTodoOperation', function () {
    it('should remove the CREATE_TODO op matching the given tempId', function () {
      const result = shortcutSlice.reducer(
        {
          operations: [
            {
              type: 'CREATE_TODO',
              payload: { tempId: -1, description: 'a', labels: [] },
              generation: 0,
            },
            {
              type: 'CREATE_TODO',
              payload: { tempId: -2, description: 'b', labels: [] },
              generation: 0,
            },
          ],
        },
        {
          type: 'shortcuts/removeCreateTodoOperation',
          payload: -1,
        },
      );
      expect(result).toEqual({
        operations: [
          {
            type: 'CREATE_TODO',
            payload: { tempId: -2, description: 'b', labels: [] },
            generation: 0,
          },
        ],
      });
    });

    it('should leave non-CREATE_TODO ops untouched', function () {
      const editOp = {
        type: 'EDIT_TODO',
        payload: { id: 1, description: 'edited' },
        generation: 0,
      };
      const result = shortcutSlice.reducer(
        { operations: [editOp] },
        {
          type: 'shortcuts/removeCreateTodoOperation',
          payload: -1,
        },
      );
      expect(result).toEqual({ operations: [editOp] });
    });
  });

  describe('shortcuts/clearOperationsUpThroughGeneration', function () {
    it('should toggle a new label to active', function () {
      const result = shortcutSlice.reducer(
        {
          operations: [
            {
              generation: 0,
            },
            {
              generation: 1,
            },
            {
              generation: 2,
            },
          ],
        },
        {
          type: 'shortcuts/clearOperationsUpThroughGeneration',
          payload: 1,
        },
      );
      expect(result).toEqual({
        operations: [
          {
            generation: 2,
          },
        ],
      });
    });
  });
});

export {};
