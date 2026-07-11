import '../__mocks__/matchMediaMock';
import { FILTER_STATUS } from './types';
import { workContexts, workspaceSlice } from './workspaceSlice';

describe('workspace reducer', function () {
  it('should return the initial state', function () {
    expect(workspaceSlice.reducer(undefined, {})).toEqual({
      csrfToken: null,
      editTodoId: null,
      filterLabels: {
        Unlabeled: FILTER_STATUS.Active,
        snoozed: FILTER_STATUS.Inverted,
      },
      labelTodoId: null,
      loggedIn: false,
      showCompletedTodos: false,
      showLabelFilter: false,
      snoozeTodoId: null,
    });
  });

  describe('workspace/toggleLabel', function () {
    it('should toggle a new label to active', function () {
      const result = workspaceSlice.reducer(
        {
          filterLabels: {
            other: FILTER_STATUS.Active,
          },
        },
        {
          type: 'workspace/toggleLabel',
          payload: 'new',
        },
      );
      expect(result).toEqual({
        filterLabels: {
          new: FILTER_STATUS.Active,
          other: FILTER_STATUS.Active,
        },
      });
    });

    it('should toggle an active label to inverted', function () {
      const result = workspaceSlice.reducer(
        {
          filterLabels: {
            activeLabel: FILTER_STATUS.Active,
            other: FILTER_STATUS.Active,
          },
        },
        {
          type: 'workspace/toggleLabel',
          payload: 'activeLabel',
        },
      );
      expect(result).toEqual({
        filterLabels: {
          activeLabel: FILTER_STATUS.Inverted,
          other: FILTER_STATUS.Active,
        },
      });
    });

    it('should toggle an inverted label to unset', function () {
      const result = workspaceSlice.reducer(
        {
          filterLabels: {
            invertedLabel: FILTER_STATUS.Inverted,
            other: FILTER_STATUS.Active,
          },
        },
        {
          type: 'workspace/toggleLabel',
          payload: 'invertedLabel',
        },
      );
      expect(result).toEqual({
        filterLabels: {
          other: FILTER_STATUS.Active,
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
          snoozed: FILTER_STATUS.Inverted,
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
  describe('workContexts', function () {
    it('should define a virtual Snoozed work context', function () {
      expect(workContexts.snoozed).toEqual({
        displayName: 'Snoozed',
        labels: {
          snoozed: FILTER_STATUS.Active,
        },
      });
    });

    it('should invert both backlog and snoozed by default for non-Inbox contexts', function () {
      expect(workContexts.urgent).toEqual({
        displayName: 'Urgent',
        labels: {
          urgent: FILTER_STATUS.Active,
          backlog: FILTER_STATUS.Inverted,
          snoozed: FILTER_STATUS.Inverted,
        },
      });
    });

    it('should keep Inbox backlog-inclusive while still excluding snoozed todos', function () {
      expect(workContexts.inbox).toEqual({
        displayName: 'Inbox',
        labels: {
          Unlabeled: FILTER_STATUS.Active,
          snoozed: FILTER_STATUS.Inverted,
        },
      });
    });
  });

  describe('workspace/setSnoozeTodoId', function () {
    it('should set the snooze todo id', function () {
      const result = workspaceSlice.reducer(
        { snoozeTodoId: null },
        {
          type: 'workspace/setSnoozeTodoId',
          payload: 42,
        },
      );
      expect(result).toEqual({ snoozeTodoId: 42 });
    });

    it('should clear the snooze todo id', function () {
      const result = workspaceSlice.reducer(
        { snoozeTodoId: 42 },
        {
          type: 'workspace/setSnoozeTodoId',
          payload: null,
        },
      );
      expect(result).toEqual({ snoozeTodoId: null });
    });
  });
});

export {};
