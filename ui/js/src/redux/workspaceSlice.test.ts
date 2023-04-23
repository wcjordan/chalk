import '../__mocks__/matchMediaMock';
import { FILTER_STATUS } from './types';
import workspaceSlice from './workspaceSlice';

describe('workspace reducer', function () {
  it('should return the initial state', function () {
    expect(workspaceSlice.reducer(undefined, {})).toEqual({
      csrfToken: null,
      editTodoId: null,
      filterLabels: {
        Unlabeled: FILTER_STATUS.Active,
      },
      labelTodoId: null,
      loggedIn: false,
    });
  });

  describe('workspace/filterByLabels', function () {
    it('should update the filterLabels', function () {
      const result = workspaceSlice.reducer(
        {
          filterLabels: {
            old: FILTER_STATUS.Active,
          },
        },
        {
          type: 'workspace/filterByLabels',
          payload: {
            new: FILTER_STATUS.Inverted,
            otherNew: FILTER_STATUS.Active,
          },
        },
      );
      expect(result).toEqual({
        filterLabels: {
          new: FILTER_STATUS.Inverted,
          otherNew: FILTER_STATUS.Active,
        },
      });
    });
  });

  describe('workspace/setLabelTodoId', function () {
    it('should update the labeling id', function () {
      const result = workspaceSlice.reducer(
        {
          labelTodoId: 1,
        },
        {
          type: 'workspace/setLabelTodoId',
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
          type: 'workspace/setLabelTodoId',
          payload: null,
        },
      );
      expect(result).toEqual({
        labelTodoId: null,
      });
    });
  });

  describe('workspace/setEditTodoId', function () {
    it('should update the edit id', function () {
      const result = workspaceSlice.reducer(
        {
          editTodoId: 1,
        },
        {
          type: 'workspace/setEditTodoId',
          payload: 2,
        },
      );
      expect(result).toEqual({
        editTodoId: 2,
      });
    });

    it('should support cancelling an edit', function () {
      const result = workspaceSlice.reducer(
        {
          editTodoId: 1,
        },
        {
          type: 'workspace/setEditTodoId',
          payload: null,
        },
      );
      expect(result).toEqual({
        editTodoId: null,
      });
    });
  });

  describe('workspace/setWorkContext', function () {
    it('should update filter labels to match the work context', function () {
      const result = workspaceSlice.reducer(
        {
          filterLabels: {
            Chalk: FILTER_STATUS.Active,
          },
        },
        {
          type: 'workspace/setWorkContext',
          payload: 'inbox',
        },
      );
      expect(result).toEqual({
        filterLabels: {
          Unlabeled: FILTER_STATUS.Active,
        },
      });
    });

    it('should ignore invalid work contexts', function () {
      const result = workspaceSlice.reducer(
        {
          filterLabels: {
            Chalk: FILTER_STATUS.Active,
          },
        },
        {
          type: 'workspace/setWorkContext',
          payload: 'I made this up',
        },
      );
      expect(result).toEqual({
        filterLabels: {
          Chalk: FILTER_STATUS.Active,
        },
      });
    });
  });
});

export {};
