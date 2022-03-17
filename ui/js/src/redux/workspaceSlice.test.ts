import '../__mocks__/matchMediaMock';
import workspaceSlice from './workspaceSlice';

describe('workspace reducer', function () {
  it('should return the initial state', function () {
    expect(workspaceSlice.reducer(undefined, {})).toEqual({
      csrfToken: null,
      filterLabels: [],
      labelTodoId: null,
      loggedIn: false,
      todoEditId: null,
    });
  });

  describe('workspace/filterByLabels', function () {
    it('should update the filterLabels', function () {
      const result = workspaceSlice.reducer(
        {
          filterLabels: ['old'],
        },
        {
          type: 'workspace/filterByLabels',
          payload: ['new', 'otherNew'],
        },
      );
      expect(result).toEqual({
        filterLabels: ['new', 'otherNew'],
      });
    });
  });

  describe('workspace/setTodoLabelingId', function () {
    it('should update the labeling id', function () {
      const result = workspaceSlice.reducer(
        {
          labelTodoId: 1,
        },
        {
          type: 'workspace/setTodoLabelingId',
          payload: 2,
        },
      );
      expect(result).toEqual({
        labelTodoId: 2,
      });
    });

    it('should support cancelling a labeling', function () {
      const result = workspaceSlice.reducer(
        {
          labelTodoId: 1,
        },
        {
          type: 'workspace/setTodoLabelingId',
          payload: null,
        },
      );
      expect(result).toEqual({
        labelTodoId: null,
      });
    });
  });

  describe('workspace/setTodoEditId', function () {
    it('should update the edit id', function () {
      const result = workspaceSlice.reducer(
        {
          todoEditId: 1,
        },
        {
          type: 'workspace/setTodoEditId',
          payload: 2,
        },
      );
      expect(result).toEqual({
        todoEditId: 2,
      });
    });

    it('should support cancelling an edit', function () {
      const result = workspaceSlice.reducer(
        {
          todoEditId: 1,
        },
        {
          type: 'workspace/setTodoEditId',
          payload: null,
        },
      );
      expect(result).toEqual({
        todoEditId: null,
      });
    });
  });
});

export {};
