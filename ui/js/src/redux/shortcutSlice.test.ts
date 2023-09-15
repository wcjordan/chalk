import '../__mocks__/matchMediaMock';
import shortcutSlice from './shortcutSlice';

describe('shortcut reducer', function () {
  it('should return the initial state', function () {
    expect(shortcutSlice.reducer(undefined, {})).toEqual({
      latestGeneration: 0,
      operations: [],
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
